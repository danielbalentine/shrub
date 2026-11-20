# Public tags not listed in Table E.1-1

PS3.15 §E.1.1 requires a de-identifier to protect or retain the attributes listed in Table E.1-1. Under the Basic Profile alone, a public attribute that the table does not list passes through unchanged. This file lists 220 such attributes, found during the read of DICOM 2026d that produced [FEATURES.md](FEATURES.md) (see section 1.3 there).

How the list was made:

1. Readers of the PS3.6 registry noted tags whose names suggested people, organizations, IDs, free text, dates or UIDs. They also cited some tags only for context.
2. A script took every tag cited in those four reports (562 in all) and kept the 220 that are not keys of `BasicProfileTags` in `src/shrub/_phi_dict.py`. VR, name and retired status come from `src/shrub/_dicom_dict.py`.
3. The categories below were assigned by hand from the tag name and VR. Nobody checked each tag's module definition in PS3.3, so a category is a first guess.

The list is not complete. It holds only the tags the readers happened to cite. A complete list would compare every tag in `DicomDictionary` against `BasicProfileTags`.

| Category | Count |
|---|---|
| alt-calendar date | 2 |
| name or ID | 32 |
| free text | 54 |
| URI or address | 11 |
| instance UID | 16 |
| date or time | 8 |
| binary | 3 |
| private pointer | 2 |
| container | 30 |
| structural | 38 |
| DICONDE (industrial) | 3 |
| DICOS (security screening) | 21 |

## Alt-calendar date

Patient dates stored as LO, so a rule that handles dates by VR (DA, DT, TM) misses them.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0010,0033) | LO | Patient's Birth Date in Alternative Calendar |  |
| (0010,0034) | LO | Patient's Death Date in Alternative Calendar |  |

## Name or ID

Names of people or devices, and identifiers that point to a person, device or site.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0010,0214) | LO | Strain Stock Number |  |
| (0010,0217) | LO | Strain Source |  |
| (0010,2295) | LO | Breed Registration Number |  |
| (0010,2298) | CS | Responsible Person Role |  |
| (0018,1003) | LO | Device ID |  |
| (0018,1006) | LO | Grid ID |  |
| (0018,2045) | SH | Target Label |  |
| (0040,0031) | UT | Local Namespace Entity ID |  |
| (0040,0032) | UT | Universal Entity ID |  |
| (0040,A067) | PN | Document Author (Trial) | yes |
| (0044,000A) | LO | Product Lot Identifier |  |
| (0044,0012) | LO | Substance Administration Device ID |  |
| (0062,0020) | UT | Tracking ID |  |
| (0074,100C) | LO | Contact Display Name |  |
| (0088,0130) | SH | Storage Media File-set ID |  |
| (0100,0426) | LO | Authorization Equipment Certification Number |  |
| (2100,0160) | SH | Owner ID |  |
| (2110,0030) | LO | Printer Name |  |
| (3002,0020) | SH | Radiation Machine Name |  |
| (300A,0183) | LO | Patient Setup Label |  |
| (300A,0194) | SH | Fixation Device Label |  |
| (300A,021B) | SH | Source Model ID |  |
| (300A,0236) | LO | Application Setup Name |  |
| (300A,0244) | LO | Template Name |  |
| (300A,0263) | SH | Brachy Accessory Device ID |  |
| (300A,0273) | SH | Afterloader Channel ID |  |
| (300A,030F) | SH | Snout ID |  |
| (300A,0318) | SH | Range Shifter ID |  |
| (300A,0346) | SH | Range Modulator ID |  |
| (300A,0352) | SH | Patient Support ID |  |
| (300A,0421) | SH | General Accessory ID |  |
| (3010,001A) | LO | Manufacturer's Model Version |  |

## Free text

