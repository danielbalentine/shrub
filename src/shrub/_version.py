"""Shrub version and the DICOM Standard edition it implements."""

# DICOM Standard edition used for:
#   _dicom_dict.py                     (PS3.6, PS3.7)
#   _phi_dict.py, _safe_private_dict.py (PS3.15)
# The generator scripts in utils/ warn when the XML they read is a
# different edition than this.
__dicom_version__: str = "2026d"

# Shrub's release version is the DICOM edition it implements
# (Shrub 2026d implements DICOM 2026d), so the two never drift apart.
__version__: str = __dicom_version__
