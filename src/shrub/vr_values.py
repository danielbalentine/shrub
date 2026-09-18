"""
vr_dummy_values.py
 
Dummy values for the 'D' action code (replace with a non-zero length
value that may be a dummy value, consistent with the VR).
 
Covers only the VRs actually verified to appear on a D-action tag in
Table E.1-1 -- cross-referenced against Part 6's Data Dictionary
(Table 6-1, Tag -> VR), not every VR the standard defines. 93 D-action
tags exist; every one of them resolved to a real VR (zero misses), and
they only ever use these 18. None of the plain numeric VRs (FL, FD, IS,
DS, SL, SS, SV, UL, US, UV) or the other binary VRs (OD, OF, OL, OV, OW)
appear on any D-action tag, so they're deliberately left out rather than
carried as unverified dead code.
"""

from pydicom.sequence import Sequence
 
VR_DUMMY_VALUES = {
    'AE': 'ANONYMIZED',                    # <=16 bytes -- e.g. Destination AE
    'AS': '000Y',                          # 4 bytes fixed, nnnD/W/M/Y -- Selector AS Value
    'CS': 'ANON',                          # <=16 bytes -- Reason for the Attribute Modification
    'DA': '19000101',                      # 8 bytes fixed, YYYYMMDD -- Date, Safe Position Exit Date
    'DT': '19000101000000.000000',        # <=26 bytes -- Assertion DateTime, etc. (25 tags, the largest group)
    'LO': 'ANONYMIZED',                    # <=64 chars -- Acquisition Field Of View Label, etc.
    'LT': 'ANONYMIZED',                    # <=10240 chars -- Selector LT Value
    'OB': b'\x00',                         # binary byte stream -- Certificate of Signer, Encapsulated Document
    'PN': 'ANONYMIZED^ANONYMIZED',         # <=64 chars per component group -- Person Name, Selector PN Value
    'SH': 'ANON',                          # <=16 chars -- Entity Label, Radiation Generation Mode Label
    'ST': 'ANONYMIZED',                    # <=1024 chars -- Interlock Description, Interlock Origin Description
    'TM': '000000.000000',                 # <=14 bytes -- Safe Position Exit/Return Time
    'UC': 'ANONYMIZED',                    # unlimited, trailing-space padded -- X-Ray Detector/Source ID
    'UN': b'',                             # unknown encoding -- Selector UN Value
    'UR': 'http://anonymized.invalid/',    # URI, no backslash -- Selector UR Value
    'UT': 'ANONYMIZED',                    # unlimited text -- Selector UT Value
}
 

VR_EMPTY_VALUES = {
    # text / string-ish
    'AE': '', 'AS': '', 'CS': '', 'DA': '', 'DT': '', 'LO': '', 'LT': '',
    'PN': '', 'SH': '', 'ST': '', 'TM': '', 'UC': '', 'UI': '', 'UR': '', 'UT': '',
    # binary
    'OB': b'', 'OD': b'', 'OF': b'', 'OL': b'', 'OV': b'', 'OW': b'', 'UN': b'',
    # numeric -- absence is None, not 0 or ''
    'DS': None, 'FL': None, 'FD': None, 'IS': None,
    'SL': None, 'SS': None, 'SV': None, 'UL': None, 'US': None, 'UV': None,
    # sequence -- Type 2 permits zero Items, but the value is still a Sequence
    'SQ': Sequence([]),
}

# these two VRs appear on D-action tags but cannot get a flat dummy value
# the same way -- each needs its own dedicated logic, not a lookup
VR_NEEDS_SPECIAL_HANDLING = {
    'SQ': 'Sequence (5 D-action tags, e.g. Content Sequence, Flow Identifier Sequence) -- D means recurse into contents, not substitute a value',
    'UI': 'UID (1 D-action tag: Annotation Group UID) -- must be a validly-formatted, run-consistent UID (digits/periods only), see the UID consistency cache',
}