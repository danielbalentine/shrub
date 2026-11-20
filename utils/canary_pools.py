"""
Realistic building blocks for canary values in the generated test fixtures.

generate_fixtures.py draws from these pools with a fixed seed to give every
PHI tag a unique, realistic value. All institutions, towns and domains here
are invented. Names are common surnames and given names paired at random,
so no value describes a real person.

Grow a pool if generate_fixtures.py reports that it ran out of unique
values for a category.
"""

SURNAMES = [
    "HOLLOWAY", "OKAFOR", "NAKAMURA", "BRENNAN", "SANTOS", "LINDQVIST",
    "MBEKI", "CASTELLANO", "WHITFORD", "ABERNATHY", "KOWALSKI", "DESAI",
    "FAIRCLOUGH", "ODUYA", "MARCHETTI", "HALVORSEN", "PEMBERTON", "QUINTERO",
    "VASQUEZ", "THORNBURY", "ADEYEMI", "ROSSITER", "KILBRIDE", "TANAKA",
    "VOLKOV", "ELLSWORTH", "GALLAGHER", "NWOSU", "PRZYBYLSKI", "DUBOIS",
    "HARGREAVES", "IBARRA", "LACHANCE", "MORCOMBE", "OYELARAN", "STRAND",
]

GIVEN_NAMES = [
    "MARGARET", "DANIEL", "PRIYA", "TOMASZ", "ADAEZE", "HENRIK", "LUCIA",
    "OWEN", "FATIMA", "GRAHAM", "INGRID", "KWAME", "ROSALIND", "MATEO",
    "YUKI", "BEATRIZ", "CORMAC", "ELODIE", "FARID", "HARRIET", "IKECHUKWU",
    "JOSEFINA", "LEOPOLD", "MAEVE", "NIKOLAI", "OLUWASEUN", "PETRA",
    "RAFAEL", "SIOBHAN", "THEODORE", "ULLA", "VIKRAM", "WINIFRED", "ZOFIA",
]

MIDDLE_NAMES = [
    "ANNE", "JAMES", "ROSE", "LEE", "MARIE", "JOHN", "GRACE", "PAUL",
    "JUNE", "RAY", "LOUISE", "DEAN",
]

# Invented institutions. Do not replace these with real hospital names.
INSTITUTIONS = [
    "HOLLOW CREEK REGIONAL MEDICAL CENTER",
    "BRANNOCK VALLEY HOSPITAL",
    "ST. ODILE COMMUNITY HOSPITAL",
    "WEXLEY FALLS IMAGING ASSOCIATES",
    "NORTH TARRANT CHILDRENS HOSPITAL",
    "CALDER RIDGE UNIVERSITY HEALTH",
    "PINEMOOR VETERANS CLINIC",
    "ASHGROVE CANCER INSTITUTE",
]

# Short codes for AE titles and station names, at most 8 characters each.
SITE_CODES = ["HCRMC", "BVH", "SOCH", "WFIA", "NTCH", "CRUH", "PVC", "ACI"]

DEPARTMENTS = [
    "NEURORADIOLOGY", "CARDIOLOGY", "EMERGENCY DEPT", "ONCOLOGY",
    "PEDIATRIC IMAGING", "NUCLEAR MEDICINE", "INTERVENTIONAL RADIOLOGY",
    "MUSCULOSKELETAL", "BREAST IMAGING", "RADIATION ONCOLOGY",
]

TOWNS = [
    "HOLLOW CREEK", "BRANNOCK", "WEXLEY FALLS", "CALDER RIDGE", "PINEMOOR",
    "ASHGROVE", "NORTH TARRANT", "ODILE",
]

STREETS = [
    "MAPLE ST", "HARBOR RD", "LINDEN AVE", "QUARRY LN", "ORCHARD WAY",
    "BIRCH CT", "MILL RACE RD", "COPPER HILL DR", "WILLOW BEND",
]

# Two-letter regions and ZIP-shaped codes are invented to match the towns.
REGIONS = ["NV", "OR", "VT", "ME", "MT", "ND"]

OCCUPATIONS = [
    "TEACHER", "ELECTRICIAN", "NURSE", "FARMER", "ACCOUNTANT", "WELDER",
    "PHARMACIST", "BUS DRIVER", "CHEF", "ENGINEER",
]

# Free-text clinical phrases for descriptions, comments and notes.
CLINICAL_PHRASES = [
    "FOLLOW UP MRI BRAIN W WO CONTRAST",
    "PT CLAUSTROPHOBIC SEDATED PER DR REQUEST",
    "R/O PULMONARY EMBOLISM",
    "POST OP LEFT KNEE ARTHROPLASTY",
    "HX OF FALL AT HOME LAST TUESDAY",
    "STAGING CT CHEST ABD PELVIS",
    "PATIENT ARRIVED FROM ER BY WHEELCHAIR",
    "CHRONIC HEADACHES SINCE MVA",
    "COMPARE WITH PRIOR OUTSIDE STUDY",
    "SCREENING MAMMOGRAM ANNUAL",
    "RIGHT SHOULDER PAIN AFTER LIFTING",
    "PREGNANCY TEST NEGATIVE CONFIRMED BY NURSE",
    "CONTRAST ALLERGY PREMEDICATED",
    "TRANSFERRED FROM OUTSIDE FACILITY",
    "REPEAT SCAN DUE TO MOTION",
    "RESEARCH PROTOCOL ENROLLMENT VISIT",
]

# Short labels for SH tags such as labels and procedure names.
SHORT_LABELS = [
    "HEAD ROUTINE", "CHEST PE", "ABD PELVIS", "KNEE LT", "SHOULDER RT",
    "SPINE LUMB", "CARDIAC CTA", "BRAIN PERF", "BREAST BIL", "NECK SOFT",
]

ETHNIC_GROUPS = [
    "HISPANIC", "NOT HISPANIC", "ASIAN", "PACIFIC ISLANDER", "MAORI",
    "ASHKENAZI", "ROMANI", "SAMI",
]

# Text placed inside binary (OB, OW, UN) values, so a leak stays readable
# when the bytes are dumped.
BINARY_TEXTS = [
    "VENDOR MAKERNOTE SERIAL", "GPS FIX BY CELL TOWER", "SIGNED BY",
    "SCANNED REQUISITION FORM FOR", "CERTIFICATE ISSUED TO",
    "DEVICE SETTINGS PROFILE OF",
]
