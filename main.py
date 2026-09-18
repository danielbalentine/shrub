

from pydicom.tag import Tag
from src.shrub.tags import WildcardTag,SafePrivateTag,StandardTag, TagList
from src.shrub._phi_dict import BasicProfileTags, WildcardTags
from src.shrub._dicom_dict import DicomDictionary
from pathlib import Path
import sys
import pandas as pd

from helmer_tags import (
    MARKVCID_MRI_CT_PHI_TAGS,
    MARKVCID_MRI_CT_MUST_REMOVE_TAGS,
    MARKVCID_MRI_CT_RECHECK_TAGS,
    DISCOVERY_MRI_CT_PHI_TAGS,
    DISCOVERY_MRI_CT_MUST_REMOVE_TAGS,
    DISCOVERY_MRI_CT_RECHECK_TAGS,
)


def compare_to_our_tags(taglist):
    
    in_markvcid_not_in_standard = []
    in_standard_not_in_markvcid = []
    markvcid_list = MARKVCID_MRI_CT_PHI_TAGS + MARKVCID_MRI_CT_MUST_REMOVE_TAGS

    markvcid_phi_tags = [Tag(tag) for tag in markvcid_list]
    for tag in markvcid_phi_tags:
        tag = Tag(tag)
        if taglist.find_tag(tag) == None:
            
            value = DicomDictionary.get(tag)
            if value:
                tag = [str(tag),value[2]]
            in_markvcid_not_in_standard.append(str(tag))

    for tag in taglist.standard:
        if tag.tag not in markvcid_phi_tags:
            in_standard_not_in_markvcid.append(tag.as_dict())


    df = pd.DataFrame(in_standard_not_in_markvcid)

    df.to_csv('tags_in_standard_not_markvcid.csv', index=False)

    df = pd.DataFrame(in_markvcid_not_in_standard)
    df.to_csv('tags_in_markvcid_not_in_standard.csv', index=False)


def main():


    #helmer_modes = ["retain_uids_option","retain_device_identity_option","retain_longitudinal_temporal_information_with_full_dates_option"]
    helmer_modes = ["retain_uids_option","retain_device_identity_option","retain_longitudinal_temporal_information_with_modified_dates_option"]
    taglist = TagList(helmer_modes)

    

    for key,value in BasicProfileTags.items():
        taglist.add_tag(StandardTag(key,value))

    print(taglist.get_all_actions())
    # drop all keeps for comparison
    taglist.drop_tags_with_keeps()

    compare_to_our_tags(taglist)
    




if __name__ == "__main__":
    main()