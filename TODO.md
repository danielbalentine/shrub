# let's also add keyword from part06.xml, I guess keyword and name are different (says docstring in pydicom generate_dicom_dict.py)

# when mode is "retain_longitudinal_temporal_information_with_full_dates_option"  The Attribute​
# Longitudinal Temporal Information Modified (0028,0303) shall be added to the Data Set with a Value of "UNMODIFIED".
# The Attribute Longitudinal Temporal Information Modified (0028,0303) shall be added to the Data Set with a Value of "MODIFIED" (this is where you would apply Jitter)

# look into the diffusion tags in our internal data docs, see if they are always covered by what is in safe private
# Deferred from the basic_profile fixture work (2026-11-19)

# Shrub entry point. Write the top-level function that walks a dataset and applies each tag's action. The integration tests below need it.

# basic_profile integration test. Run tests/fixtures/basic_profile.json through the entry point. Check each tag against _phi_dict.py, and require compound codes to resolve to chain[0]. Check that no canary in basic_profile.canaries.json survives. Decide how to search for canaries first: walk the dataset with pydicom, or search the raw .dcm bytes.

# Deep nesting fixture. Use several items per sequence and sequences inside sequences. basic_profile.json stops at one item with one child.

# Random DICOM generator. Build random datasets from PS3.5 rules: VR formats, value multiplicity, private block reservation, and nesting. Public tags that Table E.1-1 does not list pass through unchanged (decided 2026-11-20, see FEATURES.md 1.3), so tests can expect them untouched.

# Property-based tests with hypothesis. These need the random generator. Candidate properties: no canary survives, running shrub twice changes nothing, and one input UID always maps to one output UID.
