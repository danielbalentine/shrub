from pydicom.tag import Tag

MARKVCID_MRI_CT_PHI_TAGS = [
    "00080050",
    "00080081",
    "00080082",
    "00080090",
    "00080092",
    "00080094",
    "00080096",
    "00080116",
    "00081048",
    "00081050",
    "00081052",
    "00081060",
    "00081062",
    "00081072",
    "00081080",
    "00081084",
    "00081100",
    "00081111",
    "00084000",
    "00100021",
    "00100030",
    "00100032",
    "00100040",
    "00100050",
    "00100101",
    "00100102",
    "00101000",
    "00101001",
    "00101002",
    "00101005",
    "00101040",
    "00101050",
    "00101060",
    "00101080",
    "00101081",
    "00101090",
    "00102000",
    "00102110",
    "00102150",
    "00102152",
    "00102154",
    "00102160",
    "00102180",
    "001021a0",
    "001021b0",
    "001021c0",
    "001021f0",
    "00102203",
    "00102297",
    "00102299",
    "00104000",
    "0029e131",
    "00320012",
    "00321030",
    "00321032",
    "00321033",
    "00321060",
    "00321064",
    "00324000",
    "00380040",
    "00380050",
    "00380300",
    "00380400",
    "00380500",
    "00384000",
    "00400006",
    "00400007",
    "00400008",
    "00400009",
    "00400010",
    "00400275",
    "00400280",
    "004006fa",
    "00401001",
    "00401002",
    "00401005",
    "00401010",
    "00401011",
    "00401101",
    "00401102",
    "00401103",
    "00401400",
    "00402001",
    "00402008",
    "00402009",
    "00402010",
    "00402016",
    "00402017",
    "00402400",
    "00403001",
    "0040a027",
    "0040a075",
    "0040a123",
    "0040a730",
    "04000115",
    "04000120",
    "40004000",
    "40080102",
    "4008010a",
    "4008010b",
    "4008010c",
    "40080111",
    "40080202",
    "40080114",
    "40080115",
    "40080118",
    "40080119",
    "4008011a",
]

# Site will be contacted if tags are found with these values.
# Tag will also be removed and logged.
MARKVCID_MRI_CT_MUST_REMOVE_TAGS = [
    "00080050",
    "00080081",
    "00080082",
    "00080090",
    "00080092",
    "00080094",
    "00080096",
    "00080116",
    "00081048",
    "00081050",
    "00081052",
    "00081060",
    "00081062",
    "00081072",
    "00084000",
    "00100021",
    "00100030",
    "00100032",
    "00100040",
    "00100050",
    "00100101",
    "00100102",
    "00101000",
    "00101001",
    "00101002",
    "00101005",
    "00101040",
    "00101050",
    "00101060",
    "00101090",
    "00102154",
    "001021b0",
    "00102297",
    "00102299",
    "00104000",
    "0029e131",
    "00320012",
    "00321032",
    "00321033",
    "00324000",
    "00380300",
    "00380400",
    "00380500",
    "00400006",
    "00401010",
    "00401011",
    "00401101",
    "00401102",
    "00401103",
    "00402008",
    "0040a123",
    "04000115",
    "04000120",
    "40080102",
    "4008010a",
    "4008010b",
    "4008010c",
    "40080114",
    "40080118",
    "40080119",
    "4008011a",
    "40080202",
]