Comments, descriptions, labels and reasons. Same risk as the Clean Descriptors fields, but not in that list.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0008,0401) | LT | Inventory Purpose |  |
| (0008,0402) | LT | Inventory Instance Description |  |
| (0008,0418) | LT | Transaction Status Comment |  |
| (0010,0212) | UC | Strain Description |  |
| (0010,0218) | UT | Strain Additional Information |  |
| (0010,0222) | UC | Genetic Modifications Description |  |
| (0018,003A) | ST | Intervention Description |  |
| (0018,990F) | UT | Protocol Planning Information |  |
| (0018,9916) | LO | Instruction Text |  |
| (0018,9917) | UT | Instruction Description |  |
| (0018,991A) | UT | Instruction Performance Comment |  |
| (0022,112C) | LT | Calculation Comment |  |
| (0024,0044) | LT | Comments on Patient's Performance of Visual Field |  |
| (0028,0A04) | LO | Pixel Spacing Calibration Description |  |
| (0028,1351) | ST | Partial View Description |  |
| (0028,6022) | LO | Frame of Interest Description |  |
| (0028,6190) | ST | Mask Operation Explanation |  |
| (0028,7007) | LO | System Status Comment |  |
| (0028,702A) | LO | Test Result Comment |  |
| (0040,0400) | LT | Comments on the Scheduled Procedure Step |  |
| (0040,A160) | UT | Text Value |  |
| (0040,A16A) | ST | Bibliographic Citation (Trial) | yes |
| (0040,A224) | ST | Identification Description (Trial) | yes |
| (0040,A33A) | ST | Report Status Comment (Trial) | yes |
| (0040,A492) | LO | Completion Flag Description |  |
| (0042,0010) | ST | Document Title |  |
| (0044,0003) | LT | Approval Status Further Description |  |
| (0044,0011) | LO | Substance Administration Notes |  |
| (0044,0106) | UT | Assertion Comments |  |
| (0062,0006) | ST | Segment Description |  |
| (0066,0004) | LT | Surface Comments |  |
| (0070,0081) | LO | Content Description |  |
| (0070,0208) | ST | Graphic Group Description |  |
| (0070,030F) | ST | Fiducial Description |  |
| (0074,1006) | ST | Procedure Step Progress Description |  |
| (0074,1202) | LO | Worklist Label |  |
| (0074,1204) | LO | Procedure Step Label |  |
| (0074,1238) | LT | Reason for Cancellation |  |
| (0082,0003) | UT | Assessment Summary Description |  |
| (0082,000A) | UT | Observation Description |  |
| (0100,0424) | LT | SOP Authorization Comment |  |
| (2200,0004) | LT | Media Disposition |  |
| (3002,0004) | ST | RT Image Description |  |
| (3004,0006) | LO | Dose Comment |  |
| (3006,00C8) | LO | Frame of Reference Transformation Comment |  |
| (3008,0012) | ST | Measured Dose Description |  |
| (3008,0066) | ST | Override Reason |  |
| (3008,0202) | ST | Treatment Status Comment |  |
| (300A,0184) | LO | Patient Additional Position |  |
| (300A,01D0) | ST | Setup Reference Description |  |
| (300A,0402) | ST | Setup Image Comment |  |
| (300A,0730) | ST | Treatment Termination Description |  |
| (300A,0735) | ST | Treatment Tolerance Violation Identification |  |
| (4008,0103) | LO | Reference to Recorded Sound | yes |

## URI or address

URLs, URIs, file names and network addresses. Can expose hostnames or file names that contain patient names.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0008,0407) | UR | Stored Instance Base URI |  |
| (0008,0408) | UR | Folder Access URI |  |
| (0008,0409) | UR | File Access URI |  |
| (0008,040B) | UR | Filename in Container |  |
| (0008,1190) | UR | Retrieve URL |  |
| (0018,1803) | LO | NTP Source Address |  |
| (0028,7FE0) | UR | Pixel Data Provider URL |  |
| (0040,4073) | UR | Storage URL |  |
| (0040,A992) | ST | Uniform Resource Locator (Trial) | yes |
| (0040,E010) | UR | Retrieve URI |  |
| (0074,100A) | UR | Contact URI |  |

## Instance UID

UIDs of instances, frames of reference or events that Table E.1-1 does not mark `U`. Keeping them allows linkage to the originals; replacing them needs the same mapping as other UIDs.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0008,3012) | UI | Radiopharmaceutical Administration Event UID |  |
| (0008,9123) | UI | Creator-Version UID |  |
| (0018,991E) | UI | Target Frame of Reference UID |  |
| (0020,0242) | UI | SOP Instance UID of Concatenation Source |  |
| (0020,9312) | UI | Volume Frame of Reference UID |  |
| (0020,9313) | UI | Table Frame of Reference UID |  |
| (0040,E011) | UI | Retrieve Location UID |  |
| (0040,E030) | UI | Repository Unique ID |  |
| (0040,E031) | UI | Home Community ID |  |
| (0044,0102) | UI | Assertion UID |  |
| (0044,0108) | UI | Referenced Assertion UID |  |
| (0068,7004) | UI | Model Group UID |  |
| (0070,031B) | UI | Referenced Fiducial UID |  |
| (0070,1209) | UI | Volumetric Presentation Input Set UID |  |
| (300A,0675) | UI | Equipment Frame of Reference UID |  |
| (3010,001F) | UI | Segmentation Template UID |  |

