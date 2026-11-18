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