MARKVCID_MRI_CT_RECHECK_TAGS = [
    "00080081",  # Institution Address
    "00080090",  # Referring Physicians Name
    "00080092",  # Referring Physicians Address
    "00080094",  # Referring Physicians Telephone Numbers
    "00080116",  # Coding Scheme Responsible Organization (name of the organization responsible for the Coding Scheme)
    "00081048",  # Physicians Of Record, names of physicians who are responsible for patient care
    "00081050",  # Performing Physicians Name
    "00081060",  # Name of Physicians Reading Study
    "00081080",  # Admitting Diagnoses Description
    "00084000",  # Identifying Comments
    "00100021",  # Issuer of Patient ID
    "00100030",  # Patients Birth Date
    "00101000",  # Other Patient IDs (could possibly contain the old patient ID from site)
    "00101001",  # Other Patient Names
    "00101005",  # Patients Birthname
    "00101040",  # Patients Address
    "00101050",  # Insurance Plan Identification
    "00101060",  # Patients Mothers Birthname
    "00101080",  # Military Rank
    "00101081",  # Branch of Service
    "00101090",  # Medical Record Locator
    "00102000",  # Medical Alerts
    "00102110",  # Allergies
    "00102150",  # Country of Residence
    "00102152",  # Region of Residence
    "00102154",  # Patients Telephone Numbers
    "00102160",  # Ethnic Group
    "00102180",  # Occupation
    "001021b0",  # Additional Patient History
    "001021f0",  # Patients Religious Preferences
    "00102297",  # Responsible Person
    "00102298",  # Responsible Person Role
    "00102299",  # Responsible Organization
    "00104000",  # Patient Comments
    "00320012",  # Study ID Issuer
    "00321030",  # Reason for Study
    "00321032",  # Requesting Physician
    "00321033",  # Requesting Service
    "00321060",  # Requested Procedure Description
    "00324000",  # Study Comments
    "00380040",  # Discharge Diagnosis Description
    "00380050",  # Special Needs
    "00380300",  # Current Patient Location
    "00380400",  # PatientsInstitutionResidence
    "00380500",  # Patient State
    "00384000",  # Visit Comments
    "00400006",  # Scheduled Performing Physicians Name
    "00400010",  # Scheduled Station Name
    "00400280",  # Comments on the Performed Procedure Step
    "00401002",  # Reason for the Requested Procedure
    "00401005",  # Requested Procedure Location
    "00401010",  # Names of Intended Recipients of Results
    "00401102",  # Persons Address
    "00401103",  # Persons Telephone Numbers
    "00401400",  # Requested Procedure Comments
    "00402001",  # Reson for the Imaging Service Request
    "00402008",  # Order Entered By
    "00402009",  # Order Enterer's Location
    "00402010",  # Order Callback Phone Number
    "00402400",  # Imaging SErvice Request Comments
    "00403001",  # Confidentiality Constraint on Patient Data Description
    "0040a027",  # Verifying Organization
    "0040a075",  # Verifying Observer Name
    "0040a123",  # Persons Name
    "40004000",  # Text Comments
    "40080102",  # Interpretation Recorder
    "4008010a",  # Interpretation Transcriber
    "4008010b",  # Interpretation Text
    "4008010c",  # Interpretation Author
    "40080202",  # Interpretation ID Issuer
    "40080114",  # Physician Approving Interpretation
    "40080119",  # Distibution Name
    "4008011a",  # Distribution Address
]


