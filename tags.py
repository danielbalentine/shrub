from pydicom.tag import BaseTag, Tag
import re
from typing import Dict
from pydicom.datadict import dictionary_VR



# maps the DICOM standard's actual Option name (per PS3.15 section E.3) to
# the corresponding key in a row dict
MODE_NAMES = {
    "retain_safe_private_option": "rtn_safe_priv",
    "retain_uids_option": "rtn_uids",
    "retain_device_identity_option": "rtn_dev_id",
    "retain_institution_identity_option": "rtn_inst_id",
    "retain_patient_characteristics_option": "rtn_pat_chars",
    "retain_longitudinal_temporal_information_with_full_dates_option": "rtn_long_full_dates",
    "retain_longitudinal_temporal_information_with_modified_dates_option": "rtn_long_modif_dates",
    "clean_descriptors_option": "clean_desc",
    "clean_structured_content_option": "clean_struct_cont",
    "clean_graphics_option": "clean_graph",
}

class StandardTag():
    def __init__(self,item: dict):
        self.tag = self.parse_tag(item['tag'])
        self.vr = item['vr']
        print(self.vr)
        self.name = item['name']

        # action to perform for said tag, can be overwritten by mode specific action
        self.action = item['basic_profile']
        self.modes = self.parse_modes(item)
        


    def parse_tag(self,tag_str: str) -> Tag:
        group, element = tag_str.strip("()").split(",")
        return Tag(int(group, 16), int(element, 16))

    def parse_modes(self,item: dict) -> dict:
        modes = {mode: item.get(mode) for mode in MODE_NAMES.values() if item.get(mode)}
        return modes
        
    def matches(self, tag: Tag) -> bool:
        return self.tag == tag

    def get_action(self):
        return self.action


class WildcardTag(StandardTag):
    def __init__(self, item: dict):
        # skip StandardTag.__init__ entirely, self.parse_tag can't handle
        # a wildcard shape, everything below is set independently instead
        self.group_mask, self.group_value, self.element = self.parse_wildcard_shape(item['tag'])
        self.name = item['name']
        self.action = item['basic_profile']
        self.modes = self.parse_modes(item)  # reused from StandardTag, unchanged
 
    def parse_wildcard_shape(self, tag_str: str) -> tuple[int, int, int | None]:
        match = re.match(r'\(([0-9A-Fa-fx]{4}),([0-9A-Fa-fx]{4})\)', tag_str)
        group_str, element_str = match.groups()
        group_mask = int(''.join('0' if c == 'x' else 'F' for c in group_str), 16)
        group_value = int(group_str.replace('x', '0'), 16)
        element = None if element_str == 'xxxx' else int(element_str, 16)
        return group_mask, group_value, element
 
    def matches(self, tag: Tag) -> bool:
        group_matches = (tag.group & self.group_mask) == self.group_value
        if not group_matches:
            return False
        return self.element is None or tag.element == self.element
 


class SafePrivateTag:
    def __init__(self, group: int, element_low: int, row: dict):
        self.group = group
        self.element_low = element_low
        self.row = row

    @classmethod
    def from_row(cls, row: dict) -> "SafePrivateTag":
        ...

    def matches(self, tag: Tag, private_creator: str) -> bool:
        ...


class TagList:
    def __init__(self, modes: list):
        self.enabled_modes = [MODE_NAMES[mode] for mode in modes]
        self.all_tags = []
        self.standard = []
        self.wildcard = []

    def add_tag(self, tag):

        matched = [tag.modes[mode] for mode in self.enabled_modes if mode in tag.modes]

        if len(set(matched)) > 1:
            raise ValueError(f'{tag.name}: enabled modes disagree, got {matched}')

        if matched:
            tag.action = matched[0]  # overwrite directly, no separate trump_action

        if tag.action == 'K':
            return
        
        self.all_tags.append(tag)
        if isinstance(tag, WildcardTag):
            self.wildcard.append(tag)
        else:
            self.standard.append(tag)


    def get_all_actions(self) -> dict:

        all_actions = set()

        for tag in self.all_tags:
            all_actions.add(tag.get_action())

        return all_actions

    


