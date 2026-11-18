## General Overview
1. This a dicom deidentification tool based on the latest edition of the NEMA dicom standards. One of the main benefits of this tool is that it stays inline with the standard, so labs using it can say they deidentified to "DICOM 2026c". 
2. Dicom deidentification can be a very complicated and nuanced task, so the aim is to make this tool and friendly, simple, and easy to use as possible. Someone who has never deidentified data would be able to call it very simply, but an expert in the domain would also be able to fit it to their needs.

## Dummy PHI Test Files
1. A suite of 10 or so dummy dicom files (with .dcm suffix) with a mix of the following:
    a. Flat/Nested PHI Public Tags
    b. Flat/Nested PHI Public Sequences
    c. Flat/Nested PHI Private Tags and Sequences
    d. Flat/Nested Safe Private Tags and Sequences
2. These files can be built and saved as .json files. Pydicom.from_json() can be used
    to also save them as .dcm files.
3. The PHI elements will be completely dummy and made up.

### The Dicom Standard
## General Overview

Here is a link to the dicom standard: `https://www.dicomstandard.org/current`

It is managed by NEMA (National Electrical Manufacturers Association) and new versions are released several times a year. 

The standard is an extremely large amount of context. It is your job to keep the scope of this project within this context, confirming that the guidance in the standard translates correctly to Shrub. 

Please refer to STANDARD.md for more technical and specific context.

## Tracking the Standard
1. The standard is updated 4 times a year. One of the core functionalities of Shrub is that it stays up to date with the standard on release. 
2. We track the current version that Shrub is pulling from with a _version.py file. Shrub will be released as a python package, the Shrub version will directly match the dicom standard version (etc. 2026d in Dicom Standard, Shrub is 2026d). 

## Dictionary Generation
1. generate_dicom_dict.py & other generator scripts should write the version of the standard into the doc strings of the dictionary files (ex. dicom_dict.py, _phi_dict.py)

## Generator Data Flow
The `_*.py` dictionaries in `src/shrub/` are generated. Never hand-edit them; change the generator and regenerate.

| Script | Reads (DocBook XML) | Writes | Dicts |
|---|---|---|---|
| `utils/generate_dicom_dict.py` | PS3.6 `part06.xml`: Registry of DICOM Data Elements, File Meta Elements, Directory Structuring Elements. PS3.7 `part07.xml`: Command Fields, Retired Command Fields | `_dicom_dict.py` | `DicomDictionary` (int tag keys), `RepeatersDictionary` (string keys like `"50xx0022"`) |
| `utils/generate_phi_dict.py` | PS3.15 `part15.xml`: `table_E.1-1` (per-attribute action table) | `_phi_dict.py` | `BasicProfileTags` (int tag keys), `WildcardTags` (string keys like `"50xxxxxx"`) |
| `utils/generate_phi_dict.py` | PS3.15 `part15.xml`: `table_E.3.10-1` (Retain Safe Private list) | `_safe_private_dict.py` | `SafePrivateTags` (keyed on `(tag, private_creator)`) |

- Both scripts download from `dicom.nema.org/.../current` by default, or take `--local`.
- Both read the edition from the XML `<subtitle>` (e.g. "DICOM PS3.6 2026d - ..."), write it into the generated file's docstring, and warn if it differs from `__dicom_version__` in `src/shrub/_version.py`.
- Run `generate_dicom_dict.py` first: `generate_phi_dict.py` cross-checks every `BasicProfileTags` key against `_dicom_dict.py`.
- After regenerating, run `tests/test_data_invariants.py`. It checks that the shape of the standard the code depends on hasn't changed.
- Downstream: `tags.py` (`StandardTag`, `TagList`) and `action_codes.py` (`ActionCode`) consume these dicts.
- `main.py` and `helmer_tags.py` are a lab-internal comparison script, not part of the package.

## Commands
Development runs in podman containers.

- `./utils/build.sh` builds the `localhost/shrub-dev` image from `Containerfile` (Python + pinned `requirements-dev.txt`, no code). Rebuild only when those two files change.
- `./utils/generate_dicts.sh` regenerates all `src/shrub/_*.py` dicts inside the `localhost/shrub-dev` container (repo bind-mounted at `/shrub`), running `generate_dicom_dict.py` then `generate_phi_dict.py`. Review the output with `git diff`.
- `./utils/test.sh` runs all of `tests/` in the container. Arguments pass straight to pytest, e.g. `./utils/test.sh tests/test_data_invariants.py` or `./utils/test.sh tests/test_action_codes.py::TestActionCodes::<name> -v`.