DISCOVERY_MRI_CT_PHI_TAGS = [
    Tag(0x00080012),
    Tag(0x00080023),
    Tag(0x00080024),
    Tag(0x00080025),
    Tag(0x0008002A),
    Tag(0x00080050),
    Tag(0x00080081),
    Tag(0x00080082),
    Tag(0x00080090),
    Tag(0x00080092),
    Tag(0x00080094),
    Tag(0x00080096),
    Tag(0x00080116),
    Tag(0x00081048),
    Tag(0x00081050),
    Tag(0x00081052),
    Tag(0x00081060),
    Tag(0x00081062),
    Tag(0x00081072),
    Tag(0x00081080),
    Tag(0x00081084),
    Tag(0x00081100),
    Tag(0x00081111),
    Tag(0x00084000),
    Tag(0x00100021),
    Tag(0x00100030),
    Tag(0x00100032),
    Tag(0x00100040),
    Tag(0x00100050),
    Tag(0x00100101),
    Tag(0x00100102),
    Tag(0x00101000),
    Tag(0x00101001),
    Tag(0x00101002),
    Tag(0x00101005),
    Tag(0x00101040),
    Tag(0x00101050),
    Tag(0x00101060),
    Tag(0x00101080),
    Tag(0x00101081),
    Tag(0x00101090),
    Tag(0x00102000),
    Tag(0x00102110),
    Tag(0x00102150),
    Tag(0x00102152),
    Tag(0x00102154),
    Tag(0x00102160),
    Tag(0x00102180),
    Tag(0x001021A0),
    Tag(0x001021B0),
    Tag(0x001021C0),
    Tag(0x001021D0),
    Tag(0x001021F0),
    Tag(0x00102203),
    Tag(0x00102297),
    Tag(0x00102299),
    Tag(0x00104000),
    Tag(0x0029E131),
    Tag(0x00320012),
    Tag(0x00320032),
    Tag(0x00320034),
    Tag(0x00321000),
    Tag(0x00321010),
    Tag(0x00321030),
    Tag(0x00321032),
    Tag(0x00321033),
    Tag(0x00321040),
    Tag(0x00321050),
    Tag(0x00321060),
    Tag(0x00321064),
    Tag(0x00324000),
    Tag(0x00380020),
    Tag(0x00380030),
    Tag(0x00380040),
    Tag(0x00380050),
    Tag(0x00380300),
    Tag(0x00380400),
    Tag(0x00380500),
    Tag(0x00384000),
    Tag(0x00400002),
    Tag(0x00400004),
    Tag(0x00400006),
    Tag(0x00400007),
    Tag(0x00400008),
    Tag(0x00400009),
    Tag(0x00400010),
    Tag(0x00400044),
    Tag(0x00400244),
    Tag(0x00400250),
    Tag(0x00400275),
    Tag(0x00400280),
    Tag(0x004006FA),
    Tag(0x00401001),
    Tag(0x00401002),
    Tag(0x00401005),
    Tag(0x00401010),
    Tag(0x00401011),
    Tag(0x00401101),
    Tag(0x00401102),
    Tag(0x00401103),
    Tag(0x00401400),
    Tag(0x00402001),
    Tag(0x00402004),
    Tag(0x00402008),
    Tag(0x00402009),
    Tag(0x00402010),
    Tag(0x00402016),
    Tag(0x00402017),
    Tag(0x00402400),
    Tag(0x00403001),
    Tag(0x00404005),
    Tag(0x00404010),
    Tag(0x00404011),
    Tag(0x0040A027),
    Tag(0x0040A030),
    Tag(0x0040A075),
    Tag(0x0040A120),
    Tag(0x0040A121),
    Tag(0x0040A123),
    Tag(0x0040A730),
    Tag(0x04000105),
    Tag(0x04000115),
    Tag(0x04000120),
    Tag(0x21000040),
    Tag(0x30080024),
    Tag(0x30080054),
    Tag(0x30080056),
    Tag(0x30080162),
    Tag(0x30080166),
    Tag(0x30080250),
    Tag(0x300A0006),
    Tag(0x300E0004),
    Tag(0x40004000),
    Tag(0x40080100),
    Tag(0x40080102),
    Tag(0x40080108),
    Tag(0x4008010A),
    Tag(0x4008010B),
    Tag(0x4008010C),
    Tag(0x40080111),
    Tag(0x40080112),
    Tag(0x40080114),
    Tag(0x40080115),
    Tag(0x40080118),
    Tag(0x40080119),
    Tag(0x4008011A),
    Tag(0x40080202),
    Tag(0x07A31019),
    Tag(0x07A3101A),
    Tag(0x07A3101C),
    Tag(0x07A3101D),
    Tag(0x07A51000),
    Tag(0x07A51040),
]

DISCOVERY_MRI_CT_MUST_REMOVE_TAGS = [
    Tag(0x00080050),
    Tag(0x00080081),
    Tag(0x00080082),
    Tag(0x00080090),
    Tag(0x00080092),
    Tag(0x00080094),
    Tag(0x00080096),
    Tag(0x00080116),
    Tag(0x00081048),
    Tag(0x00081050),
    Tag(0x00081052),
    Tag(0x00081060),
    Tag(0x00081062),
    Tag(0x00081072),
    Tag(0x00084000),
    Tag(0x00100021),
    Tag(0x00100030),
    Tag(0x00100032),
    Tag(0x00100040),
    Tag(0x00100050),
    Tag(0x00100101),
    Tag(0x00100102),
    Tag(0x00101000),
    Tag(0x00101001),
    Tag(0x00101002),
    Tag(0x00101005),
    Tag(0x00101040),
    Tag(0x00101050),
    Tag(0x00101060),
    Tag(0x00101090),
    Tag(0x00102154),
    Tag(0x001021B0),
    Tag(0x00102297),
    Tag(0x00102299),
    Tag(0x00104000),
    # msmoy added 1/10/2023
    # Per MayoMN, this is a private tag with PHI
    Tag(0x0029E131),
    Tag(0x00320012),
    Tag(0x00321032),
    Tag(0x00321033),
    Tag(0x00324000),
    Tag(0x00380020),
    Tag(0x00380030),
    Tag(0x00380300),
    Tag(0x00380400),
    Tag(0x00380500),
    Tag(0x00400006),
    Tag(0x00401010),
    Tag(0x00401011),
    Tag(0x00401101),
    Tag(0x00401102),
    Tag(0x00401103),
    Tag(0x00402008),
    Tag(0x0040A123),
    Tag(0x04000115),
    Tag(0x04000120),
    Tag(0x40080102),
    Tag(0x4008010A),
    Tag(0x4008010B),
    Tag(0x4008010C),
    Tag(0x40080114),
    Tag(0x40080118),
    Tag(0x40080119),
    Tag(0x4008011A),
    Tag(0x40080202),
    # btl13 added 11/29/2023
    # Karl found these private tags in a UMD Tier 1 scan and that it would
    # be good practice to remove them
    Tag(0x07A31019),
    Tag(0x07A3101A),
    Tag(0x07A3101C),
    Tag(0x07A3101D),
    Tag(0x07A51000),
    Tag(0x07A51040),
]

