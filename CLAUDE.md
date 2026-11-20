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
4. PHI test files are initially created as JSON, after review by the director they can be exported to .dcm at runtime.
5. These test files are built with the purpose of going through integration tests
6. Canary tests need to act almost as a user...and are just using Shrub and looking for expected output (these are after you have built and deployed your service)

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

## Generator data flow
The `_*.py` dicts in `src/shrub/` are generated. Never hand-edit them. Change the generator and regenerate.

| Script | Reads (DocBook XML) | Writes | Dicts |
|---|---|---|---|
| `utils/generate_dicom_dict.py` | PS3.6 `part06.xml`: Registry of DICOM Data Elements, File Meta Elements, Directory Structuring Elements. PS3.7 `part07.xml`: Command Fields, Retired Command Fields | `_dicom_dict.py` | `DicomDictionary` (int tag keys), `RepeatersDictionary` (string keys like `"50xx0022"`) |
| `utils/generate_phi_dict.py` | PS3.15 `part15.xml`: `table_E.1-1` (per-attribute action table) | `_phi_dict.py` | `BasicProfileTags` (int tag keys), `WildcardTags` (string keys like `"50xxxxxx"`) |
| `utils/generate_phi_dict.py` | PS3.15 `part15.xml`: `table_E.3.10-1` (Retain Safe Private list) | `_safe_private_dict.py` | `SafePrivateTags` (keyed on `(tag, private_creator)`) |

- Both scripts fetch the XML from `dicom.nema.org/.../current` at run time and never save it. `--local` reads a local copy instead.
- Both read the edition from the XML `<subtitle>`, for example "DICOM PS3.6 2026d - Data Dictionary". They write it into each generated file's docstring and warn if it differs from `__dicom_version__` in `src/shrub/_version.py`. They never change `_version.py`. Bump it by hand after regenerating and passing the tests.
- Run `generate_dicom_dict.py` first, because `generate_phi_dict.py` cross-checks every `BasicProfileTags` key against `_dicom_dict.py`.
- After regenerating, run `tests/test_data_invariants.py`. It checks facts about the generated dicts that `ActionCode`, `StandardTag` and `TagList` rely on, such as the set of Basic Profile action codes.
- `tags.py` (`StandardTag`, `TagList`) and `action_codes.py` (`ActionCode`) read these dicts.
- `main.py` is a lab-internal comparison script that imports `helmer_tags.py`. Neither is part of the package.

## Commands
Development runs in the rootless podman image `localhost/shrub-dev` (stored in `~/.local/share/containers/storage`), which holds Python and `requirements-dev.txt` but no code. The repo is bind-mounted at `/shrub` on each run.

- `./utils/build.sh` builds `localhost/shrub-dev` from `Containerfile`. Rerun it only when `Containerfile` or `requirements-dev.txt` changes.
- `./utils/generate_dicts.sh` runs `generate_dicom_dict.py` and then `generate_phi_dict.py` in the container. Review the regenerated dicts with `git diff`.
- `./utils/test.sh` runs all of `tests/` in the container. It passes its arguments to pytest, for example `./utils/test.sh tests/test_data_invariants.py` or `./utils/test.sh tests/test_action_codes.py::TestActionCodes::<name> -v`.

