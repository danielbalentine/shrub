"""
Unit tests for the PS3.3 Include resolver in utils/generate_fixtures.py.

Each test builds a small DocBook document in the shape PS3.3 uses: module
tables whose first cell marks nesting with ">", and "Include Table ..."
rows that point at another table by xml:id.
"""

import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "generate_fixtures", Path(__file__).parent.parent / "utils" / "generate_fixtures.py"
)
gf = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(gf)

SEQ = 0x00400001
CHILD_A = 0x00100010
CHILD_B = 0x00100020
DEEP = 0x00100030


def attribute(name: str, tag: int) -> str:
    return f"<tr><td><para>{name}</para></td><td><para>({tag >> 16:04X},{tag & 0xFFFF:04X})</para></td></tr>"


def include(depth: int, table_id: str) -> str:
    marks = "&gt;" * depth
    return f'<tr><td><para><emphasis>{marks}Include <xref linkend="{table_id}"/></emphasis></para></td><td/></tr>'


def document(tables: dict[str, list[str]]) -> ET.Element:
    body = "".join(
        f'<table xml:id="{table_id}"><tbody>{"".join(rows)}</tbody></table>'
        for table_id, rows in tables.items()
    )
    return ET.fromstring(f'<book xmlns="http://docbook.org/ns/docbook">{body}</book>')


def children_of(tables: dict[str, list[str]]) -> set[int]:
    indexed = gf.index_tables(document(tables))
    return gf.sequence_children(indexed, {SEQ}).get(SEQ, set())


def test_direct_children():
    assert children_of({
        "table_m": [attribute("Seq", SEQ), attribute("&gt;A", CHILD_A), attribute("B", CHILD_B)],
    }) == {CHILD_A}


def test_include_one_level_shifts_depth():
    assert children_of({
        "table_m": [attribute("Seq", SEQ), include(1, "table_macro")],
        "table_macro": [attribute("A", CHILD_A), attribute("&gt;Deep", DEEP)],
    }) == {CHILD_A}


def test_include_resolves_recursively():
    assert children_of({
        "table_m": [attribute("Seq", SEQ), include(1, "table_outer")],
        "table_outer": [include(0, "table_inner")],
        "table_inner": [attribute("B", CHILD_B)],
    }) == {CHILD_B}


def test_include_cycle_terminates():
    assert children_of({
        "table_m": [attribute("Seq", SEQ), include(1, "table_x")],
        "table_x": [attribute("A", CHILD_A), include(0, "table_y")],
        "table_y": [include(0, "table_x")],
    }) == {CHILD_A}


def test_children_combine_across_tables():
    assert children_of({
        "table_m1": [attribute("Seq", SEQ), attribute("&gt;A", CHILD_A)],
        "table_m2": [attribute("Seq", SEQ), attribute("&gt;B", CHILD_B)],
    }) == {CHILD_A, CHILD_B}


def test_missing_include_target_is_skipped():
    assert children_of({
        "table_m": [attribute("Seq", SEQ), include(1, "table_gone"), attribute("&gt;A", CHILD_A)],
    }) == {CHILD_A}
