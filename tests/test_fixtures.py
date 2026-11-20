"""
Sanity tests for the generated basic_profile fixture.

These check the fixture, not shrub. A fixture that silently lost tags, or
whose canaries never got planted, would let the later integration test
pass for the wrong reason. If one of these fails, rerun
utils/generate_fixtures.py, or fix the generator.
"""

import base64

import pytest

from src.shrub._phi_dict import BasicProfileTags, WildcardTags
from src.shrub._version import __dicom_version__
from src.shrub.vr_values import VR_DUMMY_VALUES
from tests.fixture_io import (
    canary_matches,
    fixture_dcm,
    load_canaries,
    load_fixture,
    resolve_path,
)

NAME = "basic_profile"


@pytest.fixture(scope="module")
def json_ds():
    return load_fixture(NAME)


@pytest.fixture(scope="module")
def dcm_ds(tmp_path_factory):
    return fixture_dcm(NAME, tmp_path_factory.mktemp("fixtures"))


@pytest.fixture(scope="module")
def canaries():
    return load_canaries(NAME)


def wildcard_matches(pattern: str, tag: int) -> bool:
    """"60xx3000" matches 0x60023000. An x matches any hex digit."""
    return all(p == "x" or p == t for p, t in zip(pattern.lower(), f"{tag:08x}"))


# Basic Profile tags a file's main dataset cannot hold. Group 0000 is the
# command group, used only in network messages. (0002,0003) is file meta,
# which fixture_io.write_dcm fills from SOPInstanceUID.
NOT_IN_DATASET = {0x00001000, 0x00001001, 0x00020003}


class TestCoverage:
    def test_every_basic_profile_tag_is_present(self, json_ds):
        missing = [
            f"{tag:08X}" for tag in BasicProfileTags
            if tag not in json_ds and tag not in NOT_IN_DATASET
        ]
        assert not missing

    def test_excluded_tags_are_only_command_and_file_meta_groups(self):
        """If a new edition adds another group 0000 or 0002 tag, this fails
        so someone decides how the fixture handles it."""
        assert {tag for tag in BasicProfileTags if tag >> 16 in (0x0000, 0x0002)} == NOT_IN_DATASET

    def test_one_instance_per_wildcard_outside_the_base_group(self, json_ds):
        for pattern in WildcardTags:
            instances = [int(elem.tag) for elem in json_ds if wildcard_matches(pattern, int(elem.tag))]
            assert len(instances) == 1, pattern
            base_group = int(pattern[:2] + "00", 16)
            assert instances[0] >> 16 != base_group, pattern

    def test_sequences_hold_one_item_with_at_most_one_flat_child(self, json_ds):
        for elem in json_ds:
            if elem.VR != "SQ":
                continue
            assert len(elem.value) == 1, elem.tag
            item = elem.value[0]
            assert len(item) <= 1, elem.tag
            assert all(child.VR != "SQ" for child in item), elem.tag


class TestCanaries:
    def test_edition_matches_shrub_version(self, canaries):
        assert canaries["edition"] == __dicom_version__

    def test_canary_values_are_unique(self, canaries):
        keys = [str(c.get("value", c.get("value_base64"))) for c in canaries["canaries"]]
        assert len(keys) == len(set(keys))

    def test_no_canary_equals_a_shrub_dummy_value(self, canaries):
        """A canary that matched a value shrub writes for D would show up
        as a false leak in the integration test."""
        dummies = {repr(v) for v in VR_DUMMY_VALUES.values()}
        for canary in canaries["canaries"]:
            if "value_base64" in canary:
                values = [base64.b64decode(canary["value_base64"])]
            else:
                values = canary["value"]
            assert not {repr(v) for v in values} & dummies, canary["paths"]

    def test_every_canary_is_planted_in_the_json(self, json_ds, canaries):
        self._assert_planted(json_ds, canaries, skip_file_meta=True)

    def test_every_canary_survives_the_dcm_round_trip(self, dcm_ds, canaries):
        self._assert_planted(dcm_ds, canaries, skip_file_meta=False)

    @staticmethod
    def _assert_planted(ds, canaries, skip_file_meta):
        failures = []
        for canary in canaries["canaries"]:
            for path in canary["paths"]:
                if skip_file_meta and path.startswith("(0002,"):
                    continue
                element = resolve_path(ds, path)
                if element is None:
                    failures.append(f"{path}: missing")
                elif not canary_matches(element, canary):
                    failures.append(f"{path}: has {element.value!r}")
        assert not failures, "\n".join(failures[:20])


class TestDcmFile:
    def test_file_meta(self, dcm_ds):
        meta = dcm_ds.file_meta
        assert meta.TransferSyntaxUID == "1.2.840.10008.1.2.1"
        assert meta.MediaStorageSOPClassUID == "1.2.840.10008.5.1.4.1.1.7"
        assert meta.MediaStorageSOPInstanceUID == dcm_ds.SOPInstanceUID
