# De-identification Features in DICOM 2026d

This file lists what the DICOM Standard (edition 2026d) says about
de-identification and records how much of it Shrub implements today.

Each entry has:

- **Standard**: where the requirement lives. `§` is a section, `Table` a table.
- **Status**:
  - `implemented`: Shrub changes datasets this way and a test covers it.
  - `data only`: the Standard's content is in a generated dict or class, but no code applies it to a dataset yet.
  - `not implemented`: nothing in the code yet.
- **Code**: `file:line` when code exists.
- **Label**: `normative` (a requirement), `informative` (Notes, examples, PS3.17), or `retired`.

The rules come from PS3.15 Annex E. The rest of the Standard (PS3.3, PS3.5, PS3.10, PS3.16 and others) says where identifying data can hide and how the marking attributes work. See [How this list was made](#how-this-list-was-made) for how much of the Standard was read.

---

## 1. Profile scope and conformance

### 1.1 Basic Application Level Confidentiality Profile
- **Standard**: PS3.15 §E.1, §E.1.1, §E.2; PS3.16 Annex D code 113100
- **Label**: normative
- **Status**: data only
- **Code**: `src/shrub/_phi_dict.py:9` (`BasicProfileTags`), `src/shrub/_phi_dict.py:665` (`WildcardTags`), `utils/generate_phi_dict.py`
- **Notes**: A de-identifier must "protect or retain all instances of the Attributes listed in Table E.1-1, whether contained in the top level Data Set or embedded in an Item of a Sequence of Items." The Basic Profile removes patient identity and demographics, responsible parties, personnel, organizations, UIDs, dates and times, and Private Attributes from non-pixel data, including graphics and overlays. It does not touch pixel data unless Clean Pixel Data or Clean Recognizable Visual Features is also applied (§E.2). Shrub has no entry point that walks a dataset yet. `TODO.md` lists it.

### 1.2 Table E.1-1 (per-attribute actions)
- **Standard**: PS3.15 Table E.1-1
- **Label**: normative
- **Status**: data only
- **Code**: `src/shrub/_phi_dict.py`, `src/shrub/tags.py:49` (`StandardTag`), `src/shrub/tags.py:77` (`WildcardTag`)
- **Notes**: Checked by script against the 2026d XML: 656 of the table's 657 rows match the generated dicts exactly in every column. The one missing row is the blanket `Private Attributes (gggg,eeee) where gggg is odd` row. Its Basic action is `X` and its Retain Safe Private action is `C`. The generator skips it on purpose at `utils/generate_phi_dict.py:256-257`, so it needs its own handling. See 6.1. Breakdown of Basic Profile actions: X 413, D 93, U 55, Z 42, X/D 23, X/Z 11, X/Z/D 8, Z/D 6, X/Z/U* 2. 100 rows are retired attributes and 181 are not in any standard composite IOD.

### 1.3 Table E.1-1 is a minimum, not a complete list
- **Standard**: PS3.15 §E.1.1 (Notes after Table E.1-1a)
- **Label**: normative
- **Status**: not implemented
- **Notes**: Identifying data can also be in Private Attributes, new Standard Attributes, Retired Attributes, and attributes used only in Standard Extended SOP Classes. "It is the responsibility of the de-identifier to ensure that all identifying information is removed." The table "is subject to extension as the DICOM Standard evolves", and the Standard suggests handling all DA, DT and TM values by VR rather than only the listed ones. It does not say whether to remove known risks or keep only known-safe data. "De-identification of Private SOP Classes is not defined." Shrub has to decide what to do with a public tag that isn't in Table E.1-1. `TODO.md` already lists this decision.

  The second pass gave a partial measure of the gap. The PS3.6 readers cited 562 tags. A script found that 220 of them are not in Table E.1-1, and under the Basic Profile alone those 220 pass through unchanged. [UNLISTED.md](UNLISTED.md) lists all 220, grouped by a first-guess category. About 70 of them are not identifying. These are mostly structural values such as Pixel Data and SOP Class UID, plus sequences whose contents the table does list. The rest are a real gap:
  - Patient's Birth Date in Alternative Calendar (0010,0033) and Patient's Death Date in Alternative Calendar (0010,0034). Both are LO, so a date rule keyed on DA, DT and TM misses them.
  - 32 names and IDs, such as Document Author (Trial) (0040,A067), Contact Display Name (0074,100C), Owner ID (2100,0160) and Printer Name (2110,0030).
  - 54 free-text fields, such as Text Value (0040,A160), Document Title (0042,0010) and Dose Comment (3004,0006).
  - 11 URIs and addresses, 16 instance UIDs not marked `U`, and 8 dates and times.

  The list holds only the tags the readers cited. A full comparison of `DicomDictionary` against `BasicProfileTags` would be complete.

### 1.4 Conformance Statement content for a de-identifier
- **Standard**: PS3.15 §E.1.3; PS3.2 §N.1.6 (Table N.1-14), §N.8.4.4 (Table N.8-7), §N.11.2.6 (Table N.11-6)
- **Label**: normative (PS3.15), informative template (PS3.2)
- **Status**: not implemented
- **Notes**: The Conformance Statement must cover:
  - which attributes are removed, and how dummy values are made
  - what goes into any Encrypted Attributes Data Set, and how keys are chosen
  - how far referential integrity of replacement UIDs reaches (across Studies, or when the same Study is processed twice)
  - which attributes are inserted
  - supported Transfer Syntaxes and Options

  PS3.2 §N.8.4.4 also asks how the de-identifier treats attributes added in later editions (kept, removed, or configurable). That ties directly to Shrub's edition tracking. The PS3.2 template for a vendor's private attributes (Table N.9-26) has an "Identifiable Information" column with values such as SAFE. Those vendor tables are one of the sources the Retain Safe Private Option accepts (see 6.2). Clean Descriptors, Modified Dates, Retain Patient Characteristics, Retain Safe Private and preamble handling each add their own documentation requirement. Their entries below give the details.

### 1.5 Options override the Profile
- **Standard**: PS3.15 §E.1.1 (text after Table E.1-1a), §E.3
- **Label**: normative
- **Status**: data only
- **Code**: `src/shrub/tags.py:18` (`MODE_NAMES`), `src/shrub/tags.py:131` (`TagList.add_tag`), `src/shrub/tags.py:154` (`get_highest_order_action`)
- **Notes**: When an Option applies to an attribute, its action replaces the Basic Profile action. `TagList` already picks the Option action, and picks `C` when two enabled Options disagree. The only disagreement in Table E.1-1 is Retain Device Identity `K` versus Retain Longitudinal Modified Dates `C`.

### 1.6 Limits the Standard states about itself
- **Standard**: PS3.15 Annex E intro, §E.1.1 Notes; PS3.18 §8.11
- **Label**: normative / informative
- **Status**: not applicable (documentation)
- **Notes**: "De-identification of the Attributes does not imply de-identification of the Information Object." Conformance does not guarantee confidentiality. Pixel matching against originals, attacks on encryption, and Options that keep more data all raise the risk of re-identification. `README.md` already carries a warning along these lines.

---

## 2. Action codes

The legend is PS3.15 Table E.1-1a, repeated in PS3.2 Table N.11-6.

### 2.1 D: replace with a non-zero-length dummy value
- **Standard**: PS3.15 Table E.1-1a
- **Label**: normative
- **Status**: implemented, but not for SQ or UI
- **Code**: `src/shrub/action_codes.py:26`, `src/shrub/vr_values.py:19` (`VR_DUMMY_VALUES`), `src/shrub/vr_values.py:54` (`VR_NEEDS_SPECIAL_HANDLING`); tests `tests/test_action_codes.py:65`, `tests/test_data_invariants.py:34`
- **Notes**: "Consistent with the VR." §E.1.1 adds that dummy values must keep the IOD valid and must not identify the patient. Values for one entity (Patient ID, Study ID, Series Number) must stay consistent across that entity's instances. `D` is not handled yet for the 5 Sequence tags, such as Content Sequence, or for the one UI tag, Annotation Group UID.

### 2.2 Z: replace with zero length (or a dummy)
- **Standard**: PS3.15 Table E.1-1a
- **Label**: normative
- **Status**: implemented
- **Code**: `src/shrub/action_codes.py:29`, `src/shrub/vr_values.py:39` (`VR_EMPTY_VALUES`); test `tests/test_action_codes.py:44`

### 2.3 X: remove (for a Sequence, all Items and their contents)
- **Standard**: PS3.15 Table E.1-1a
- **Label**: normative
- **Status**: implemented
- **Code**: `src/shrub/action_codes.py:32`; tests `tests/test_action_codes.py:86`, `tests/test_action_codes.py:103`

### 2.4 K: keep (unchanged for non-Sequences, cleaned for Sequences)
- **Standard**: PS3.15 Table E.1-1a; §E.1.1
- **Label**: normative
- **Status**: not implemented (stub)
- **Code**: `src/shrub/action_codes.py:35`
- **Notes**: "Keeping a Sequence ('K' action) requires recursively applying the Profile rules to each Data Set in each Item of the Sequence (for example, in order to remap any UIDs contained within that sequence)." `K` only appears under Options. The test at `tests/test_data_invariants.py:27` checks this.

### 2.5 C: clean (replace with values of similar meaning that don't identify)
- **Standard**: PS3.15 Table E.1-1a; §E.1.1 Notes
- **Label**: normative
- **Status**: not implemented (raises `NotImplementedError`)
- **Code**: `src/shrub/action_codes.py:39`
- **Notes**: On a Sequence, `C` means either change values whose meaning is known, or recursively apply the Profile to each Item. It applies to Code Sequences too, because private or local codes can identify someone, especially codes for providers and staff. Only Options use `C`.

### 2.6 U: replace with a consistent replacement UID
- **Standard**: PS3.15 Table E.1-1a
- **Label**: normative
- **Status**: not implemented (raises `NotImplementedError`)
- **Code**: `src/shrub/action_codes.py:42`
- **Notes**: "Internally consistent within a set of Instances." See section 4.

### 2.7 Conditional codes (Z/D, X/Z, X/D, X/Z/D, X/Z/U*)
- **Standard**: PS3.15 Table E.1-1a
- **Label**: normative
- **Status**: data only
- **Code**: parsed at `src/shrub/action_codes.py:9-11`; `apply` always uses `chain[0]` (`src/shrub/action_codes.py:22-24`)
- **Notes**: Which branch applies depends on the attribute's Type (1, 2 or 3) in the IOD of the instance being processed. Shrub doesn't know attribute Types per IOD yet. Always taking the first branch gives the most aggressive action (X or Z), which can produce a non-conformant IOD when the attribute is Type 1 or 2. `X/Z/U*` also covers UIDs inside the sequence. `requires_uid_check` is parsed (`action_codes.py:9`) but nothing uses it yet.

### 2.8 Actions apply to a whole Sequence and its contents
- **Standard**: PS3.15 §E.1.1 (text after Table E.1-1a); §E.1.1 "the complete Sequence of Items may need to be protected"
- **Label**: normative
- **Status**: not implemented
- **Notes**: An action on a Sequence covers the Sequence and everything in it. A protected attribute inside a Sequence may mean the whole Sequence needs protecting.

---

## 3. Marking a dataset as de-identified

### 3.1 Patient Identity Removed (0012,0062) = YES
- **Standard**: PS3.15 §E.1.1; PS3.3 §C.7.1.1 (Table C.7-1)
- **Label**: normative
- **Status**: not implemented
- **Notes**: Set or add `YES`. PS3.3 says `YES` asserts that identity has been removed from both the attributes and the pixel data. If YES, (0012,0063) or (0012,0064) is required. This tag is not in Table E.1-1; the de-identifier adds it. A re-identifier sets it back to `NO` and removes (0012,0063) and (0012,0064) (§E.1.2).

### 3.2 De-identification Method (0012,0063) / Code Sequence (0012,0064), CID 7050
- **Standard**: PS3.15 §E.1.1; PS3.3 Table C.7-1; PS3.16 CID 7050 and Annex D codes 113100 to 113112
- **Label**: normative
- **Status**: not implemented
- **Notes**: Add one CID 7050 code per Profile and Option applied, and/or a free-text description. CID 7050 has 13 codes: 113100 Basic Application Confidentiality Profile, then 113101 to 113112:
  - 113101 Clean Pixel Data
  - 113102 Clean Recognizable Visual Features
  - 113103 Clean Graphics
  - 113104 Clean Structured Content
  - 113105 Clean Descriptors
  - 113106 Retain Longitudinal Temporal Information Full Dates
  - 113107 Retain Longitudinal Temporal Information Modified Dates
  - 113108 Retain Patient Characteristics
  - 113109 Retain Device Identity
  - 113110 Retain UIDs
  - 113111 Retain Safe Private
  - 113112 Retain Institution Identity

  The group is Extensible, and (0012,0063) is VM 1-n, so successive de-identification steps can each be recorded. PS3.17 §LLL.2 shows a real example value: `CTP: DICOM-S142-Baseline: 20090627:021422`. This is how a Shrub output would state "de-identified to DICOM 2026d" in the data itself.

### 3.3 Longitudinal Temporal Information Modified (0028,0303)
- **Standard**: PS3.15 §E.2, §E.3.6; PS3.3 §C.12.1 (Table C.12-1)
- **Label**: normative
- **Status**: not implemented (noted in `TODO.md`)
- **Notes**: Add `REMOVED` when neither Retain Longitudinal Option is used, `UNMODIFIED` with Full Dates, and `MODIFIED` with Modified Dates.

### 3.4 Burned In Annotation (0028,0301) and Recognizable Visual Features (0028,0302)
- **Standard**: PS3.15 §E.3.1, §E.3.2; PS3.3 §C.7.6.1 (Table C.7-9), §C.8.6.3, §C.24.2
- **Label**: normative
- **Status**: not implemented
- **Notes**: Clean Pixel Data adds (0028,0301) = `NO`. Clean Recognizable Visual Features adds (0028,0302) = `NO`. Neither is in Table E.1-1. In most image modules, a missing value means "may or may not contain", not "safe". See section 8 for the per-IOD rules.

### 3.5 Recording Shrub as Contributing Equipment (code 109104)
- **Standard**: PS3.3 Table C.7-1 (description of 0012,0064), §C.12.1.1.5; PS3.16 CID 7005, code 109104 "De-identifying Equipment"
- **Label**: normative (optional to use)
- **Status**: not implemented
- **Notes**: The de-identifier may add an item to Contributing Equipment Sequence (0018,A001) with Purpose of Reference 109104. PS3.3 names "software (such as a de-identification tool ...)" as equipment.

---

## 4. UIDs

### 4.1 SOP Instance UID and every reference to other instances must be replaced
- **Standard**: PS3.15 §E.1.1
- **Label**: normative
- **Status**: not implemented
- **Code**: the generated dict marks 55 tags `U` (for example `src/shrub/_phi_dict.py:563` SOP Instance UID, `src/shrub/_phi_dict.py:600` Study Instance UID)
- **Notes**: This applies whether or not the UID is nested in a Sequence. If protection is done by encryption, a SOP Instance UID nested in a Sequence means the enclosing top-level attribute is encrypted whole.

### 4.2 Consistency of replacement UIDs
- **Standard**: PS3.15 §E.1.1, §E.1.3; PS3.17 §KKK.6 (informative)
- **Label**: normative
- **Status**: not implemented
- **Notes**: The same input UID must map to the same output UID across all related instances, so references keep working. This matters most for Study Instance UID and Frame of Reference UID. How far this reaches has to be stated in the Conformance Statement. PS3.17 §KKK.6 sets the referential-integrity scope for conversions at the Patient. `TODO.md` already plans a property test for one-input-one-output UID mapping.

### 4.3 UID format for generated UIDs
- **Standard**: PS3.5 §9.1, §9.2.2, §B.2
- **Label**: normative
- **Status**: not implemented
- **Notes**: At most 64 characters, numeric components without leading zeros, separated by ".". Without an owned root, `2.25.` plus the decimal form of a UUID is the standard way to make UIDs on the fly (§B.2).

### 4.4 Original UIDs can carry information
- **Standard**: PS3.15 §E.3.9 Notes; PS3.5 §B.1
- **Label**: informative
- **Status**: not applicable
- **Notes**: Organization-derived UIDs can embed device serials, study, series and image numbers, and timestamps. Replace a UID whole, never edit part of it. Replacement UIDs can carry timestamps of their own, for example time-based UUIDs.

### 4.5 Structural UIDs are never replaced
- **Standard**: PS3.15 §E.3.9
- **Label**: normative
- **Status**: data only (Table E.1-1 doesn't list SOP Class UID or Transfer Syntax UID)
- **Notes**: "One would never remove or replace the SOP Class UID for de-identification purposes." A rule that replaces every UI value would break this. PS3.6 registers other UIDs the Standard itself defines, which must also stay unchanged: the Standard Color Palette SOP Instance UIDs (`1.2.840.10008.1.5.x`, PS3.6 Table B.1-1), Template UIDs (`1.2.840.10008.9.x`, Table A-4), Context Group UIDs (`1.2.840.10008.6.1.x`) and Transfer Syntax UIDs. A UID under the `1.2.840.10008` root never identifies a patient, so Shrub can leave every UID under that root unchanged.

### 4.6 UID pairs and groups that must stay linked
- **Standard**: PS3.3 §C.7.9.1, §C.7.4.1.1.1, §C.7.4.2.1.1, §C.8.8.5.1, §C.8.20.4.1, §C.11.22, §C.17.2.2 to C.17.2.3, §C.11.28; PS3.4 §B.4.1.3
- **Label**: normative
- **Status**: not implemented
- **Notes**: Places where one replaced UID must match another:
  - Palette Color LUT UID must equal the SOP Instance UID in a Palette Color LUT instance.
  - Frame of Reference UID is shared across Series. Synchronization Frame of Reference UID can span different Patients.
  - RT Structure Set references must match the images they point to.
  - A Tracking UID must equal the matching SR content item.
  - Presentation Display / Sequence Collection UIDs group several instances.
  - SR evidence and Identical Documents references.

  PS3.4 notes that changing UIDs breaks references and can invalidate digital signatures.

### 4.7 Retain UIDs Option
- **Standard**: PS3.15 §E.3.9; PS3.16 code 113110
- **Label**: normative
- **Status**: data only (60 tags `K`)
- **Code**: `src/shrub/tags.py:20` (`retain_uids_option`)
- **Notes**: Keeps an audit trail, but anyone with access to the originals or the PACS database can recover identity. Implementation Class UID is File Meta and is always replaced.

---

## 5. Dates and times

### 5.1 Basic Profile date handling
- **Standard**: PS3.15 Table E.1-1; §E.1.1 Notes
- **Label**: normative
- **Status**: data only
- **Notes**: 169 date and time attributes have an Option action for the longitudinal Options. The Standard suggests handling DA, DT and TM by VR, so that unlisted dates are caught too.

### 5.2 Retain Longitudinal Temporal Information with Full Dates
- **Standard**: PS3.15 §E.3.6; PS3.16 code 113106
- **Label**: normative
- **Status**: data only (169 tags `K`)
- **Code**: `src/shrub/tags.py:24`; mutual exclusion with Modified Dates is enforced at `src/shrub/tags.py:119-125`

### 5.3 Retain Longitudinal Temporal Information with Modified Dates
- **Standard**: PS3.15 §E.3.6; PS3.16 code 113107
- **Label**: normative
- **Status**: data only (169 tags `C`)
- **Code**: `src/shrub/tags.py:25`
- **Notes**: Dates must be changed so they're harder to match against the originals, while both rough and fine timing relationships survive. Shifting relative to an event needs consistency: process the whole set at once, or keep a mapping database. Things to watch:
  - an acquisition that spans midnight
  - intervals the clinical data needs, such as PET injection-to-acquisition time for SUV, and DCE timing

  The method must be in the Conformance Statement. The offset and event type can be recorded in Longitudinal Temporal Offset from Event (0012,0052) and Longitudinal Temporal Event Type (0012,0053) (PS3.3 §C.7.2.3; PS3.16 CID 280, TID 1502).

### 5.4 Timezone Offset From UTC (0008,0201)
- **Standard**: PS3.3 §C.12.1.1.8, §C.12.5
- **Label**: normative
- **Status**: not implemented
- **Notes**: It applies to every DA, TM and DT value in the instance and hints at location. Any date shifting has to stay consistent with it.

---

## 6. Private attributes

### 6.1 Basic Profile removes all Private Attributes
- **Standard**: PS3.15 Table E.1-1 (row `(gggg,eeee) where gggg is odd`), §E.3.10
- **Label**: normative
- **Status**: not implemented
- **Code**: the generator drops this row (`utils/generate_phi_dict.py:256-257`)
- **Notes**: Without Retain Safe Private, every private attribute is removed (`X`). Under Retain Safe Private the row is `C`.

### 6.2 Retain Safe Private Option and Table E.3.10-1
- **Standard**: PS3.15 §E.3.10, Table E.3.10-1; PS3.16 code 113111
- **Label**: normative
- **Status**: data only
- **Code**: `src/shrub/_safe_private_dict.py` (479 entries, all matching the XML), `src/shrub/tags.py:99` (`SafePrivateTag`, `matches` at `src/shrub/tags.py:106`)
- **Notes**: Keep private attributes known to be safe, and the Private Creator elements they need. All others are removed, or handled per Deidentification Action (0008,0307) when present. "Known to be safe" can come from:
  - a SAFE block declaration
  - Nonidentifying Private Elements
  - Table E.3.10-1
  - a vendor Conformance Statement

  More rules in the same section:
  - A private SQ of unknown safety must be opened and its nested attributes handled one by one.
  - Numeric VRs are likely safe. Other string VRs are assumed unsafe, with CS as a possible exception.
  - OB bulk data is especially unsafe, because proprietary headers can hold the patient name.
  - The private attributes kept must be listed in the Conformance Statement. Vendors guarantee nothing about Table E.3.10-1.

### 6.3 Private Data Element Characteristics Sequence (0008,0300)
- **Standard**: PS3.3 §C.12.1 (Table C.12-1), §C.12.1.1.7; PS3.15 §E.3.10; PS3.2 §N.9.1.3 (informative); PS3.17 §AAAA.2.2 (example)
- **Label**: normative
- **Status**: not implemented
- **Notes**: The instance itself can declare each private block SAFE, UNSAFE or MIXED through Block Identifying Information Status (0008,0303):
  - For MIXED, Nonidentifying Private Elements (0008,0304) lists the safe elements by the low 8 bits of their tags.
  - Deidentification Action Sequence (0008,0305) pairs Identifying Private Elements (0008,0306) with a suggested action in (0008,0307). Only `D`, `Z`, `X` and `U` are allowed there ("No C (clean) action is specified").

  Blocks are named by Private Creator, not block number, because block numbers can be reassigned.

### 6.4 Finding private creators inside Sequence Items
- **Standard**: PS3.5 §7.8.1
- **Label**: normative
- **Status**: not implemented (`SafePrivateTag.matches` takes the creator as an argument, but nothing resolves it from the data yet)
- **Notes**: A private element's creator has to be read from the same Item. "Different Items may reserve the same block of Private Data Elements for different private creators."

### 6.5 Removing private blocks
- **Standard**: PS3.5 §7.8.1
- **Label**: normative
- **Status**: not implemented
- **Notes**: A whole private block can be deleted along with its Private Creator, and the other blocks don't need renumbering. Leaving an orphan creator behind is allowed but not required. Private Creator elements are LO, and groups 0001, 0003, 0005, 0007 and FFFF must not be used.

### 6.6 Standard attributes inside private Sequences
- **Standard**: PS3.5 §7.8.2
- **Label**: normative
- **Status**: not implemented
- **Notes**: Private Sequences can hold Standard elements, which can be PHI. Pixel, Waveform and Overlay Data must not be inside private Sequence Items in Standard Extended SOP Classes. PS3.15 §E.1.1 says Table E.1-1 also lists Command, Directory and File Meta elements because they "could be misused within Private Sequences".

### 6.7 Private references from other attributes
- **Standard**: PS3.3 §10.17.1.2, §C.23.4.1.1.3, §C.7.6.17.1; PS3.4 §C.3.5
- **Label**: normative
- **Status**: not implemented
- **Notes**: Selector and Hanging Protocol attributes point at private elements by a block-relative tag plus a creator string. Dimension Index Pointer (0020,9165) and Functional Group Pointer can do the same, with Dimension Index Private Creator (0020,9213) and Functional Group Private Creator (0020,9238) naming the block. Removing private blocks leaves these pointers dangling. Private attributes can also hold UIDs. PS3.4 §C.3.5 warns that "referential integrity of UIDs in Private Attributes might not be updated" by an application that doesn't understand them. A kept private attribute can therefore still carry an original UID after every standard UID has been replaced.

### 6.8 Raw Data and other opaque private payloads
- **Standard**: PS3.3 §C.19.1; PS3.17 §MM.7 (informative)
- **Label**: normative / informative
- **Status**: not implemented
- **Notes**: Raw Data stores its payload in vendor private attributes, so whether it holds PHI can only be known through Safe Private knowledge.

---

## 7. Sequences and nested copies of identifying data

### 7.1 Walk every nesting level
- **Standard**: PS3.15 §E.1; PS3.3 (many modules)
- **Label**: normative
- **Status**: not implemented (no dataset walker)
- **Code**: fixtures with nested data: `utils/generate_fixtures.py`, `tests/fixtures/basic_profile.json`, checks in `tests/test_fixtures.py:74`
- **Notes**: The Standard repeats identifying attributes inside sequences in many places. Examples found in this read:
  - Contributing Equipment Sequence (PS3.3 §C.12.1, §10.10)
  - Person Identification Macro (§10.1)
  - Content Creator / Operator Identification (§10.9.3)
  - Patient Group Macro (§C.7.1.4.1.1)
  - Patient Clinical Trial Participation Sequence (§C.2.4)
  - Treatment Machine Sequence (§C.8.8.18)
  - Inventory objects (§A.88, §C.38.1)
  - Unassigned Shared and Per-Frame Converted Attributes Sequences (0020,9170), (0020,9171) in Legacy Converted images. PS3.4 §C.3.5 says identifying attributes "such as Series Number or Series Description, will be present in the Unassigned functional groups", along with private attributes from the source images.
  - SR content trees. The PS3.16 dose report templates (TID 10011, 10013, 10022, 10041 and others) and the PS3.17 RDSR examples (§UUUU.4, §UUUU.5) put operator and physician names, device serials, calibration responsible parties and free text into content items. They also copy Study Instance UID, Study Date and Frame of Reference UID from the images (see 10).

  `TODO.md` already plans a deep-nesting fixture.

### 7.2 Original Attributes Sequence (0400,0561) and Modified Attributes Sequence (0400,0550)
- **Standard**: PS3.15 §E.1.1 Notes; PS3.3 §C.12.1.1.9, §C.12.1.1.9.1, §C.12.1.1.9.2
- **Label**: normative
- **Status**: data only (`X` at `src/shrub/_phi_dict.py:324`)
- **Notes**: "Generally needs to be removed" because it can hold plain copies of earlier values, for example names coerced on import. The other choice is to edit its contents selectively. Nonconforming Modified Attributes Sequence (0400,0551) stores bad original values as OB, where a string scan won't find them. PS3.3 says existing Items "shall be preserved" when an application coerces attributes. That is about coercion, but it conflicts with the Annex E advice, so Shrub needs a stated choice here.

### 7.3 Contributing Equipment Sequence (0018,A001)
- **Standard**: PS3.3 §C.12.1, §C.12.1.1.5; PS3.17 §VVV.1.3, §LLL.2 (informative)
- **Label**: normative
- **Status**: not implemented
- **Notes**: The Sequence itself is not in Table E.1-1, but the attributes inside it are: Institution Name, Station Name, Operators' Name, Device Serial Number and others. Handling it correctly depends on 7.1.

### 7.4 Instance Origin Status (0400,0600)
- **Standard**: PS3.3 §C.12.1.1.10; PS3.15 Table E.1-1
- **Label**: normative
- **Status**: data only (`X` at `src/shrub/_phi_dict.py:229`)

---

## 8. Pixel data and image content

### 8.1 Clean Pixel Data Option
- **Standard**: PS3.15 §E.3.1; PS3.16 code 113101
- **Label**: normative
- **Status**: not implemented
- **Notes**: Text burned into pixels that matches removed attributes must be removed. A person may need to review. The stored pixel values themselves must change; covering text with an overlay, graphic or shutter is not enough. The Option applies to top-level Pixel Data. Icon Image pixel data is removed, and Pixel Data inside private attributes is removed. Removing all burned-in text is allowed. Adds (0028,0301) = NO.

### 8.2 Clean Recognizable Visual Features Option
- **Standard**: PS3.15 §E.3.2; PS3.16 code 113102
- **Label**: normative
- **Status**: not implemented
- **Notes**: Pixel data that would let someone be recognized, including through a 3D reconstruction (head and neck CT/MR, face photos), must be removed or distorted enough. A person may need to approve. Adds (0028,0302) = NO.

### 8.3 What Burned In Annotation means, per IOD
- **Standard**: PS3.3 §C.7.6.1, §C.8.6.3, §C.8.12.4, §C.8.13.1, §C.8.15.2, §C.8.22.3, §C.8.25.14.1.1.6, §C.8.31.1, §C.24.2
- **Label**: normative
- **Status**: not implemented
- **Notes**:
  - Enhanced MR, CT, PET, XA/XRF, US, Mammography, Parametric Map and Photoacoustic allow only `NO`, so those instances should have no burned-in identity. Legacy Converted SOP Classes are the exception.
  - `NO` is about patient demographics only. Other burned-in text can be present (§C.8.25.14.1.1.6).
  - Whole Slide label and overview images can contain the specimen label, and BIA may be `NO` only if the label has no patient data (§C.8.12.4).
  - In Encapsulated Documents, identifying text inside the document counts as burned-in annotation (§C.24.2).

### 8.4 Images whose content is itself identifying
- **Standard**: PS3.3 §C.8.12.13, §C.8.30.2
- **Label**: normative
- **Status**: not implemented
- **Notes**: Dermoscopy showing fingerprints must set Recognizable Visual Features to `YES`, and Corneal Topography always sets `YES`. Removing attributes can't de-identify these.

### 8.5 Icon Image Sequence (0088,0200)
- **Standard**: PS3.15 Table E.1-1 (with Note 11), §E.1.1 Notes, §E.3.1; PS3.3 §C.7.6.1.1.6, §C.18.4; PS3.11 §A.3.3.2; PS3.17 §X.3.4 (informative)
- **Label**: normative
- **Status**: data only (`X` at `src/shrub/_phi_dict.py:217`)
- **Notes**: Clean or regenerate the icon's pixels, otherwise remove it. Icons are also copied into Image Reference Macros in SR and KO, into DICOMDIR image records (PS3.11), and into CDA reports as base64 (PS3.17).

### 8.6 Overlays and Curves
- **Standard**: PS3.15 Table E.1-1 (`60xx3000` Overlay Data, `60xx4000` Overlay Comments, `50xxxxxx` Curve Data); PS3.3 §C.9.2, §C.9.2.1.3; PS3.5 §8.1.2
- **Label**: normative; retired (overlay bits inside Pixel Data, curves)
- **Status**: data only
- **Code**: `src/shrub/_phi_dict.py:665` (`WildcardTags`), `src/shrub/tags.py:77` (`WildcardTag`)
- **Notes**: Overlay Data can hold text as a bitmap. Older files can hide overlays in the unused high bits of Pixel Data. That usage is retired but still turns up. Overlay Description and Label are free text.

### 8.7 Sensitive Content Code Sequence (0008,001D)
- **Standard**: PS3.3 §C.12.1.1.11; PS3.16 CID 900, CID 901 (code 131393 "Identifying Content"); PS3.17 chapter GGGGG (informative)
- **Label**: normative
- **Status**: not implemented
- **Notes**: Flags faces, tattoos and similar content. If Shrub sets Recognizable Visual Features, this sequence should agree with it. PS3.17 says unknown codes should "fail closed".

### 8.8 Audio and video
- **Standard**: PS3.3 §A.1.2.12, §C.7.6.5.1.3, §A.32.5.2, §A.32.9.4; PS3.16 code 109110; PS3.22 chapter 8
- **Label**: informative; normative for the Real-Time Video constraint
- **Status**: not implemented
- **Notes**: Waveforms can carry a dictated report in the physician's voice. Video can carry multiplexed audio commentary. Neither can be cleaned by editing attributes. Real-Time Video Endoscopic and Photographic IODs "shall not include audio". Voice and commentary travel in a separate audio waveform IOD (§A.34.10, §A.34.11), which needs the same handling.

### 8.9 Pixel Data padding
- **Standard**: PS3.5 §8.1.1
- **Label**: normative
- **Status**: not implemented
- **Notes**: "In no case should a sending application place private data in the padding data." Receivers "may delete the excess padding". Older files can still hide bytes after the last pixel, so Shrub can trim padding to the length that Rows, Columns, Samples per Pixel, Bits Allocated and Number of Frames call for.

### 8.10 Images converted from EXIF or TIFF
- **Standard**: PS3.17 §NNNN.1, Table NNNN-1
- **Label**: informative
- **Status**: not implemented
- **Notes**: The mapping table carries EXIF and TIFF metadata into DICOM: Artist into Operators' Name, camera owner, body, lens and camera serial numbers, GPS position and time, UserComment, HostComputer, original ImageID, MakerNote, XMP and IPTC blocks, and the embedded JPEG thumbnail. Photographs converted from cameras can therefore carry identity in places a scanner image never would.

---

## 9. Graphics and annotations (Clean Graphics Option)

- **Standard**: PS3.15 §E.3.3; PS3.16 code 113103; PS3.3 §C.10.5, §C.10.7, §C.10.10, §C.10.11, §C.11.18, §C.11.28; PS3.4 §N.2.3
- **Label**: normative
- **Status**: data only (1 standard tag plus 3 wildcard tags `C`)
- **Code**: `src/shrub/tags.py:28` (`clean_graphics_option`)
- **Notes**: Identifying text in graphics, text annotations or overlays, in images and Presentation States (not SR), must be removed. Removing all graphics and overlays is allowed. Free-text places: Unformatted Text Value (0070,0006) in Graphic Annotation, Structured Display and Waveform Annotation; Graphic Layer Description; Graphic Group Label and Description; Text Object Sequence in Volumetric Graphic Annotation.

---

## 10. Structured content (Clean Structured Content Option)

- **Standard**: PS3.15 §E.3.4, Table E.3.4-1; PS3.16 code 113104, TID 1001 to 1021, TID 1502, chapter O; PS3.3 §C.17.3.2.1
- **Label**: normative
- **Status**: not implemented. Table E.3.4-1 is not generated into any Shrub dict.
- **Notes**: SR Content Items, Acquisition Context items and Specimen Preparation items are de-identified by Concept Name code according to Table E.3.4-1. It has its own Basic and Option columns, with values X, D and X/D plus K and C under Options. Retired codes (SRT, SNM3, 99SDM) must still be recognized. The PS3.16 observation-context templates show where identity sits in an SR tree: Person Observer Name, Subject Name/ID/Birth Date, Device Observer Serial Number, Station AE Title. Many of these default to the top-level values, so the same identity appears twice. Value types TEXT, PNAME, DATE, DATETIME, TIME and UIDREF are the places to inspect. The Standard calls skipping SR cleaning "a significant risk".

---

## 11. Free-text descriptors (Clean Descriptors Option)

- **Standard**: PS3.15 §E.3.5; PS3.16 code 113105
- **Label**: normative
- **Status**: data only (141 tags `C`)
- **Code**: `src/shrub/tags.py:26`
- **Notes**: Example from the Standard: "CT chest abdomen pelvis - 55F Dr. Smith" in Study Description. The Standard suggests looking at every SH, LO, ST, LT, UT and PN value; CS, DS and IS are rarely at risk. How cleaning is done must be in the Conformance Statement. Other free-text fields the read flagged include Name to Use (0010,0012, which is LT, not PN), Image Comments, Derivation Description, Segment Description, and Barcode Value (2200,0005), which "may be the same as Patient ID".

---

## 12. Other Retain Options

### 12.1 Retain Patient Characteristics
- **Standard**: PS3.15 §E.3.7; PS3.16 code 113108
- **Label**: normative
- **Status**: data only (14 `K`, 5 `C`)
- **Code**: `src/shrub/tags.py:23`
- **Notes**: Age, sex, height, weight and similar. They are needed for SUV, DEXA and body composition. How retained values are cleaned must be documented.

### 12.2 Retain Device Identity
- **Standard**: PS3.15 §E.3.8; PS3.16 code 113109; PS3.3 §10.29, §10.36; PS3.17 §UUUU.4.3 (informative)
- **Label**: normative
- **Status**: data only (48 `K`, 11 `C`)
- **Code**: `src/shrub/tags.py:21`
- **Notes**: AE Titles are marked `C`, not `K`, because they can contain institution or person names. Device identity also appears in RDSR content items (TID 1002/1004), not only in the General Equipment Module.

### 12.3 Retain Institution Identity
- **Standard**: PS3.15 §E.3.11; PS3.16 code 113112
- **Label**: normative
- **Status**: data only (10 `K`)
- **Code**: `src/shrub/tags.py:22`

---

## 13. Encapsulated documents

- **Standard**: PS3.15 §E.1.1 Notes; PS3.3 §A.45, §A.85, §C.24.2, §C.24.2.3; PS3.17 §IIII, §RRRR (informative); PS3.20 §C.1
- **Label**: normative
- **Status**: data only (`D` at `src/shrub/_phi_dict.py:142`; the OB dummy in `src/shrub/vr_values.py:19` is `b'\x00'`)
- **Notes**: "Options for cleaning the content of the Encapsulated Document (0042,0011) Attribute are not specified by the Standard, and it is required to be replaced." Cleaning instead is optional and must be documented. PDF Title, XMP metadata and the CDA header can all hold PHI, and the Patient ID inside a CDA can differ from the DICOM one. PS3.17 shows STL and OBJ models with the MRN built into the geometry (Burned In Annotation = YES). OBJ Relative URI values keep the original filenames.

---

## 14. Digital signatures

- **Standard**: PS3.15 §E.1.1 Notes; PS3.3 §C.12.1.1.3; PS3.4 §B.4.1.3
- **Label**: normative
- **Status**: data only (`X` at `src/shrub/_phi_dict.py:125`)
- **Notes**: Digital Signatures Sequence (FFFA,FFFA) is removed, because Certificate of Signer identifies someone and de-identification breaks the signature anyway.

---

## 15. File Meta Information and preamble

- **Standard**: PS3.15 §E.1.1, §E.3.8 Notes; PS3.10 §7.1 (Table 7.1-1), §7.1.1.1, §7.5; PS3.6 chapter 7
- **Label**: normative
- **Status**: not implemented
- **Code**: test helper only, which builds File Meta for fixtures: `tests/fixture_io.py:51`
- **Notes**: "The File Meta Information including the 128 byte preamble, if present, shall be replaced with a description of the de-identifying application." The same applies to DICOM Real-Time Video meta information. Leak points:
  - Source, Sending and Receiving AE Titles (0002,0016) to (0002,0018)
  - Presentation Addresses (0002,0026) to (0002,0028), which are URIs with hostnames
  - Private Information (0002,0100/0102)
  - Implementation Class UID and Version Name

  For the preamble, PS3.10 §7.5 gives three choices: check that it is all zeroes, check for a known magic number (TIFF), or clear it whatever it holds. Whichever Shrub does must be in the Conformance Statement.

  Files retrieved over DICOMweb as `application/dicom` may keep the AE Titles and Presentation Addresses from when the server first received them (PS3.18 §8.7.3.1). Shrub has to replace their File Meta the same way it does for any other input.

---

## 16. DICOMDIR, Group 0004 and file names

- **Standard**: PS3.15 §E.1.1; PS3.10 §6.2.3.2, §7.3, §8.2, §8.6; PS3.11 §A.3.3.2, §B.3.3.2, §D.3.3.1, §H.3.3.1; PS3.12 chapter L; PS3.4 §S.1.1, §S.3.2.1.1; PS3.3 §F.3.2, §F.5, §F.6.1, §F.7
- **Label**: normative
- **Status**: not implemented
- **Notes**: "All Data Elements with a Group Number of 0004 shall be removed from any SOP Instance or DICOM File other than a DICOMDIR File." A DICOMDIR must be rebuilt from the de-identified files, or itself de-identified. Otherwise remove it. File IDs and File-set IDs may legally encode patient or study data (PS3.10 §6.2.3.2), so output file names need neutral values. Media creation services don't de-identify anything (PS3.4 §S.1.1).

  De-identifying an existing DICOMDIR means handling the following:
  - Directory records copy identifying keys from the instances. Patient's Name, Patient ID, Study Date, Study Time and Accession Number are required keys in several PS3.11 profiles.
  - Directory records can hold Icon Image Sequences (PS3.3 §F.7).
  - Private directory records and private keys (§F.6.1) can be present.
  - Free-text keys such as Document Title (§F.5.32) can be present.
  - The File-set Descriptor File is a non-DICOM file "used for user comments related to the File-set (e.g., a README file)". The Standard does not call it identifying, but it is free text that no DICOM parser reads.
  - Referenced SOP Instance UID in File must follow the UID replacement.

  Rebuilding the DICOMDIR from the de-identified files avoids all six.

---

## 17. Group Length elements

- **Standard**: PS3.5 §7.2
- **Label**: retired
- **Status**: not implemented
- **Notes**: (gggg,0000) is retired. After editing values, remove these elements or recompute them.

---

## 18. Encrypted Attributes and re-identification

- **Standard**: PS3.15 §E.1.1, §E.1.2; PS3.3 §C.12.1.1.4 (Table C.12-7)
- **Label**: normative (optional to implement)
- **Status**: not implemented
- **Notes**: The original values can be stored, encrypted, in Encrypted Attributes Sequence (0400,0500) as one item of Modified Attributes Sequence. Encryption uses RSA for key transport and AES or Triple-DES for the content. This is optional. Ad hoc recovery schemes such as hashes of Patient's Name in private elements are deprecated. The re-identifier procedure is in §E.1.2.

---

## 19. Clinical trial attributes

- **Standard**: PS3.3 §7.6, §C.7.1.3, §C.7.2.3, §C.7.3.2, §C.2.4, §C.34.4; PS3.17 chapter H (informative)
- **Label**: normative
- **Status**: data only (the 0012 group is in `src/shrub/_phi_dict.py:55-68`, `264-269`, `326`)
- **Notes**:
  - Clinical Trial Subject ID can equal Patient ID, so replacing Patient ID alone can leave the real ID behind.
  - The Consent for Clinical Trial Use Sequence purposely has no person identifier, and a WITHDRAWN consent flag has no defined automatic action.
  - The Clinical Trial modules are optional (`U`) in every IOD.
  - The usual workflow is to de-identify first, then add the trial identifiers (PS3.17 §H.1).

---

## 20. Services and other Parts

### 20.1 WADO-URI `anonymize=yes`
- **Standard**: PS3.18 §9.4.1.2.1, §9.4.2.3; PS3.2 §N.5.3.1.2
- **Label**: normative
- **Status**: not applicable (Shrub is a library, not a web service)
- **Notes**: `anonymize=yes` is defined as "Basic Profile with Clean Pixel Data Option". "If the Target Resource has not already been de-identified, the returned Instance shall have a new SOP Instance UID." This is a concrete outside definition of what "anonymized" means.

### 20.2 Thumbnails and rendered output
- **Standard**: PS3.18 §10.4.3.3.4, §8.3.5.1.1
- **Label**: normative
- **Status**: not applicable
- **Notes**: WADO-RS thumbnails must not contain patient-identifying information. The `annotation=patient` rendering parameter burns patient data into the rendered pixels.

### 20.3 Coercion on storage and in query responses
- **Standard**: PS3.4 §B.4.1.3, §C.6.4.1.4; PS3.18 §10.5.2; PS3.2 §N.5.2.5.2
- **Label**: normative / informative
- **Status**: not applicable
- **Notes**: Storage servers that coerce values record the originals in Original Attributes Sequence. A file that came through such a server can carry PHI there even if the main attributes look clean (see 7.2).

### 20.4 Inventory objects
- **Standard**: PS3.17 §YYYY.5.3, §YYYY.6.8; PS3.3 §C.38.1.4.3
- **Label**: informative
- **Status**: not implemented
- **Notes**: The Basic Profile is hard to apply to Inventory objects. The recommendation is to de-identify the repository first and then build the Inventory. Values in an Inventory override those in the stored files.

### 20.5 Audit, CDA, AIM and Real-Time Video
- **Standard**: PS3.15 §A.5 (audit "Anonymized" field, data life cycle value 7 "De-identification"); PS3.20 §C.1; PS3.21 §A.3.2.2; PS3.22 chapter 8
- **Label**: informative
- **Status**: not applicable
- **Notes**: Audit messages carry patient ID and name themselves. CDA and AIM have no way to signal de-identification. RTV metadata can carry PII.

---

## Appendix A. Where each Part contributes

| Part | Contributes to sections |
|---|---|
| PS3.1, PS3.7, PS3.8, PS3.14, PS3.19 | Nothing found, after triage and a second full read |
| PS3.2 Conformance | 1.4, 3.2, 20.1, 20.3 |
| PS3.3 Information Objects | 3, 4.6, 5.4, 6.3, 6.7, 6.8, 7, 8.3 to 8.8, 9, 10, 11, 13, 14, 16, 18, 19 |
| PS3.4 Services | 4.6, 6.7, 7.1, 9, 14, 16, 20.3 |
| PS3.5 Encoding | 4.3, 4.4, 6.4 to 6.6, 8.6, 8.9, 17 |
| PS3.6 Data Dictionary | 1.3, 4.5, 15, 16 (tag registry; also the source of `_dicom_dict.py`) |
| PS3.10 File Format | 15, 16 |
| PS3.11, PS3.12 Media | 8.5, 16 |
| PS3.15 Security Profiles | 1, 2, 3, 4, 5, 6, 8, 9 to 14, 15, 16, 18, 20.5 |
| PS3.16 Content Mapping | 3.2, 3.5, 5.3, 7.1, 8.7, 8.8, 10 |
| PS3.17 Explanatory | 3.2, 4.2, 7.1, 7.3, 8.5, 8.7, 8.10, 10, 13, 19, 20.4 |
| PS3.18 Web Services | 1.6, 15, 20.1 to 20.3 |
| PS3.20, PS3.21, PS3.22 | 8.8, 13, 20.5 |

## Appendix B. Small issues found along the way

These are small issues noticed during the read. None of them has been fixed.

- **Standard typo**: PS3.2 Table N.5-13 gives the Original Attributes Sequence as `(0040,0561)`. The correct tag is `(0400,0561)`, which is what PS3.3 and PS3.6 use.
- **Generated name has a note marker**: `src/shrub/_phi_dict.py:217` keeps `"Icon Image Sequence (see Note 11)"` as the name. It is the only name in the dict with a note marker, and it comes from the XML cell.
- **ActionCode signatures**: `apply` passes `(dataset, tag, vr)` (`src/shrub/action_codes.py:24`), but `_keep`, `_clean` and `_replace_uid` take two arguments (`action_codes.py:35`, `:39`, `:42`). `K` would raise `TypeError` before its stub runs.
- **`drop_tags_with_keeps` never drops anything**: `src/shrub/tags.py:173` compares an `ActionCode` object to the string `"K"`, so the comparison is always False.
- **`WildcardTag.action` is a string**: `src/shrub/tags.py:82` doesn't wrap it in `ActionCode`, so `get_action().as_str()` in `get_all_actions` (`tags.py:151`) would fail for wildcard tags.

## How this list was made

- **Source**: DocBook XML for all 20 active Parts (PS3.1 to PS3.8, PS3.10 to PS3.12, PS3.14 to PS3.22), downloaded from `dicom.nema.org/medical/dicom/current/source/docbook/` on 2026-11-19. All 20 report edition 2026d in their `<subtitle>`. The XML was kept outside the repo.
- **Coverage**: the full text is about 2.74 million words. It was read in two passes. The first pass read the relevant parts closely:
  1. Every section heading and table caption in all Parts (about 101k words) was triaged for relevance.
  2. A keyword search added sections that mention de-identification terms.
  3. Very large tables (the PS3.6 registry, the PS3.16 DCM code table) contribute only the rows that matched a keyword.
  4. Sections over 1,500 words outside PS3.15 contribute their prose plus matching table rows only.

  About 264k words were read in full this way.

  A second pass then read everything the first pass skipped, in 102 chunks of 1,000 to 4,300 lines. That covered all 20 Parts, including the PS3.6 registry, PS3.3 module tables and PS3.16 code tables. Every reader reported reaching the last line of its chunk. One PS3.14 reader skipped 250 lines, which a script confirmed are display calibration numbers. The second pass found 149 candidate findings. Most were marginal or repeated the first pass. The ones added here are in 1.3, 1.4, 4.5, 6.7, 7.1, 8.8 to 8.10, 15 and 16.
- **Checks**:
  - Every quote in the first-pass reports (218 findings) was confirmed to appear word for word in the converted text. In the second pass, 148 of 149 quotes matched by script. The remaining one joins two separate quotes, and both were confirmed by hand in PS3.12.
  - The 220 tags in 1.3 come from comparing reader-cited PS3.6 tags against `BasicProfileTags` by script. Their categories in `UNLISTED.md` were assigned by hand.
  - Table E.1-1 and Table E.3.10-1 were compared row by row against `_phi_dict.py` and `_safe_private_dict.py` by a script independent of the generator.
  - The action legend, CID 7050, Deidentification Action values and Instance Origin Status were re-checked by hand against the source text.