DISCOVERY_MRI_CT_RECHECK_TAGS = [
    Tag(0x00080081),  # Institution Address
    Tag(0x00080090),  # Referring Physicians Name
    Tag(0x00080092),  # Referring Physicians Address
    Tag(0x00080094),  # Referring Physicians Telephone Numbers
    Tag(
        0x00080116
    ),  # Coding Scheme Responsible Organization (name of the organization responsible for the Coding Scheme)
    Tag(
        0x00081048
    ),  # Physicians Of Record, names of physicians who are responsible for patient care
    Tag(0x00081050),  # Performing Physicians Name
    Tag(0x00081060),  # Name of Physicians Reading Study
    Tag(0x00081080),  # Admitting Diagnoses Description
    Tag(0x00084000),  # Identifying Comments
    Tag(0x00100021),  # Issuer of Patient ID
    Tag(0x00100030),  # Patients Birth Date
    Tag(
        0x00101000
    ),  # Other Patient IDs (could possibly contain the old patient ID from site)
    Tag(0x00101001),  # Other Patient Names
    Tag(0x00101005),  # Patients Birthname
    Tag(0x00101040),  # Patients Address
    Tag(0x00101050),  # Insurance Plan Identification
    Tag(0x00101060),  # Patients Mothers Birthname
    Tag(0x00101080),  # Military Rank
    Tag(0x00101081),  # Branch of Service
    Tag(0x00101090),  # Medical Record Locator
    Tag(0x00102000),  # Medical Alerts
    Tag(0x00102110),  # Allergies
    Tag(0x00102150),  # Country of Residence
    Tag(0x00102152),  # Region of Residence
    Tag(0x00102154),  # Patients Telephone Numbers
    Tag(0x00102180),  # Occupation
    Tag(0x001021B0),  # Additional Patient History
    Tag(0x001021F0),  # Patients Religious Preferences
    Tag(0x00102297),  # Responsible Person
    Tag(0x00102298),  # Responsible Person Role
    Tag(0x00102299),  # Responsible Organization
    Tag(0x00104000),  # Patient Comments
    Tag(0x00320012),  # Study ID Issuer
    Tag(0x00321030),  # Reason for Study
    Tag(0x00321032),  # Requesting Physician
    Tag(0x00321033),  # Requesting Service
    Tag(0x00324000),  # Study Comments
    Tag(0x00380040),  # Discharge Diagnosis Description
    Tag(0x00380050),  # Special Needs
    Tag(0x00380300),  # Current Patient Location
    Tag(0x00380400),  # Patients Institution Residence
    Tag(0x00380500),  # Patient State
    Tag(0x00384000),  # Visit Comments
    Tag(0x00400006),  # Scheduled Performing Physicians Name
    Tag(0x00400010),  # Scheduled Station Name
    Tag(0x00401002),  # Reason for the Requested Procedure
    Tag(0x00401005),  # Requested Procedure Location
    Tag(0x00401010),  # Names of Intended Recipients of Results
    Tag(0x00401102),  # Persons Address
    Tag(0x00401103),  # Persons Telephone Numbers
    Tag(0x00401400),  # Requested Procedure Comments
    Tag(0x00402001),  # Reason for the Imaging Service Request
    Tag(0x00402008),  # Order Entered By
    Tag(0x00402009),  # Order Enterer's Location
    Tag(0x00402010),  # Order Callback Phone Number
    Tag(0x00402400),  # Imaging Service Request Comments
    Tag(0x00403001),  # Confidentiality Constraint on Patient Data Description
    Tag(0x0040A027),  # Verifying Organization
    Tag(0x0040A075),  # Verifying Observer Name
    Tag(0x0040A123),  # Persons Name
    Tag(0x40004000),  # Text Comments
    Tag(0x40080102),  # Interpretation Recorder
    Tag(0x4008010A),  # Interpretation Transcriber
    Tag(0x4008010B),  # Interpretation Text
    Tag(0x4008010C),  # Interpretation Author
    Tag(0x40080202),  # Interpretation ID Issuer
    Tag(0x40080114),  # Physician Approving Interpretation
    Tag(0x40080119),  # Distribution Name
    Tag(0x4008011A),  # Distribution Address
]