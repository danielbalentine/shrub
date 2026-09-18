# let's also add keyword from part06.xml, I guess keyword and name are different (says docstring in pydicom generate_dicom_dict.py)

# when mode is "retain_longitudinal_temporal_information_with_full_dates_option"  The Attribute​
# Longitudinal Temporal Information Modified (0028,0303) shall be added to the Data Set with a Value of "UNMODIFIED".
# The Attribute Longitudinal Temporal Information Modified (0028,0303) shall be added to the Data Set with a Value of "MODIFIED" (this is where you would apply Jitter)

# look into the diffusion tags in our internal data docs, see if they are always covered by what is in safe private