#!/usr/bin/env python
"""
Generate the basic_profile canary fixture from the DICOM Standard.

Writes two files to tests/fixtures/:

basic_profile.json
    A DICOM JSON dataset (PS3.18 Annex F) holding every tag in
    BasicProfileTags plus one instance of each WildcardTags entry. Every
    value is realistic and dummy, drawn from utils/canary_pools.py with a
    fixed seed, so the file is identical on every run.

basic_profile.canaries.json
    The recorded canary list. Each entry is a value the standard calls PHI,
    its VR, and every path where the generator planted it. A test can look
    each canary up by path before de-identification, and search for it
    after.

Sequences
---------
Each Basic Profile SQ gets one item with one child. The child is a real
child of that sequence in PS3.3 (Information Object Definitions). The
generator reads the PS3.3 module tables, where ">" marks nesting, and
resolves "Include Table ..." rows recursively with a cycle guard.

  1. If a child is a Basic Profile tag, pick one. Its value is a canary.
  2. Otherwise pick any real child. It gets a realistic value, but it is
     not a canary, because shrub may legally keep it under a D parent.
  3. If PS3.3 gives no usable child, the item stays empty and the script
     prints a warning.

Values
------
Every canary is unique, and every value is checked against its VR's PS3.5
format and length rules. The script raises on a duplicate or a format
violation. Enumerated tags such as GPSLatitudeRef ("N" or "S") cannot be
both realistic and unique, so they get a fixed real value from
ENUMERATED_VALUES and are not canaries.

Run order: generate_dicom_dict.py, then generate_phi_dict.py, then this
script. It reads both generated dicts.
"""

import argparse
import base64
import datetime
import importlib.util
import json
import random
import re
import struct
import sys
import urllib.request as urllib2
import xml.etree.ElementTree as ET
from pathlib import Path

PART03_URL = "https://dicom.nema.org/medical/dicom/current/source/docbook/part03/part03.xml"

