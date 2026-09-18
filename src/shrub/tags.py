from pydicom.tag import BaseTag, Tag
import re
from typing import Dict
from src.shrub._dicom_dict import DicomDictionary
from src.shrub.action_codes import ActionCode

"""REG MODES


When the Retain Longitudinal Temporal Information With Full Dates Option is specified in addition to the Basic Application Level​
Confidentiality Profile, any dates and times present in the Attributes shall be retained, as described in Table E.1-1. The Attribute​
Longitudinal Temporal Information Modified (0028,0303) shall be added to the Data Set with a Value of "UNMODIFIED".


"""


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

PROFILE_COLUMNS = [
    "name",
    "retd",
    "std_comp_iod",
    "basic_profile",
    "rtn_safe_priv",
    "rtn_uids",
    "rtn_dev_id",
    "rtn_inst_id",
    "rtn_pat_chars",
    "rtn_long_full_dates",
    "rtn_long_modif_dates",
    "clean_desc",
    "clean_struct_cont",
    "clean_graph",
]


class StandardTag:
    def __init__(self, key: int, value: tuple):
        self.tag = Tag(key)
        self.vr = DicomDictionary[key][0]
        item = dict(zip(PROFILE_COLUMNS, value))
        self.name = item["name"]
        self.action = ActionCode(item["basic_profile"])
        self.modes = self.parse_modes(item)

    def parse_modes(self, item: dict) -> dict:
        modes = {mode: item.get(mode) for mode in MODE_NAMES.values() if item.get(mode)}
        return modes

    def as_dict(self):
        d = self.__dict__.copy()
        d["tag"] = str(self.tag).replace(",", "").replace("(", "").replace(")", "")
        return d

    def matches(self, tag: Tag) -> bool:
        return self.tag == tag

    def get_action(self):
        return self.action

    def apply(self, dataset):
        return self.action.apply(dataset,self.tag,self.vr)


class WildcardTag(StandardTag):
    def __init__(self, key: str, value: tuple):
        self.group_mask, self.group_value, self.element = self.parse_wildcard_shape(key)
        item = dict(zip(PROFILE_COLUMNS, value))
        self.name = item["name"]
        self.action = item["basic_profile"]
        self.modes = self.parse_modes(item)

    def parse_wildcard_shape(self, key: str) -> tuple[int, int, int | None]:
        group_str, element_str = key[:4], key[4:]
        group_mask = int("".join("0" if c == "x" else "F" for c in group_str), 16)
        group_value = int(group_str.replace("x", "0"), 16)
        element = None if element_str == "xxxx" else int(element_str, 16)
        return group_mask, group_value, element

    def matches(self, tag: Tag) -> bool:
        group_matches = (tag.group & self.group_mask) == self.group_value
        if not group_matches:
            return False
        return self.element is None or tag.element == self.element


class SafePrivateTag:
    def __init__(self, key: tuple, value: tuple):
        tag_str, self.private_creator = key
        self.group = int(tag_str[:4], 16)
        self.element_low = int(tag_str[6:8], 16)
        self.vr, self.vm, self.meaning = value

    def matches(self, tag: Tag, private_creator: str) -> bool:
        return (
            tag.group == self.group
            and (tag.element & 0xFF) == self.element_low
            and private_creator == self.private_creator
        )


class TagList:
    def __init__(self, modes: list= []):
        self.enabled_modes = [MODE_NAMES[mode] for mode in modes]

        # guard statement for incompatable modes
        if (
            "rtn_long_full_dates" in self.enabled_modes
            and "rtn_long_modif_dates" in self.enabled_modes
        ):
            raise ValueError(
                f"Cannot call modes rtn_long_full_dates & rtn_long_modif_dates, mutually exclusive"
            )

        self.all_tags = []
        self.standard = []
        self.wildcard = []

    def add_tag(self, tag):
        matched = [tag.modes[mode] for mode in self.enabled_modes if mode in tag.modes]

        if len(set(matched)) > 1:
            raise ValueError(f"{tag.name}: enabled modes disagree, got {matched}")

        if matched:
            tag.action = matched[0]

        tag.action_code = ActionCode(tag.action)   # built once, here, action is final

        self.all_tags.append(tag)
        if isinstance(tag, WildcardTag):
            self.wildcard.append(tag)
        else:
            self.standard.append(tag)

    def get_all_actions(self) -> dict:
        """Return all unique actions in the taglist"""
        all_actions = set()
        for tag in self.all_tags:
            all_actions.add(tag.get_action().as_str())
        return all_actions

    def get_tags_with_mode(self, mode: str) -> list:
        """Return all tags of a given mode"""
        mode_key = MODE_NAMES[mode]
        return [tag for tag in self.all_tags if mode_key in tag.modes]

    def drop_tags_with_keeps(self) -> None:
        self.all_tags = [tag for tag in self.all_tags if tag.action != "K"]
        self.standard = [tag for tag in self.standard if tag.action != "K"]
        self.wildcard = [tag for tag in self.wildcard if tag.action != "K"]

    def find_tag(self, tag: Tag):
        for standard_tag in self.standard:
            if standard_tag.matches(tag):
                return standard_tag
        for wildcard_tag in self.wildcard:
            if wildcard_tag.matches(tag):
                return wildcard_tag
        return None
