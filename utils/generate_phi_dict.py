#!/usr/bin/env python
"""
Create the _phi_dict.py file from Table E.1-1 and Table E.3.10-1 of the
DICOM Standard, PS3.15.

Reformat the docbook XML (from the standard) to Python syntax, same
approach and output shape as generate_dicom_dict.py (adapted from
pydicom's), so this reads the same way to anyone already familiar
with that file.

BasicProfileTags
-----------------
Table E.1-1 rows with a concrete, single-tag notation, written as an int
key (0xggggeeee, matching pydicom's DicomDictionary convention):
    Tag: ("Name", "Retd", "StdCompIOD", "BasicProfile", "RtnSafePriv",
          "RtnUIDs", "RtnDevId", "RtnInstId", "RtnPatChars",
          "RtnLongFullDates", "RtnLongModifDates", "CleanDesc",
          "CleanStructCont", "CleanGraph")

WildcardTags
------------
The 3 wildcard-shaped rows (e.g. "(50xx,xxxx)") that can't be a single
Tag, as string keys (e.g. "50xxxxxx", matching pydicom's
RepeatersDictionary convention), same value shape as BasicProfileTags.

SafePrivateTags
-----------------
Table E.3.10-1 rows, one dict entry per row, same flat shape as the other
two, written to its own file _safe_private_dict.py:
    (Tag, "Private Creator"): ("VR", "VM", "Meaning")

Where Tag uses the same wildcard string convention as WildcardTags.
The key is a (tag, creator) pair rather than tag alone -- 103 of the 318
distinct tag shapes in this table are reused by more than one vendor for
different meanings, tag alone isn't unique.
"""

import argparse
import importlib.util
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import urllib.request as urllib2

NSMAP = {"d": "http://docbook.org/ns/docbook", "xml": "http://www.w3.org/XML/1998/namespace"}

PART15_URL = "https://dicom.nema.org/medical/dicom/current/source/docbook/part15/part15.xml"

_PKG_DIRECTORY = Path(__file__).parent.parent / "src" / "shrub"
PHI_DICT_FILENAME = _PKG_DIRECTORY / "_phi_dict.py"
SAFE_PRIVATE_DICT_FILENAME = _PKG_DIRECTORY / "_safe_private_dict.py"
DICOM_DICT_FILENAME = _PKG_DIRECTORY / "_dicom_dict.py"
SHRUB_VERSION_FILENAME = _PKG_DIRECTORY / "_version.py"

BASIC_PROFILE_KEYS = [
    "name", "tag", "retd", "std_comp_iod", "basic_profile", "rtn_safe_priv",
    "rtn_uids", "rtn_dev_id", "rtn_inst_id", "rtn_pat_chars",
    "rtn_long_full_dates", "rtn_long_modif_dates", "clean_desc",
    "clean_struct_cont", "clean_graph",
]
SAFE_PRIVATE_KEYS = ["tag", "private_creator", "vr", "vm", "meaning"]

# columns written into each BasicProfileTags/WildcardProfileTags tuple,
# in order, tag itself becomes the dict key so it's excluded here
VALUE_COLUMNS = [
    "name", "retd", "std_comp_iod", "basic_profile", "rtn_safe_priv",
    "rtn_uids", "rtn_dev_id", "rtn_inst_id", "rtn_pat_chars",
    "rtn_long_full_dates", "rtn_long_modif_dates", "clean_desc",
    "clean_struct_cont", "clean_graph",
]


def _fetch_xml(source: str) -> ET.Element:
    # stdlib only, matching generate_dicom_dict.py -- Python's expat-based
    # parser does not resolve external entities by default (verified: an
    # undefined-entity XXE payload raises ParseError, not silent expansion),
    # so no extra hardening needed here the way lxml required explicit flags
    if source.startswith("http://") or source.startswith("https://"):
        handle = urllib2.urlopen(source)
    else:
        handle = open(source, "rb")
    tree = ET.parse(handle)
    return tree.getroot()


