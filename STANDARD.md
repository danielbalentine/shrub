### General Overview
The standard is in DocBook XML, as `part05.xml` (PS3.5, data structures and encoding)
and `part15.xml` (PS3.15, security profiles, including Annex E, the de-identification profile).
Here is an example link to part05.xml: `https://dicom.nema.org/medical/dicom/current/source/docbook/part05/part05.xml`
Each file is hundreds of KB. **Never read a whole file into context.** Pull only the pieces you need.


### Where things are
- The de-identification rules are in `part15.xml`, **Annex E** (`chapter_E`):
  - `sect_E.1`: the Application Level Confidentiality Profile
  - `sect_E.2`: the Basic Profile (the "remove everything identifying" baseline)
  - `sect_E.3`: the Options, with one subsection each (`sect_E.3.1` Clean Pixel Data, and so on)
  - `table_E.1-1a`: the deidentification action codes table, keys are the deidentification codes, values are the actions they require. These actions are reflected in `src/shrub/action_codes.py`. The logic in this table should be correctly reflected by this class.
  - `table_E.1-1`: the **action table** (per-attribute actions: D, Z, X, K, C, U, and so on). This is the core data for Shrub.
  - `table_E.3.10-1`: the Retain Safe Private list
- `part05.xml` covers VRs, value encoding, transfer syntaxes, sequence and item encoding, and private elements.
  Use it when you need exact VR semantics, length rules, or how nested data sets are encoded.
- Prose and table cells cross-reference each other with `<xref linkend="...">`. Follow the `linkend`
  id to the target `xml:id`. Cross-standard references use `<olink targetdoc="PS3.x" targetptr="...">`
  and point outside these two files.

### How to read it
1. **Look things up by `xml:id` or section label, not by line number.** Elements carry stable ids
   (`sect_E.3.4`, `table_E.1-1`, `chapter_E`, `para_<uuid>`). Prefer `section[@xml:id='sect_E.3.4']`
   or `table[@xml:id='table_E.1-1']`.
2. **Extract with a tool, don't page through the file.** Use `xmllint --xpath` or Python `lxml`
   (run Python with `-I`, and pass the path as an argument). Print only the matched node's text,
   and strip the markup if you don't need it.
3. **Check a table's actual structure before writing a parser.** Look at the header row and a few body rows first.
   Confirm the column order and how rows are nested, and check for `rowspan`/`colspan` and for tag-range patterns like `(50xx,xxxx)`.
   Don't assume the layout. Print the first ~5 rows and the last 2.
4. **Searching:** to find where something is defined, grep the XML for the attribute name or tag,
   for example `grep -n "(0010,0010)" part15.xml`. Take the enclosing section id from the hit, then extract that section.
5. If the file isn't on disk, use the project's `project_search` or `project_read` for these two docs.
   Don't glob the filesystem for them.

### Rules for using what you pull
- **The table is the source of truth for per-attribute behavior.** Prose in E.2 and E.3 gives intent
  and the Option logic. If prose and `table_E.1-1` disagree, say so. Don't silently pick one.
- **Cite the source in code comments** with the section or table id and, for table rows, the tag.
  Example: `# PS3.15 E.1-1: (0008,0050) Accession Number -> Z`.
- **Options modify the Basic Profile.** Each Option changes specific rows or adds behavior
  (for example, it adds Longitudinal Temporal Information Modified (0028,0303) = "REMOVED"/"UNMODIFIED").
  Read the Option's own section and the table's per-Option columns together.
- **Don't encode actions from memory.** If you can't find a row in the table, flag it as unverified
  rather than guessing from your DICOM knowledge.
- **Generated data from the table** (an action map, for example) must come from a script
  checked into the repo that parses the XML. Don't hand-transcribe it. Record which standard
  edition/version the XML came from.
- Shrub is "best effort". The standard states that using a profile does not replace a
  de-identification process. Keep that caveat in user-facing docs.