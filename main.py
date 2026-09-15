
from dicom_tables import load_dicom_tables, refresh_dicom_tables

from pydicom.tag import Tag
from tags import WildcardTag,SafePrivateTag,StandardTag, TagList

from pathlib import Path
import sys

from helmer_tags import *



def compare_to_our_tags():
    
    pass

def main():

    # use refresh to pull a new version of the tables from nema
    refresh_dicom_tables()

    tables = load_dicom_tables()


    helmer_modes = ["retain_uids_option","retain_device_identity_option"]
    taglist = TagList(helmer_modes)

    basic_profile_tags = []

    for item in tables.basic_profile_tags:
        if 'x' in item['tag']:
            taglist.add_tag(WildcardTag(item))
        else:
            taglist.add_tag(StandardTag(item))

    print(taglist.get_all_actions())


    


if __name__ == "__main__":
    main()