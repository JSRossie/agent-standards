---
name: citation-standards
description: IEEE-with-business-extensions citation format for authored markdown documents. Use when authoring research, topic briefings, analyses, reports, or any document that makes external claims; when adding or editing citations in such documents; when reviewing a document for citation completeness; or when constructing a References section. Triggers on phrases like "add citation", "cite this", "references section", "review citations", "research document", "topic briefing", "writing a brief", and any task where external research, market data, competitive claims, or quoted facts appear in authored markdown.
---

# Citation Standards

This skill governs citations in **authored markdown documents** — research files, topic briefings, analyses, reports, memos, anything where claims need to be traceable to sources. It does not govern citation entries inside structured data files (those use a separate JSON schema).

## The non-negotiable rule

No research claim, market data point, competitive assertion, or externally sourced fact may appear in any authored document without a proper citation. Under no circumstances is uncited external research acceptable. Every web-based source must include a working hyperlink (URL).

## Citation format: IEEE with business extensions

This standard uses **IEEE citation style** extended with business-source conventions. All documents must use numbered inline references `[1]`, `[2]`, etc., with a collected References section at the end.

### Required citation elements

Every citation must include all available elements:

1. **Author(s)** — Individual name(s) as `First Initial. Last Name`, or organizational/corporate author if no individual is credited
2. **Title** — Article, report, or page title in quotation marks
3. **Publication / Publisher** — Website name, journal, analyst firm, or publishing organization in italics
4. **Date** — Publication date (month and year minimum; full date if available)
5. **URL** — Full hyperlink to the source (mandatory for all web-based sources)
6. **Access date** — Date the source was retrieved, formatted as `Accessed: Mon. DD, YYYY` (mandatory for all web sources)
7. **Report ID** — For analyst reports, include the firm's report identifier (e.g., Gartner G00XXXXXX, Forrester RES-XXXXXX, IDC #USXXXXX)

For per-source-type templates (web article with author, web article without author, analyst report, vendor whitepaper, competitor product page, industry standard, internal cross-ref) see `templates/ieee-citation-templates.md`.

## Inline citation rules

- Use numbered references `[1]` in the body text, corresponding to the References section
- Place the citation immediately after the claim it supports — `"The market will reach $5.2B by 2028 [3]."` — not at the end of a paragraph
- When multiple sources support a single claim, group them: `[3][4][7]`
- When a passage draws heavily from a single source, cite it on first reference and note the range: `[3, pp. 12–18]`
- In narrative-heavy documents (e.g., market research summaries), hyperlinked claims are acceptable as a **supplement** — not a replacement — for numbered references: `"The market is [growing at 15% CAGR](https://example.com/report) [3]."`

## Link and access date policy

Web-based sources decay over time (average URL lifespan is roughly two years), so we record the state of a source at the time of retrieval rather than trying to preserve the source itself. Two requirements apply to every external citation:

1. **URL.** The full original URL must be included.
2. **Access date.** The date the source was retrieved, formatted `Accessed: Mon. DD, YYYY`.

If a linked page later changes or disappears, the access date identifies when we saw the state we cited. Authors are free to attach additional permanence signals (archive.org snapshots, screenshots, saved PDFs) on a per-citation basis, but none are required.

Format for every external citation: `Available: [URL]. Accessed: [date].`

**Internal documents** are cross-referenced by document ID (e.g., a project's own document IDs) and require neither URL nor access date.

## References section format

Every document containing external citations must end with a **References** section. The format and required footer line are spelled out in `templates/references-section-format.md`. Key rules:

- References are numbered sequentially in the order they first appear in the document
- Do not alphabetize
- Do not reuse numbers
- If a source is removed during editing, renumber all subsequent references and update inline citations accordingly
- Every References section ends with a horizontal rule and the standard footer line (see template)

## Enforcement and compliance

- **New documents:** Full compliance required from the date these standards are adopted in a project
- **Existing documents:** Grandfathered as-is; compliance required only if the document undergoes substantial revision
- **Generated documents** (pipeline outputs from data files): Exempt
- **Review checkpoint:** When authoring or reviewing any new analysis document, verify that every factual claim sourced from external research has a corresponding numbered citation with a valid URL

## Workflow

When authoring or editing a document covered by this skill:

1. Read `templates/ieee-citation-templates.md` for the per-source-type format you need.
2. Write the citation inline at the point of the claim, numbered in order of first appearance.
3. Append a fully-formed entry to the References section.
4. Verify the section ends with the footer block from `templates/references-section-format.md`.

When reviewing an existing document:

1. Walk every external claim and confirm it carries a numbered inline reference.
2. Walk every entry in the References section and confirm it has all required elements (URL + access date for web sources).
3. Confirm numbering is sequential, no gaps, no duplicates.
4. Confirm the footer line is present.