## Date or time

Dates and times. A VR-based date rule would catch these.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0008,0404) | DT | Item Inventory DateTime |  |
| (0008,0416) | DT | Expiration DateTime |  |
| (0008,041F) | DT | Study Update DateTime |  |
| (0014,0102) | DA | Secondary Review Date |  |
| (0014,0103) | TM | Secondary Review Time |  |
| (0014,1020) | DA | Expiry Date |  |
| (0014,3076) | DA | Date of Gain Calibration |  |
| (0014,3077) | TM | Time of Gain Calibration |  |

## Binary

Opaque binary values. Inventory record keys and HPGL documents.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0008,041B) | OB | Record Key |  |
| (0008,041C) | OB | Prior Record Key |  |
| (0068,6300) | OB | HPGL Document |  |

## Private pointer

Private Creator strings that name private blocks used by Dimension Index and Functional Group pointers. See FEATURES.md 6.7.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0020,9213) | LO | Dimension Index Private Creator |  |
| (0020,9238) | LO | Functional Group Private Creator |  |

## Container

Sequences that Table E.1-1 does not list, though it lists the attributes inside them. Safe only if Shrub walks every item (FEATURES.md 7.1).

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0008,0051) | SQ | Issuer of Accession Number Sequence |  |
| (0008,0220) | SQ | Responsible Group Code Sequence |  |
| (0008,0310) | SQ | Private Data Element Definition Sequence |  |
| (0008,0419) | SQ | File Set Access Sequence |  |
| (0008,041A) | SQ | File Access Sequence |  |
| (0008,041D) | SQ | Metadata Sequence |  |
| (0008,041E) | SQ | Updated Metadata Sequence |  |
| (0008,0420) | SQ | Inventory Access End Points Sequence |  |
| (0008,0421) | SQ | Study Access End Points Sequence |  |
| (0008,1125) | SQ | Referenced Visit Sequence |  |
| (0010,0024) | SQ | Issuer of Patient ID Qualifiers Sequence |  |
| (0010,0026) | SQ | Source Patient Group Identification Sequence |  |
| (0010,0027) | SQ | Group of Patients Identification Sequence |  |
| (0010,0216) | SQ | Strain Stock Sequence |  |
| (0010,2294) | SQ | Breed Registration Sequence |  |
| (0010,2296) | SQ | Breed Registry Code Sequence |  |
| (0018,A001) | SQ | Contributing Equipment Sequence |  |
| (0020,9170) | SQ | Unassigned Shared Converted Attributes Sequence |  |
| (0020,9171) | SQ | Unassigned Per-Frame Converted Attributes Sequence |  |
| (0020,9172) | SQ | Conversion Source Attributes Sequence |  |
| (0038,0044) | SQ | Discharge Diagnosis Code Sequence | yes |
| (0040,0100) | SQ | Scheduled Procedure Step Sequence |  |
| (0040,A170) | SQ | Purpose of Reference Code Sequence |  |
| (300A,0206) | SQ | Treatment Machine Sequence |  |
| (300A,063A) | SQ | Treatment Device Identification Sequence |  |
| (300A,0743) | SQ | Interlock Originating Device Sequence |  |
| (300A,0746) | SQ | Interlock Resolution User Sequence |  |
| (300A,078C) | SQ | Referenced Patient Setup Photo Sequence |  |
| (300C,0128) | SQ | Beam Hold Originating Device Sequence |  |
| (3010,0019) | SQ | Author Identification Sequence |  |

## Structural

