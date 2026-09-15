"""
loads Table E.1-1 and Table E.3.10-1 from a local snapshot. startup
never hits the network. run refresh_dicom_tables() separately (cron job,
manual command) to pull the latest from NEMA and update the snapshot.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

import requests
from lxml import etree

log = logging.getLogger(__name__)

PART15_URL = "https://dicom.nema.org/medical/dicom/current/source/docbook/part15/part15.xml"
PART06_URL = "https://dicom.nema.org/medical/dicom/current/source/docbook/part06/part06.xml"

DOCBOOK_NS = "http://docbook.org/ns/docbook"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NSMAP = {"d": DOCBOOK_NS, "xml": XML_NS}

REQUEST_TIMEOUT_SECONDS = 60

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
SNAPSHOT_PATH = SNAPSHOT_DIR / "current.json"

BASIC_PROFILE_KEYS = [
    "name", "tag", "retd", "std_comp_iod", "basic_profile", "rtn_safe_priv",
    "rtn_uids", "rtn_dev_id", "rtn_inst_id", "rtn_pat_chars",
    "rtn_long_full_dates", "rtn_long_modif_dates", "clean_desc",
    "clean_struct_cont", "clean_graph",
]
SAFE_PRIVATE_KEYS = ["tag", "private_creator", "vr", "vm", "meaning"]


@dataclass
class DicomTables:
    edition: str
    pulled_date: str
    basic_profile_tags: list[dict]
    safe_private_tags: list[dict]

    def save(self, path: Path = SNAPSHOT_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False))

    @staticmethod
    def load(path: Path = SNAPSHOT_PATH) -> "DicomTables":
        return DicomTables(**json.loads(path.read_text()))


def _fetch_xml(url: str) -> etree._Element:
    resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    # no entity resolution, no network, harden against xxe since this
    # fetches from a third party on a schedule
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    return etree.fromstring(resp.content, parser=parser)


def _cell_text(entry: etree._Element) -> str:
    # flatten a table cell to plain text, including anything nested inside
    # footnote/xref/para tags
    text = "".join(entry.itertext())
    text = text.replace("\u200b", "")  # zero-width space, present in ~24 rows (GPS fields) in the actual source
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_edition(root: etree._Element) -> str:
    subtitle = root.find("d:subtitle", NSMAP)
    return _cell_text(subtitle) if subtitle is not None else "unknown"


def _find_table(root: etree._Element, table_id: str, caption_substring: str) -> etree._Element:
    # look up by xml:id first, it's stable across editions
    matches = root.xpath(f".//d:table[@xml:id='{table_id}']", namespaces=NSMAP)
    if matches:
        return matches[0]

    # id moved or got renamed, fall back to caption text and warn so we
    # notice and fix the hardcoded id above
    log.warning(
        "table id '%s' not found, falling back to caption search for '%s'",
        table_id, caption_substring,
    )
    for table in root.xpath(".//d:table", namespaces=NSMAP):
        caption = table.find("d:caption", NSMAP)
        if caption is not None and caption_substring.lower() in _cell_text(caption).lower():
            return table

    raise LookupError(
        f"no table found by id '{table_id}' or caption '{caption_substring}', "
        f"doc structure may have changed"
    )


def _extract_rows(table: etree._Element, column_keys: list[str]) -> list[dict]:
    rows = []
    for row in table.xpath("d:tbody/d:tr", namespaces=NSMAP):
        cells = [_cell_text(td) for td in row.xpath("d:td", namespaces=NSMAP)]
        if len(cells) != len(column_keys):
            raise ValueError(f"row has {len(cells)} cells, expected {len(column_keys)}: {cells!r}")
        rows.append(dict(zip(column_keys, cells)))
    return rows


# Part 6 (Data Dictionary) splits its Tag -> VR registry across 4 tables,
# by which group of the DICOM standard the tags belong to. table_6-1 is
# the main one (5263 entries); the other 3 cover File Meta, Directory
# Structuring, and Dynamic RTP Payload elements. Command elements
# (group 0000) live in Part 7 instead, not pulled here, only 2 of the
# 655 basic_profile_tags rows need it, not worth a whole extra fetch.
VR_LOOKUP_TABLE_IDS = ["table_6-1", "table_7-1", "table_8-1", "table_9-1"]


def _extract_vr_lookup(part06_root: etree._Element) -> dict[str, str]:
    tag_to_vr = {}
    for table_id in VR_LOOKUP_TABLE_IDS:
        matches = part06_root.xpath(f".//d:table[@xml:id='{table_id}']", namespaces=NSMAP)
        if not matches:
            log.warning("VR lookup table id '%s' not found, skipping", table_id)
            continue
        for row in matches[0].xpath(".//d:tbody/d:tr", namespaces=NSMAP):
            cells = [_cell_text(td) for td in row.xpath("d:td", namespaces=NSMAP)]
            if len(cells) >= 4 and cells[0] and cells[3]:
                tag_to_vr[cells[0]] = cells[3]
    return tag_to_vr


def _add_vr(basic_profile_tags: list[dict], tag_to_vr: dict[str, str]) -> None:
    # in place -- adds a 'vr' key to every row that has a Part 6 match.
    # rows with no match (wildcard-shaped tags, the 2 Command-group tags)
    # get vr=None rather than a missing key, so callers can rely on the
    # key always being present
    for row in basic_profile_tags:
        row["vr"] = tag_to_vr.get(row["tag"])


def _diff_and_log(old_rows: list[dict], new_rows: list[dict], key_field: str, label: str) -> None:
    # warning not info, an action code changing silently between
    # editions needs a human to actually see it
    old_by_key = {r[key_field]: r for r in old_rows}
    new_by_key = {r[key_field]: r for r in new_rows}

    added = new_by_key.keys() - old_by_key.keys()
    removed = old_by_key.keys() - new_by_key.keys()
    if added:
        log.warning("%s: %d new attribute(s) added: %s", label, len(added), sorted(added))
    if removed:
        log.warning("%s: %d attribute(s) removed: %s", label, len(removed), sorted(removed))

    for key in old_by_key.keys() & new_by_key.keys():
        old_row, new_row = old_by_key[key], new_by_key[key]
        for field in old_row.keys() & new_row.keys():
            if old_row[field] != new_row[field]:
                log.warning("%s: %s.%s changed: %r -> %r", label, key, field, old_row[field], new_row[field])


def load_dicom_tables(snapshot_path: Path = SNAPSHOT_PATH) -> DicomTables:
    """reads the local snapshot only, never touches the network. call this at startup."""
    if not snapshot_path.exists():
        raise RuntimeError(
            f"no snapshot at {snapshot_path}, run refresh_dicom_tables() once "
            f"and commit the snapshot so this doesn't need network at boot"
        )
    return DicomTables.load(snapshot_path)


def refresh_dicom_tables(
    part15_url: str = PART15_URL,
    part06_url: str = PART06_URL,
    snapshot_path: Path = SNAPSHOT_PATH,
) -> DicomTables:
    """fetches from NEMA and overwrites the snapshot. run from a cron job or
    manual command, not from app startup."""
    try:
        part15_root = _fetch_xml(part15_url)

        basic_profile_tags = _extract_rows(
            _find_table(part15_root, "table_E.1-1", "Application Level Confidentiality Profile Attributes"),
            BASIC_PROFILE_KEYS,
        )

        # filter out the private attributes row, nothing burger
        basic_profile_tags = [row for row in basic_profile_tags if "gggg" not in row["tag"]]

        # sanity check, a broken extraction returns few/no rows instead
        # of erroring, this catches it
        if len(basic_profile_tags) < 600:
            raise ValueError(f"table E.1-1 only had {len(basic_profile_tags)} rows, expected 600+")

        safe_private_tags = _extract_rows(
            _find_table(part15_root, "table_E.3.10-1", "Safe Private Attributes"),
            SAFE_PRIVATE_KEYS,
        )

        # E.1-1 doesn't carry VR at all, cross-reference against Part 6's
        # Data Dictionary to add it. safe_private_tags already has its own
        # 'vr' column straight from Table E.3.10-1, doesn't need this.
        part06_root = _fetch_xml(part06_url)
        tag_to_vr = _extract_vr_lookup(part06_root)
        _add_vr(basic_profile_tags, tag_to_vr)

        tables = DicomTables(
            edition=_extract_edition(part15_root), pulled_date=date.today().isoformat(),
            basic_profile_tags=basic_profile_tags, safe_private_tags=safe_private_tags,
        )

        # log what changed vs last snapshot before overwriting it
        if snapshot_path.exists():
            previous = DicomTables.load(snapshot_path)
            _diff_and_log(previous.basic_profile_tags, tables.basic_profile_tags, "tag", "Table E.1-1")
            _diff_and_log(previous.safe_private_tags, tables.safe_private_tags, "tag", "Table E.3.10-1")

        tables.save(snapshot_path)
        return tables

    except Exception:
        # fetch failed for whatever reason, don't nuke the last good
        # snapshot, just return it
        log.exception("refresh failed, leaving previous snapshot in place")
        if snapshot_path.exists():
            return DicomTables.load(snapshot_path)
        raise RuntimeError("refresh failed and no snapshot exists yet, retry with network access")