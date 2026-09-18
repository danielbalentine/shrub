"""
vr_dummy_values_for_testing.py

Fake-but-realistic PHI-shaped *input* values, keyed by VR, for building
unit-test fixtures. This is the mirror image of vr_dummy_values.py's
VR_DUMMY_VALUES: that file holds the safe *output* a 'D' action should
produce; this file holds plausible *before* values -- what a real
(not-yet-deidentified) dataset might actually contain -- so tests can
populate a DataElement, run it through ActionCode.apply() (or the
StandardTag/TagList pipeline), and assert the PHI is actually gone.

None of these are real people, MRNs, or institutions -- just realistic
in shape/format so length limits, character-set rules, and multi-value
handling get exercised honestly.

Scope: the same 18 VRs verified against Table E.1-1's D-action tags in
vr_dummy_values.py, plus SQ and UI (the two flagged as needing special
handling there). If tags using other VRs (e.g. the plain numeric ones)
turn up under non-D actions, extend this file rather than assuming
these 20 are exhaustive for the whole Basic Profile table.

On VM (Part 5, Section 6.4): a DataElement's Value Field holds however
many Values that Data Element's VM allows, but "Data Elements with a
VR of LT, OB, OD, OF, OL, OV, OW, SQ, ST, UN, UR or UT shall always
have a Value Multiplicity of one." pydicom mirrors this directly --
DataElement.value is a plain scalar at VM=1, and only becomes an
actual Python list (MultiValue) at VM>1. So VR_PHI_VALUES below gives
one scalar per VR (the VM=1 shape, correct for every VR here, and the
*only* legal shape for the twelve VRs above). Real VM>1 examples --
only legal for VRs outside that set -- are separate, in
VR_PHI_MULTIVALUED_EXAMPLES, as genuine lists.
"""

# One realistic "before" value per VR, as a plain scalar -- matching what
# DataElement.value actually looks like at VM=1 (the only legal VM for the
# text/binary/container VRs Part 5 6.4 restricts to VM=1, and a safe default
# for the rest since none of these particular attributes are VM>1 by default).
VR_TEST_VALUES = {
    "AE": "MERCYHOSP_CT1",
    "AS": "045Y",
    "CS": "M",
    "DA": "19650304",
    "DT": "20230615103045.123456+0000",
    "LO": "St. Mary Regional Medical Center",
    "LT": "Patient reports hx of hypertension; contact Dr. Whitfield, (555) 019-2837.",
    "OB": b"FAKE_CERT_BYTES_JOHNDOE_1234567890",
    "PN": "Doe^Jane^Marie^Dr^Jr",
    "SH": "MRN00219384",
    "ST": "Chart notes filed under Jane M. Doe, DOB 1965-03-04, room 214B.",
    "TM": "103045.123456",
    "UC": "DETECTOR-SN-88213-JOHNDOE-CALIBRATION-LOG-2023",
    "UI": "1.2.826.0.1.3680043.8.498.10812349871234981234",
    "UN": b"\x01\x02\x03PATIENT_DOE_JANE\x00",
    "UR": "http://hospital-pacs.example.org/records/doe-jane-19650304",
    "UT": (
        "Report generated for patient Jane M. Doe (MRN 00219384) on 2023-06-15 "
        "by Dr. Angela Whitfield at St. Mary Regional Medical Center."
    ),
}

# A second, alternate scalar per VR -- for tests that want two distinct
# realistic values (e.g. round-trip/equality checks) without implying
# either one is itself multi-valued.
VR_PHI_VALUES_ALT = {
    "AE": "RADIOLOGY_PACS",
    "AS": "003M",
    "CS": "F",
    "DA": "20230615",
    "DT": "19870422081530.000000",
    "LO": "Referring: Dr. Angela Whitfield",
    "LT": "Follow-up call placed to Whitfield, A. regarding case notes.",
    "OB": b"FAKE_CERT_BYTES_SMITHJOHN_0987654321",
    "PN": "Smith^John^Robert",
    "SH": "ACC2023061501",
    "ST": "Signed consent on file, see records for Doe, Jane M.",
    "TM": "081530.000000",
    "UC": "DETECTOR-SN-99881-SMITHJOHN-CALIBRATION-LOG-2024",
    "UI": "1.2.840.113619.2.55.3.604688119.971.1687023045.847",
    "UN": b"\x01\x02\x03PATIENT_SMITH_JOHN\x00",
    "UR": "http://hospital-pacs.example.org/records/smith-john-19870422",
    "UT": (
        "Structured report for patient John R. Smith (MRN 41028833), reviewed "
        "by Dr. Angela Whitfield."
    ),
}

# Values genuinely legal at VM > 1 -- real Python lists, matching pydicom's
# MultiValue shape. Only VRs *outside* the Part 5 6.4 VM=1-only set (see
# module docstring) are eligible; these two are tied to attributes that are
# actually commonly multi-valued in practice, not arbitrary examples.
VR_PHI_MULTIVALUED_EXAMPLES = {
    "CS": ["ORIGINAL", "PRIMARY", "AXIAL"],  # e.g. Image Type, VM 2-n
    "PN": ["Doe^Jane", "Smith^John"],  # e.g. Other Patient Names, VM 1-n
}

# Boundary / tricky cases worth their own explicit test parametrization,
# rather than burying them in VR_PHI_VALUES above.
VR_PHI_EDGE_CASES = {
    "empty_string": {"LO": "", "SH": "", "ST": ""},
    "max_length_lo_64": {"LO": "X" * 64},  # LO hard cap
    "max_length_sh_16": {"SH": "X" * 16},  # SH hard cap
    "unicode_name": {
        "PN": "M\u00fcller^J\u00fcrgen"
    },  # non-ASCII, tests SpecificCharacterSet handling
    # raw DICOM wire form of VR_PHI_MULTIVALUED_EXAMPLES['CS'] -- pydicom
    # accepts either the backslash-joined str or the list; tests should
    # confirm your code handles both, since raw/wire data arrives as this.
    "multivalued_cs_backslash_str": {"CS": "ORIGINAL\\PRIMARY\\AXIAL"},
    "pn_multi_component_groups": {
        "PN": "Doe^Jane==D\u00f3e^Jane==DOE^JANE"
    },  # alphabetic=ideographic=phonetic
    "embedded_phi_in_free_text": {
        # exercises the 'C' (clean) action: PHI embedded inside a
        # structured/free-text field rather than as the whole value
        "UT": "Findings reviewed with patient John Q. Public (DOB 1958-11-02) present.",
    },
}

# SQ tags need recursion, not a flat value -- this is a stand-in for one
# nested Item's contents (tag keyword -> PHI value), for test code to wrap
# into an actual pydicom Dataset/Sequence. Modeled on Referenced Patient
# Sequence, one of the 5 D-action SQ tags noted in vr_dummy_values.py.
SQ_PHI_ITEM_EXAMPLE = [
    {
        "PatientName": "Doe^Jane^Marie",
        "PatientID": "MRN00219384",
        "ReferencedSOPClassUID": "1.2.840.10008.5.1.4.1.1.2",
        "ReferencedSOPInstanceUID": "1.2.826.0.1.3680043.8.498.10812349871234981234",
    }
]