NS = "http://docbook.org/ns/docbook"
NSMAP = {"d": NS, "xml": "http://www.w3.org/XML/1998/namespace"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

_REPO = Path(__file__).parent.parent
_PKG_DIRECTORY = _REPO / "src" / "shrub"
PHI_DICT_FILENAME = _PKG_DIRECTORY / "_phi_dict.py"
DICOM_DICT_FILENAME = _PKG_DIRECTORY / "_dicom_dict.py"
SHRUB_VERSION_FILENAME = _PKG_DIRECTORY / "_version.py"
POOLS_FILENAME = Path(__file__).parent / "canary_pools.py"
FIXTURE_DIR = _REPO / "tests" / "fixtures"
FIXTURE_FILENAME = FIXTURE_DIR / "basic_profile.json"
CANARIES_FILENAME = FIXTURE_DIR / "basic_profile.canaries.json"

# Changing the seed changes every value in the fixture.
SEED = 20261119

# tests/fixture_io.py copies SOPInstanceUID into the file meta as
# MediaStorageSOPInstanceUID, the way real files do. The canary list
# records that second path so a leak through the file meta is caught.
SOP_INSTANCE_UID = 0x00080018
MEDIA_STORAGE_SOP_INSTANCE_UID_PATH = "(0002,0003)"

# Basic Profile tags in these groups cannot go in a file's main dataset,
# so the fixture leaves them out. tests/test_fixtures.py lists the same
# exclusion.
NOT_IN_DATASET_GROUPS = {
    0x0000: "is a command group element that exists only in network messages, left out",
    0x0002: "is file meta, written by tests/fixture_io.py from SOPInstanceUID, left out",
}

# One concrete instance per WildcardTags key, in a non-base group (6002,
# not 6000) so a matcher hard-coded to the base group fails. The VR comes
# from RepeatersDictionary. "OB or OW" entries take the VR given here.
WILDCARD_INSTANCES = {
    "60xx3000": (0x60023000, "60xx3000", "OW"),
    "60xx4000": (0x60024000, "60xx4000", None),
    "50xxxxxx": (0x50023000, "50xx3000", "OB"),
}

# Tags whose values come from a short enumerated list in the standard.
# These get a fixed realistic value and are not canaries.
ENUMERATED_VALUES = {
    "PatientSex": "F",
    "PatientSexNeutered": "UNALTERED",
    "SmokingStatus": "YES",
    "GPSLatitudeRef": "N",
    "GPSLongitudeRef": "W",
    "GPSStatus": "A",
    "GPSMeasureMode": "3",
    "GPSSpeedRef": "K",
    "GPSTrackRef": "T",
    "GPSImgDirectionRef": "M",
    "GPSDestLatitudeRef": "N",
    "GPSDestLongitudeRef": "W",
    "GPSDestBearingRef": "T",
    "GPSDestDistanceRef": "K",
    "ReasonForTheAttributeModification": "CORRECT",
    "InstanceOriginStatus": "LOCAL",
    "PregnancyStatus": 4,
    "GPSAltitudeRef": 0,
    "GPSDifferential": 0,
    "GPSVersionID": bytes([2, 3, 0, 0]),
}

BINARY_VRS = {"OB", "OD", "OF", "OL", "OV", "OW", "UN"}
TEXT_MAX_LENGTH = {
    "AE": 16, "CS": 16, "SH": 16, "LO": 64, "ST": 1024, "LT": 10240,
    "UC": None, "UT": None, "UR": None,
}
SUPPORTED_VRS = (
    set(TEXT_MAX_LENGTH) | BINARY_VRS
    | {"AS", "AT", "DA", "DS", "DT", "FD", "FL", "IS", "PN", "SL", "SS",
       "SV", "TM", "UI", "UL", "US", "UV"}
)
INT_RANGES = {
    "US": (0, 2**16 - 1), "SS": (-(2**15), 2**15 - 1),
    "UL": (0, 2**32 - 1), "SL": (-(2**31), 2**31 - 1),
    "UV": (0, 2**64 - 1), "SV": (-(2**63), 2**63 - 1),
    "IS": (-(2**31), 2**31 - 1),
}


########################
# shared generator setup
########################

def _fetch_xml(source: str) -> ET.Element:
    if source.startswith("http://") or source.startswith("https://"):
        handle = urllib2.urlopen(source)
    else:
        handle = open(source, "rb")
    return ET.parse(handle).getroot()


def load_module(path: Path, name: str):
    """Load a module by file path. This script runs standalone from utils/,
    where `src.shrub` isn't importable."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_edition(root: ET.Element) -> str:
    """"DICOM PS3.3 2026d - Information Object Definitions" -> "2026d"."""
    return root.find("d:subtitle", NSMAP).text.split()[2]


def _cell_text(cell: ET.Element) -> str:
    text = "".join(cell.itertext()).replace("​", "")
    return re.sub(r"\s+", " ", text).strip()


def format_tag(tag: int) -> str:
    return f"({tag >> 16:04X},{tag & 0xFFFF:04X})"


################
# PS3.3 parsing
################

TAG_RE = re.compile(r"\(([0-9A-Fa-f]{4}),([0-9A-Fa-f]{4})\)")


def index_tables(root: ET.Element) -> dict[str, list[tuple]]:
    """Index every PS3.3 table by its xml:id.

    Each row becomes (depth, tag, include_id). depth is the number of
    leading ">" in the first cell. An attribute row has a tag and no
    include_id. An "Include Table ..." row has no tag and the xml:id of the
    table it includes. Rows with neither (headings, wildcard tags) are
    dropped.
    """
    tables = {}
    for table in root.iter(f"{{{NS}}}table"):
        table_id = table.get(XML_ID)
        if table_id is None:
            continue
        rows = []
        for tr in table.iter(f"{{{NS}}}tr"):
            cells = tr.findall("d:td", NSMAP)
            if not cells:
                continue
            first = _cell_text(cells[0])
            name = first.lstrip(">")
            depth = len(first) - len(name)
            if name.startswith("Include"):
                for xref in cells[0].iter(f"{{{NS}}}xref"):
                    linkend = xref.get("linkend", "")
                    if linkend.startswith("table_"):
                        rows.append((depth, None, linkend))
                continue
            if len(cells) < 2:
                continue
            match = TAG_RE.search(_cell_text(cells[1]))
            if match:
                rows.append((depth, int(match.group(1) + match.group(2), 16), None))
        tables[table_id] = rows
    return tables


def expand_table(tables: dict, table_id: str, _stack: frozenset = frozenset()) -> list[tuple[int, int]]:
    """Flatten one table into (depth, tag) rows with every Include resolved.

    An Include row at depth d splices in the included table's rows, with
    each of their depths shifted by d. Included tables can include others,
    so this recurses. _stack holds the tables currently being expanded. A
    table that includes itself, directly or through others, is skipped the
    second time instead of recursing forever.
    """
    if table_id in _stack or table_id not in tables:
        return []
    stack = _stack | {table_id}
    flat = []
    for depth, tag, include_id in tables[table_id]:
        if tag is not None:
            flat.append((depth, tag))
            continue
        for inner_depth, inner_tag in expand_table(tables, include_id, stack):
            flat.append((depth + inner_depth, inner_tag))
    return flat


def sequence_children(tables: dict, sequences: set[int]) -> dict[int, set[int]]:
    """For each tag in `sequences`, the tags PS3.3 places directly inside
    its items, combined across every table the sequence appears in.

    The direct children of a sequence at depth d are the rows that follow
    it at depth d + 1, up to the next row at depth d or less.
    """
    children = {}
    for table_id in tables:
        flat = expand_table(tables, table_id)
        for i, (depth, tag) in enumerate(flat):
            if tag not in sequences:
                continue
            found = children.setdefault(tag, set())
            for child_depth, child_tag in flat[i + 1:]:
                if child_depth <= depth:
                    break
                if child_depth == depth + 1:
                    found.add(child_tag)
    return children


################
# canary values
################

def value_count(vm: str) -> int:
    """How many values to write for a VM. A fixed VM ("3") needs exactly
    that many. A range ("1-n", "2-2n") takes its minimum."""
    match = re.match(r"\d+", vm)
    return int(match.group()) if match else 1


class ValueFactory:
    """Draws realistic values with a fixed seed. Every value it hands out
    is unique. A draw that repeats an earlier value is drawn again, and a
    category that keeps repeating raises instead of writing a duplicate."""

    MAX_TRIES = 500

    def __init__(self, seed: int, pools):
        self.rng = random.Random(seed)
        self.pools = pools
        self.used = set()

    def unique(self, label: str, make) -> object:
        for _ in range(self.MAX_TRIES):
            value = make()
            key = repr(value)
            if key not in self.used:
                self.used.add(key)
                return value
        raise ValueError(
            f"ran out of unique values for {label}. Grow its pool in {POOLS_FILENAME.name}."
        )

    # building blocks
    def person(self) -> str:
        p, r = self.pools, self.rng
        return f"{r.choice(p.SURNAMES)}^{r.choice(p.GIVEN_NAMES)}^{r.choice(p.MIDDLE_NAMES)}"

    def identifier(self, max_length: int) -> str:
        prefix = self.rng.choice(["MRN", "ACC", "ORD", "EID", "RQ", "SN", "PID"])
        digits = max(4, min(9, max_length - len(prefix)))
        return f"{prefix}{self.rng.randint(10 ** (digits - 1), 10 ** digits - 1)}"

    def address(self) -> str:
        p, r = self.pools, self.rng
        return (
            f"{r.randint(12, 9899)} {r.choice(p.STREETS)}, {r.choice(p.TOWNS)} "
            f"{r.choice(p.REGIONS)} {r.randint(10000, 99999)}"
        )

    def phone(self) -> str:
        return f"{self.rng.choice([775, 541, 802, 207, 406, 701])}-555-01{self.rng.randint(0, 99):02d}"

    def station(self) -> str:
        r = self.rng
        return f"{r.choice(self.pools.SITE_CODES)}_{r.choice(['CT', 'MR', 'US', 'DX', 'NM', 'PT'])}{r.randint(1, 9):02d}"

    def note(self) -> str:
        p, r = self.pools, self.rng
        first, second = r.sample(p.CLINICAL_PHRASES, 2)
        return f"{first}. {second}. SEEN BY DR {r.choice(p.SURNAMES)}."

    def date(self) -> datetime.date:
        start = datetime.date(1940, 1, 1)
        return start + datetime.timedelta(days=self.rng.randint(0, (datetime.date(2025, 12, 31) - start).days))

    def time(self) -> str:
        r = self.rng
        return f"{r.randint(0, 23):02d}{r.randint(0, 59):02d}{r.randint(0, 59):02d}"

    def text_for(self, vr: str, keyword: str) -> str:
        """A realistic string for a text VR, chosen by what the keyword
        says the attribute holds."""
        p, r = self.pools, self.rng
        max_length = TEXT_MAX_LENGTH.get(vr) or 64
        if vr == "AE":
            return self.station()
        if vr == "CS":
            return f"{r.choice(p.SITE_CODES)}_QC{r.randint(1, 99)}"
        if vr == "UR":
            town = r.choice(p.TOWNS).lower().replace(" ", "")
            return f"https://pacs.{town}.example/viewer?study={r.randint(10**6, 10**8)}"
        if vr in ("ST", "LT", "UT"):
            return self.note()
        if "Telephone" in keyword or "Phone" in keyword:
            return self.phone()
        if "Timezone" in keyword:
            return r.choice(["-0500", "-0600", "-0700", "-0800", "+0100", "+0930"])
        if "Ethnic" in keyword:
            return r.choice(p.ETHNIC_GROUPS)
        if "Occupation" in keyword:
            return r.choice(p.OCCUPATIONS)
        if "Address" in keyword:
            return self.address()
        if "Department" in keyword:
            return f"{r.choice(p.DEPARTMENTS)} {r.choice(p.SITE_CODES)}"
        if any(word in keyword for word in ("Station", "Location", "Machine", "Device")):
            return self.station()
        if keyword.endswith("ID") or any(word in keyword for word in ("Identifier", "Number", "IDs")):
            return self.identifier(min(max_length, 16))
        if vr == "SH":
            return f"{r.choice(p.SHORT_LABELS)} V{r.randint(1, 9)}"
        if any(word in keyword for word in ("Institution", "Organization", "Facility", "Center", "Name")):
            return self.organization()
        return f"{r.choice(p.CLINICAL_PHRASES)} DR {r.choice(p.SURNAMES)}"

    def organization(self) -> str:
        p, r = self.pools, self.rng
        if r.random() < 0.5:
            return r.choice(p.INSTITUTIONS)
        kind = r.choice(["RESEARCH GROUP", "IMAGING CENTER", "TRIAL UNIT", "CLINIC", "LABORATORY"])
        return f"{r.choice(p.TOWNS)} {kind}"

    def one_value(self, vr: str, keyword: str) -> object:
        """One realistic value for a VR, before any uniqueness check."""
        p, r = self.pools, self.rng
        if vr == "PN":
            return self.person()
        if vr == "DA":
            return self.date().strftime("%Y%m%d")
        if vr == "DT":
            return f"{self.date().strftime('%Y%m%d')}{self.time()}.{r.randint(0, 999999):06d}"
        if vr == "TM":
            return f"{self.time()}.{r.randint(0, 999):03d}"
        if vr == "AS":
            return f"{r.randint(18, 95):03d}Y"
        if vr == "UI":
            return f"2.25.{r.getrandbits(128) | 1}"
        if vr == "DS":
            if keyword == "PatientSize":
                return round(r.uniform(1.45, 1.98), 2)
            if keyword == "PatientWeight":
                return round(r.uniform(45.0, 130.0), 1)
            return round(r.uniform(1.0, 999.0), 3)
        if vr in INT_RANGES:
            low, high = INT_RANGES[vr]
            return r.randint(max(low, 1000), min(high, 65535))
        if vr in ("FL", "FD"):
            return round(r.uniform(1.0, 999.0), 3)
        if vr == "AT":
            return r.choice(["00100010", "00100020", "00080090", "00081050"])
        if vr in BINARY_VRS:
            text = f"{r.choice(p.BINARY_TEXTS)} {r.choice(p.GIVEN_NAMES)} {r.choice(p.SURNAMES)}"
            data = text.encode("ascii")
            width = {"OD": 8, "OV": 8, "OF": 4, "OL": 4, "OW": 2}.get(vr, 2)
            return data + b"\x00" * (-len(data) % width)
        if vr in TEXT_MAX_LENGTH:
            return self.text_for(vr, keyword)
        raise ValueError(f"no value rule for VR {vr}")

    def values(self, vr: str, vm: str, keyword: str, label: str) -> list:
        """The value list for one element. Each value is unique across the
        whole fixture."""
        if vr in BINARY_VRS:
            return [self.unique(label, lambda: self.one_value(vr, keyword))]
        return [
            self.unique(label, lambda: self.one_value(vr, keyword))
            for _ in range(value_count(vm))
        ]


#####################
# PS3.5 VR validation
#####################

UID_RE = re.compile(r"^(0|[1-9]\d*)(\.(0|[1-9]\d*))*$")
DS_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")


def validate(vr: str, value: object) -> None:
    """Raise ValueError if one value breaks its VR's PS3.5 Section 6.2 rule."""

    def fail(reason: str):
        raise ValueError(f"{vr} value {value!r} {reason}")

    if vr in BINARY_VRS:
        if not isinstance(value, bytes):
            fail("is not bytes")
        if len(value) % 2:
            fail("has odd length")
        return
    if vr in INT_RANGES:
        low, high = INT_RANGES[vr]
        if not isinstance(value, int) or not low <= value <= high:
            fail(f"is outside {low}..{high}")
        if vr == "IS" and len(str(value)) > 12:
            fail("is longer than 12 characters")
        return
    if vr in ("FL", "FD"):
        if not isinstance(value, float):
            fail("is not a float")
        return
    if vr == "DS":
        text = str(value)
        if len(text) > 16 or not DS_RE.match(text):
            fail("is not a decimal string of at most 16 characters")
        return
    if not isinstance(value, str):
        fail("is not a string")
    if "\\" in value and vr != "UT":
        fail("contains a backslash, the value separator")
    if vr == "PN":
        groups = value.split("=")
        if len(groups) > 3 or any(len(g) > 64 or g.count("^") > 4 for g in groups):
            fail("breaks the PN component rules")
    elif vr == "DA":
        try:
            datetime.datetime.strptime(value, "%Y%m%d")
        except ValueError:
            fail("is not a valid YYYYMMDD date")
    elif vr == "DT":
        if len(value) > 26 or not re.match(r"^\d{14}(\.\d{1,6})?$", value):
            fail("is not YYYYMMDDHHMMSS.FFFFFF")
    elif vr == "TM":
        if len(value) > 14 or not re.match(r"^([01]\d|2[0-3])[0-5]\d[0-5]\d(\.\d{1,6})?$", value):
            fail("is not HHMMSS.FFFFFF")
    elif vr == "AS":
        if not re.match(r"^\d{3}[DWMY]$", value):
            fail("is not nnnD/W/M/Y")
    elif vr == "UI":
        if len(value) > 64 or not UID_RE.match(value):
            fail("is not a valid UID of at most 64 characters")
    elif vr == "AT":
        if not re.match(r"^[0-9A-F]{8}$", value):
            fail("is not 8 hex digits")
    elif vr == "CS":
        if len(value) > 16 or not re.match(r"^[A-Z0-9 _]*$", value):
            fail("is not uppercase CS of at most 16 characters")
    elif vr == "UR":
        if " " in value:
            fail("contains a space")
    else:
        max_length = TEXT_MAX_LENGTH.get(vr)
        if max_length is not None and len(value) > max_length:
            fail(f"is longer than {max_length} characters")


###################
# DICOM JSON output
###################

def element_json(vr: str, values: list) -> dict:
    """One element in DICOM JSON form (PS3.18 Annex F)."""
    if vr == "PN":
        return {"vr": vr, "Value": [{"Alphabetic": v} for v in values]}
    if vr in BINARY_VRS:
        return {"vr": vr, "InlineBinary": base64.b64encode(values[0]).decode("ascii")}
    return {"vr": vr, "Value": values}


def canary_json(vr: str, values: list, paths: list[str]) -> dict:
    if vr in BINARY_VRS:
        return {"vr": vr, "value_base64": base64.b64encode(values[0]).decode("ascii"), "paths": paths}
    return {"vr": vr, "value": values, "paths": paths}


class FixtureBuilder:
    def __init__(self, dicom_dict, repeaters, basic_profile, factory: ValueFactory):
        self.dicom_dict = dicom_dict
        self.repeaters = repeaters
        self.basic_profile = basic_profile
        self.factory = factory
        self.canaries = []

    def vr_of(self, tag: int) -> str:
        """First VR listed in PS3.6. "US or SS" becomes "US"."""
        return self.dicom_dict[tag][0].split(" or ")[0]

    def plant(self, tag: int, vr: str, vm: str, keyword: str, path: str, is_canary: bool) -> dict:
        if keyword in ENUMERATED_VALUES:
            values = [ENUMERATED_VALUES[keyword]]
            is_canary = False
        else:
            values = self.factory.values(vr, vm, keyword, f"{keyword} {format_tag(tag)}")
        for value in values:
            validate(vr, value)
        if is_canary:
            paths = [path]
            if tag == SOP_INSTANCE_UID:
                paths.append(MEDIA_STORAGE_SOP_INSTANCE_UID_PATH)
            self.canaries.append(canary_json(vr, values, paths))
        return element_json(vr, values)

    def plant_tag(self, tag: int, path_prefix: str = "") -> dict:
        vr = self.vr_of(tag)
        _, vm, _, _, keyword = self.dicom_dict[tag]
        is_canary = tag in self.basic_profile
        return self.plant(tag, vr, vm, keyword, path_prefix + format_tag(tag), is_canary)


def choose_child(builder: FixtureBuilder, candidates: set[int]) -> int | None:
    """Rule 1: a Basic Profile child if one exists. Rule 2: any real child.
    Children that are themselves sequences, or that have a VR the factory
    has no rule for, are skipped, since this fixture nests one level."""
    usable = sorted(
        c for c in candidates
        if c in builder.dicom_dict and builder.vr_of(c) in SUPPORTED_VRS
    )
    phi = [c for c in usable if c in builder.basic_profile]
    pool = phi or usable
    return builder.factory.rng.choice(pool) if pool else None


def check_unique(canaries: list[dict]) -> None:
    """Raise if two canaries share a value. ValueFactory already redraws
    repeats, so a failure here means a bug in this script."""
    seen = {}
    for canary in canaries:
        key = json.dumps(canary.get("value", canary.get("value_base64")))
        if key in seen:
            raise ValueError(f"duplicate canary {key} at {seen[key]} and {canary['paths']}")
        seen[key] = canary["paths"]


def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Generate tests/fixtures/basic_profile.json from PS3.3 and the generated dicts",
        usage="generate_fixtures.py [options]",
    )
    opts = parser.add_argument_group("Options")
    opts.add_argument(
        "--local",
        help="Path to a local part03.xml (used instead of downloading it)",
        type=str,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = setup_argparse()
    source = args.local if args.local else PART03_URL

    print(f"Reading '{source}'")
    root = _fetch_xml(source)

    edition = read_edition(root)
    lib_version = load_module(SHRUB_VERSION_FILENAME, "_shrub_version").__dicom_version__
    if lib_version != edition:
        print(
            "Warning: '__dicom_version__' in src/shrub/_version.py is "
            f"'{lib_version}', needs to be updated to '{edition}'"
        )

    phi = load_module(PHI_DICT_FILENAME, "_phi_dict_fixture")
    dicom = load_module(DICOM_DICT_FILENAME, "_dicom_dict_fixture")
    pools = load_module(POOLS_FILENAME, "_canary_pools")

    basic_profile = phi.BasicProfileTags
    builder = FixtureBuilder(
        dicom.DicomDictionary, dicom.RepeatersDictionary, basic_profile,
        ValueFactory(SEED, pools),
    )

    sequences = {tag for tag in basic_profile if builder.vr_of(tag) == "SQ"}
    tables = index_tables(root)
    children = sequence_children(tables, sequences)

    dataset = {}
    counts = {"phi_child": 0, "real_child": 0, "empty_item": 0}
    for tag in sorted(basic_profile):
        key = f"{tag:08X}"
        if tag >> 16 in NOT_IN_DATASET_GROUPS:
            print(f"Note: {format_tag(tag)} {basic_profile[tag][0]} {NOT_IN_DATASET_GROUPS[tag >> 16]}")
            continue
        if tag not in sequences:
            dataset[key] = builder.plant_tag(tag)
            continue

        child = choose_child(builder, children.get(tag, set()))
        if child is None:
            reason = "is in no PS3.3 table" if tag not in children else "has no usable child in PS3.3"
            print(f"Warning: {format_tag(tag)} {basic_profile[tag][0]} {reason}, left with one empty item")
            counts["empty_item"] += 1
            dataset[key] = {"vr": "SQ", "Value": [{}]}
            continue

        counts["phi_child" if child in basic_profile else "real_child"] += 1
        item = {f"{child:08X}": builder.plant_tag(child, path_prefix=f"{format_tag(tag)}[0]")}
        dataset[key] = {"vr": "SQ", "Value": [item]}

    profile_wildcards = set(phi.WildcardTags)
    if profile_wildcards != set(WILDCARD_INSTANCES):
        raise ValueError(
            f"WildcardTags is now {sorted(profile_wildcards)}, update WILDCARD_INSTANCES to match"
        )
    for instance_tag, repeater_key, vr_override in WILDCARD_INSTANCES.values():
        repeater_vr, vm, _, _, keyword = dicom.RepeatersDictionary[repeater_key]
        vr = vr_override or repeater_vr
        dataset[f"{instance_tag:08X}"] = builder.plant(
            instance_tag, vr, vm, keyword, format_tag(instance_tag), is_canary=True
        )

    check_unique(builder.canaries)

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    with open(FIXTURE_FILENAME, "w") as f:
        json.dump(dict(sorted(dataset.items())), f, indent=2)
        f.write("\n")
    with open(CANARIES_FILENAME, "w") as f:
        json.dump(
            {
                "generator": "utils/generate_fixtures.py",
                "edition": edition,
                "seed": SEED,
                "canaries": builder.canaries,
            },
            f,
            indent=2,
        )
        f.write("\n")

    print(
        f"Processing complete: {len(dataset)} elements -> {FIXTURE_FILENAME}\n"
        f"{len(builder.canaries)} canaries -> {CANARIES_FILENAME}\n"
        f"sequences: {counts['phi_child']} with a PHI child, "
        f"{counts['real_child']} with a non-PHI child, {counts['empty_item']} with an empty item"
    )