Not identifying. Many must stay, such as Transfer Syntax UID, SOP Class UID and Pixel Data, or must be written by Shrub, such as De-identification Method Code Sequence. Readers cited them for context.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0002,0010) | UI | Transfer Syntax UID |  |
| (0008,0001) | UL | Length to End | yes |
| (0008,0016) | UI | SOP Class UID |  |
| (0008,001C) | CS | Synthetic Data |  |
| (0008,001D) | SQ | Sensitive Content Code Sequence |  |
| (0008,010D) | UI | Context Group Extension Creator UID |  |
| (0008,010E) | UR | Coding Scheme URL |  |
| (0008,0114) | ST | Coding Scheme External ID |  |
| (0008,0116) | ST | Coding Scheme Responsible Organization |  |
| (0008,0117) | UI | Context UID |  |
| (0008,030A) | CS | Private Data Element Value Representation |  |
| (0012,0064) | SQ | De-identification Method Code Sequence |  |
| (0016,0003) | UT | Battery Level |  |
| (0016,0037) | IS | Subject Location |  |
| (0018,1801) | SH | Time Source |  |
| (0028,0104) | US or SS | Smallest Valid Pixel Value | yes |
| (0028,0105) | US or SS | Largest Valid Pixel Value | yes |
| (0034,0003) | UI | Flow Transfer Syntax UID |  |
| (0070,0080) | CS | Content Label |  |
| (0072,0714) | CS | Show Patient Demographics Flag |  |
| (0400,0020) | AT | Data Elements Signed |  |
| (0400,0120) | OB | Signature |  |
| (300A,0123) | CS | Patient Support Rotation Direction |  |
| (300A,0124) | DS | Table Top Eccentric Axis Distance |  |
| (3010,001C) | CS | Device Alternate Identifier Type |  |
| (3010,001D) | LT | Device Alternate Identifier Format |  |
| (3010,0052) | UI | Pertinent SOP Classes in Study |  |
| (3010,0053) | UI | Pertinent SOP Classes in Series |  |
| (3010,0086) | LT | Intended Start Day of Week |  |
| (4008,00FF) | CS | Report Production Status (Trial) | yes |
| (4FFE,0001) | SQ | MAC Parameters Sequence |  |
| (5400,0100) | SQ | Waveform Sequence |  |
| (5400,1010) | OB or OW | Waveform Data |  |
| (5600,0020) | OF | Spectroscopy Data |  |
| (7FE0,0008) | OF | Float Pixel Data |  |
| (7FE0,0009) | OD | Double Float Pixel Data |  |
| (7FE0,0010) | OB or OW | Pixel Data |  |
| (FFFE,E0DD) | NONE | Sequence Delimitation Item |  |

## DICONDE (industrial)

Group 0014, industrial non-destructive testing. Unlikely in medical data.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (0014,0100) | LO | Component Welder IDs |  |
| (0014,0105) | ST | Repair ID |  |
| (0014,602F) | ST | Coil Configuration ID |  |

## DICOS (security screening)

Group 4010, airport security screening. Unlikely in medical data, though Boarding Pass ID identifies a person.

| Tag | VR | Name | Retired |
|---|---|---|---|
| (4010,1007) | SH | Route Segment ID |  |
| (4010,1013) | LT | Threat Category Description |  |
| (4010,101A) | SH | Boarding Pass ID |  |
| (4010,101E) | SH | Route Segment Start Location ID |  |
| (4010,101F) | SH | Route Segment End Location ID |  |
| (4010,1025) | DT | Route Segment Start Time |  |
| (4010,1026) | DT | Route Segment End Time |  |
| (4010,1029) | LO | Threat Detection Algorithm and Version |  |
| (4010,102A) | SH | Assigned Location |  |
| (4010,102B) | DT | Alarm Decision Time |  |
| (4010,1041) | DT | OOI Owner Creation Time |  |
| (4010,1047) | SQ | OOI Owner Sequence |  |
| (4010,1051) | LO | Itinerary ID |  |
| (4010,1052) | SH | Itinerary ID Type |  |
| (4010,1053) | LO | Itinerary ID Assigning Authority |  |
| (4010,1054) | SH | Route ID |  |
| (4010,1055) | SH | Route ID Assigning Authority |  |
| (4010,1058) | SH | Carrier ID |  |
| (4010,1059) | CS | Carrier ID Assigning Authority |  |
| (4010,1068) | LT | OOI Type Descriptor |  |
| (4010,1078) | ST | PTO Location Description |  |
