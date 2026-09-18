"""Unit tests for src/shrub/action_codes.py"""

from pydicom import FileDataset, Dataset, Sequence
from pydicom.tag import Tag
from pydicom.dataelem import DataElement
from src.shrub.action_codes import ActionCode
from src.shrub._phi_dict import BasicProfileTags
from src.shrub._dicom_dict import DicomDictionary
from src.shrub.tags import StandardTag, TagList
from tests.vr_test_values import VR_TEST_VALUES
from src.shrub.vr_values import VR_DUMMY_VALUES, VR_EMPTY_VALUES

ACCESSION_NUMBER = Tag(0x00080050)
REFERENCED_PATIENT_SEQUENCE = Tag(0x00081120)

class TestActionCodes:

    def setup_method(self) -> None:
        pass

    #########
    # HELPERS
    #########

    def create_dicom_file(self, tags: list) -> FileDataset:
        """Create a pydicom FileDataset given a list of tags, populated with
        VR-appropriate dummy PHI values."""
        ds = FileDataset(None, {})
        ds.SeriesDescription = "TEST"

        for tag in tags:
            vr = DicomDictionary[tag][0]
            dummy_value = VR_TEST_VALUES.get(vr)
            ds.add_new(
                tag, vr, dummy_value
            )  # equivalent to ds[tag] = DataElement(tag, vr, dummy_value)

        return ds

    #########
    # TESTS
    #########

    def test_replace_empty(self):
        """Test ActionCode.replace_empty
        ActionCode "Z"
        """

        ds = self.create_dicom_file([ACCESSION_NUMBER])

        standard_tag = StandardTag(ACCESSION_NUMBER, BasicProfileTags[ACCESSION_NUMBER])

        # set action to replace empty
        standard_tag.action = ActionCode("Z")

        standard_tag.apply(ds)

        target_vr = DicomDictionary[ACCESSION_NUMBER][0]
        target_value = VR_EMPTY_VALUES.get(target_vr)
        assert ds[ACCESSION_NUMBER].value == target_value
        assert ds[ACCESSION_NUMBER].VR == target_vr

        print(ds)

    def test_replace_dummy(self):
        """Test ActionCode.replace_dummy
        ActionCode "D"
        """

        ds = self.create_dicom_file([ACCESSION_NUMBER])

        standard_tag = StandardTag(ACCESSION_NUMBER, BasicProfileTags[ACCESSION_NUMBER])

        # set action to replace dummy
        standard_tag.action = ActionCode("D")

        standard_tag.apply(ds)

        target_vr = DicomDictionary[ACCESSION_NUMBER][0]
        target_value = VR_DUMMY_VALUES.get(target_vr)
        assert ds[ACCESSION_NUMBER].value == target_value
        assert ds[ACCESSION_NUMBER].VR == target_vr

        print(ds)

    def test_remove(self):
        """Test ActionCode.replace_dummy
        ActionCode "X"
        """

        ds = self.create_dicom_file([ACCESSION_NUMBER])

        standard_tag = StandardTag(ACCESSION_NUMBER, BasicProfileTags[ACCESSION_NUMBER])

        # set action to remove
        standard_tag.action = ActionCode("X")

        standard_tag.apply(ds)

        assert ACCESSION_NUMBER not in ds
        print(ds)

    def test_remove_sequence(self):
        """Test ActionCode 'X' correctly removes an SQ-VR tag and everything nested in it."""

        phi_item = Dataset()
        phi_item.PatientName = 'Doe^Jane^Marie'
        phi_item.PatientID = 'MRN00219384'
        phi_item.ReferencedSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        phi_item.ReferencedSOPInstanceUID = '1.2.826.0.1.3680043.8.498.10812349871234981234'

        ds = FileDataset(None, {})
        ds.SeriesDescription = "TEST"
        ds.add_new(REFERENCED_PATIENT_SEQUENCE, 'SQ', Sequence([phi_item]))

        print(ds)

        standard_tag = StandardTag(
            REFERENCED_PATIENT_SEQUENCE, BasicProfileTags[REFERENCED_PATIENT_SEQUENCE]
        )

        standard_tag.action = ActionCode("X")

        standard_tag.apply(ds)

        assert REFERENCED_PATIENT_SEQUENCE not in ds