def load_module(path: Path, name: str):
    """Load a module by file path. This script runs standalone from utils/,
    where `src.shrub` isn't importable."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_edition(root: ET.Element) -> str:
    """"DICOM PS3.15 2026d - Security and ..." -> "2026d", same subtitle
    parse as generate_dicom_dict.py."""
    return root.find("d:subtitle", NSMAP).text.split()[2]


def _cell_text(entry: ET.Element) -> str:
    text = "".join(entry.itertext())
    text = text.replace("\u200b", "")
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _find_table(root: ET.Element, table_id: str, caption_substring: str) -> ET.Element:
    matches = root.findall(f".//d:table[@xml:id='{table_id}']", NSMAP)
    if matches:
        return matches[0]
    for table in root.findall(".//d:table", NSMAP):
        caption = table.find("d:caption", NSMAP)
        if caption is not None and caption_substring.lower() in _cell_text(caption).lower():
            return table
    raise LookupError(f"no table found by id '{table_id}' or caption '{caption_substring}'")


def _extract_rows(table: ET.Element, column_keys: list[str]) -> list[dict]:
    rows = []
    for row in table.findall("d:tbody/d:tr", NSMAP):
        cells = [_cell_text(td) for td in row.findall("d:td", NSMAP)]
        if len(cells) != len(column_keys):
            raise ValueError(f"row has {len(cells)} cells, expected {len(column_keys)}: {cells!r}")
        rows.append(dict(zip(column_keys, cells)))
    return rows


def parse_tag_key(tag_str: str) -> int | None:
    """"(0008,0050)" -> 0x00080050. Returns None for wildcard-shaped tags
    and the blanket private-attributes rule row, neither of which is a
    single concrete tag."""
    if "gggg" in tag_str:
        return None
    group, element = tag_str.strip("()").split(",")
    if "x" in group.lower() or "x" in element.lower():
        return None
    return int(group + element, 16)


def wildcard_key(tag_str: str) -> str:
    """"(50xx,xxxx)" -> "50xxxxxx", matching pydicom's RepeatersDictionary
    string-key convention (group+element concatenated, no punctuation)."""
    group, element = tag_str.strip("()").split(",")
    return group + element


def to_double_quoted(value: str) -> str:
    """Wrap a value as a double-quoted Python string literal, escaping
    anything that would otherwise break it -- some Table E.3.10-1 "Meaning"
    fields contain literal double quotes in their text (e.g. describing a
    format string like n.nnn:1"), a naive f'"{value}"' breaks on those."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_dict(fp, dict_name: str, rows: list[dict], key_expr_fn) -> None:
    fp.write(f"\n{dict_name} = {{\n    ")
    lines = []
    for row in rows:
        key = key_expr_fn(row)
        values = ", ".join(to_double_quoted(row[col]) for col in VALUE_COLUMNS)
        lines.append(f"{key}: ({values})")
    fp.write(",\n    ".join(lines))
    fp.write(",\n}\n")


def write_safe_private_dict(fp, rows: list[dict], edition: str) -> None:
    fp.write(
        '"""Safe private tags auto-generated by generate_phi_dict.py\n\n'
        f"DICOM Standard edition: {edition} (PS3.15 Table E.3.10-1)\n"
        '"""\n'
    )
    fp.write(
        "\n# Each entry is (Tag, Private Creator): (VR, VM, Meaning). Tag uses\n"
        "# the same wildcard string convention as WildcardTags in\n"
        "# _phi_dict.py, e.g. \"7053xx00\". Tag alone is not unique -- match\n"
        "# on the full (tag, creator) pair, not tag alone.\n"
    )
    fp.write("SafePrivateTags = {\n    ")
    lines = []
    for row in rows:
        key = f'("{wildcard_key(row["tag"])}", {to_double_quoted(row["private_creator"])})'
        values = ", ".join(to_double_quoted(row[col]) for col in ("vr", "vm", "meaning"))
        lines.append(f"{key}: ({values})")
    fp.write(",\n    ".join(lines))
    fp.write(",\n}\n")


def check_against_dicom_dict(phi_dict_path: Path, dicom_dict_path: Path) -> None:
    """Every tag in BasicProfileTags should also exist in _dicom_dict.py,
    since Table E.1-1 only ever lists real, registered DICOM attributes.
    A PHI tag missing from the Data Dictionary points at an extraction
    bug on one side or the other, not a real gap -- print each miss so it
    gets a human's attention, but don't fail the whole run over it.

    WildcardTags isn't checked here -- Part 15 and Part 6 wildcard
    some of these to different precision (e.g. Curve Data is
    "(50xx,xxxx)" in Table E.1-1 but registered as the more specific
    "(50xx,3000)" in Part 6's Data Dictionary), so a literal string match
    isn't meaningful for these. There are only 3 of them, long-retired
    legacy attributes already verified by hand, not worth the complexity
    of real pattern-containment matching for."""
    if not dicom_dict_path.exists():
        print(f"skipping cross-check: no {dicom_dict_path} found, run generate_dicom_dict.py first")
        return

    phi =load_module(phi_dict_path, "_phi_dict_check")
    dicom = load_module(dicom_dict_path, "_dicom_dict_check")

    missing = [f"0x{k:08X}" for k in phi.BasicProfileTags if k not in dicom.DicomDictionary]

    if not missing:
        print(f"cross-check OK: all {len(phi.BasicProfileTags)} PHI tags found in {dicom_dict_path.name}")
        return

    print(f"cross-check FAILED: {len(missing)} PHI tag(s) not in {dicom_dict_path.name}")
    for tag in missing:
        print(f"  missing: {tag}")


def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Generate a new _phi_dict.py file from Part 15 of the DICOM Standard",
        usage="generate_phi_dict.py [options]",
    )
    opts = parser.add_argument_group("Options")
    opts.add_argument(
        "--local",
        help="Path to a local part15.xml (used instead of downloading it)",
        type=str,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = setup_argparse()
    source = args.local if args.local else PART15_URL

    print(f"Reading '{source}'")
    root = _fetch_xml(source)

    edition = read_edition(root)
    lib_version = load_module(SHRUB_VERSION_FILENAME, "_shrub_version").__dicom_version__
    if lib_version != edition:
        print(
            "Warning: '__dicom_version__' in src/shrub/_version.py is "
            f"'{lib_version}', needs to be updated to '{edition}'"
        )

    basic_profile_tags = _extract_rows(
        _find_table(root, "table_E.1-1", "Application Level Confidentiality Profile Attributes"),
        BASIC_PROFILE_KEYS,
    )
    # blanket private-attributes rule row, not a real tag, handled separately
    basic_profile_tags = [row for row in basic_profile_tags if "gggg" not in row["tag"]]

    if len(basic_profile_tags) < 600:
        raise ValueError(f"table E.1-1 only had {len(basic_profile_tags)} rows, expected 600+")

    safe_private_tags = _extract_rows(
        _find_table(root, "table_E.3.10-1", "Safe Private Attributes"),
        SAFE_PRIVATE_KEYS,
    )

    main_rows = [r for r in basic_profile_tags if parse_tag_key(r["tag"]) is not None]
    wildcard_rows = [r for r in basic_profile_tags if parse_tag_key(r["tag"]) is None]

    with open(PHI_DICT_FILENAME, "w") as f:
        f.write(
            '"""PHI tags auto-generated by generate_phi_dict.py\n\n'
            f"DICOM Standard edition: {edition} (PS3.15 Table E.1-1)\n"
            '"""\n'
        )
        f.write(
            "\n# Each dict entry is Tag: (Name, Retd, StdCompIOD, BasicProfile,\n"
            "#   RtnSafePriv, RtnUIDs, RtnDevId, RtnInstId, RtnPatChars,\n"
            "#   RtnLongFullDates, RtnLongModifDates, CleanDesc, CleanStructCont, CleanGraph)"
        )
        write_dict(f, "BasicProfileTags", main_rows, lambda r: f'0x{parse_tag_key(r["tag"]):08X}')
        write_dict(f, "WildcardTags", wildcard_rows, lambda r: f'"{wildcard_key(r["tag"])}"')

    with open(SAFE_PRIVATE_DICT_FILENAME, "w") as f:
        write_safe_private_dict(f, safe_private_tags, edition)

    print(
        f"Processing complete: {len(main_rows)} tags, {len(wildcard_rows)} wildcard tags -> {PHI_DICT_FILENAME}\n"
        f"{len(safe_private_tags)} safe private tags -> {SAFE_PRIVATE_DICT_FILENAME}"
    )

    check_against_dicom_dict(PHI_DICT_FILENAME, DICOM_DICT_FILENAME)