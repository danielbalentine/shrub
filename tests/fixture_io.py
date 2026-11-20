"""
Load the generated JSON fixtures and write them out as .dcm files.

utils/generate_fixtures.py writes the fixtures as DICOM JSON. This module
turns them into pydicom datasets and .dcm files at test time, so no .dcm
file is ever committed. It also resolves the canary paths recorded in
*.canaries.json, so sanity tests and the later integration test check
canaries the same way.
"""

import base64
import json
import re
from pathlib import Path

from pydicom import Dataset, dcmread
from pydicom.dataelem import DataElement
from pydicom.dataset import FileMetaDataset
from pydicom.multival import MultiValue
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage

FIXTURE_DIR = Path(__file__).parent / "fixtures"

PATH_STEP_RE = re.compile(r"\(([0-9A-F]{4}),([0-9A-F]{4})\)(?:\[(\d+)\])?")


def load_fixture(name: str) -> Dataset:
    """tests/fixtures/<name>.json as a pydicom Dataset."""
    with open(FIXTURE_DIR / f"{name}.json") as f:
        return Dataset.from_json(json.load(f))


def load_canaries(name: str) -> dict:
    """tests/fixtures/<name>.canaries.json as a dict."""
    with open(FIXTURE_DIR / f"{name}.canaries.json") as f:
        return json.load(f)


def write_dcm(ds: Dataset, path: Path) -> Path:
    """Write `ds` to `path` as a DICOM file and return the path.

    DICOM JSON has no file meta header (group 0002), so this builds one:
    Explicit VR Little Endian, Secondary Capture as the SOP class, and
    MediaStorageSOPInstanceUID copied from SOPInstanceUID the way real
    files carry it. The fixture's SOPInstanceUID is a canary, so its copy
    in the header is a second place a leak can happen.
    """
    if "SOPClassUID" not in ds:
        ds.SOPClassUID = SecondaryCaptureImageStorage

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
    file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.file_meta = file_meta

    ds.save_as(path, enforce_file_format=True)
    return path


def fixture_dcm(name: str, directory: Path) -> Dataset:
    """Load a JSON fixture, write it to `directory` as <name>.dcm, and read
    it back, so tests see what a real file on disk contains."""
    path = write_dcm(load_fixture(name), directory / f"{name}.dcm")
    return dcmread(path)


def resolve_path(ds: Dataset, path: str) -> DataElement | None:
    """Follow a canary path such as "(0040,A073)[0](0040,A030)" and return
    the element there, or None if any step is missing. A path that starts
    in group 0002 is looked up in the file meta header."""
    steps = PATH_STEP_RE.findall(path)
    if "".join(f"({g},{e})" + (f"[{i}]" if i else "") for g, e, i in steps) != path:
        raise ValueError(f"malformed canary path {path!r}")

    current = ds
    for position, (group, element, index) in enumerate(steps):
        tag = int(group + element, 16)
        if position == 0 and group == "0002":
            current = getattr(ds, "file_meta", None)
            if current is None:
                return None
        if tag not in current:
            return None
        found = current[tag]
        if not index:
            return found
        items = found.value
        if int(index) >= len(items):
            return None
        current = items[int(index)]
    return None


def _as_list(value) -> list:
    if isinstance(value, (list, MultiValue)):
        return list(value)
    return [value]


def canary_matches(element: DataElement, canary: dict) -> bool:
    """True if `element` holds exactly the canary's planted value."""
    if "value_base64" in canary:
        return element.value == base64.b64decode(canary["value_base64"])

    actual = _as_list(element.value)
    expected = canary["value"]
    if len(actual) != len(expected):
        return False
    vr = canary["vr"]
    if vr == "PN":
        return [str(a) for a in actual] == expected
    if vr in ("DS", "FL", "FD"):
        return all(float(a) == float(e) for a, e in zip(actual, expected))
    if vr == "IS":
        return all(int(a) == int(e) for a, e in zip(actual, expected))
    return actual == expected
