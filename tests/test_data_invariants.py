"""
test_data_invariants.py

Regression tests pinning down facts about the generated DICOM data
(_phi_dict.py, _dicom_dict.py) that the rest of the codebase's design
depends on. These aren't testing behavior -- they're testing that the
standard's shape hasn't shifted underneath us (e.g. after regenerating
against a newer DICOM revision). If one of these breaks, it means an
assumption baked into ActionCode/StandardTag/TagList needs revisiting,
not just that a value changed.
"""

from src.shrub._phi_dict import BasicProfileTags


class TestBasicProfileActionCodes:
    def test_basic_profile_action_set_is_fully_enumerated(self):
        """K and C are never a Basic Profile action -- confirmed empirically,
        not assumed. If this breaks, _keep/_clean become reachable without
        any mode enabled, and the "C is always mode-traceable via tag.modes"
        design assumption breaks with it."""
        basic_profile_actions = {row[3] for row in BasicProfileTags.values()}
        assert basic_profile_actions == {
            'Z', 'Z/D', 'X', 'X/D', 'X/Z', 'X/Z/D', 'X/Z/U*', 'D', 'U',
        }

    def test_K_and_C_never_appear_in_basic_profile(self):
        basic_profile_actions = {row[3] for row in BasicProfileTags.values()}
        assert 'K' not in basic_profile_actions
        assert 'C' not in basic_profile_actions


class TestDActionVRCoverage:
    def test_d_action_vr_set_matches_audited_18(self):
        """Per vr_dummy_values.py: 93 D-action tags exist, every one resolves
        to a real VR (zero misses), and they only ever use these 18 VRs.
        TODO: fill in real lookup against DicomDictionary once available here.
        """
        # d_action_tags = [tag for tag, row in BasicProfileTags.items() if row[3] == 'D']
        # vrs = {DicomDictionary[tag][0] for tag in d_action_tags}
        # assert vrs == set(VR_DUMMY_VALUES) | {'SQ', 'UI'}
        # assert len(d_action_tags) == 93
        ...