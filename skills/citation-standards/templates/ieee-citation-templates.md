# IEEE Citation Templates by Source Type

Use these templates when adding citations to the References section of an authored markdown document. The order of fields and punctuation is significant — IEEE style expects this exact form.

## Web article with named author

```
[1] J. Smith, "The Future of DCIM Monitoring," *Data Center Knowledge*, Mar. 15, 2026. [Online]. Available: https://example.com/article. Accessed: Apr. 9, 2026.
```

## Web article without named author (use organizational author)

```
[2] Data Center Knowledge, "Market Trends in Infrastructure Monitoring," Oct. 2025. [Online]. Available: https://example.com/trends. Accessed: Apr. 9, 2026.
```

## Analyst report (Gartner, Forrester, IDC, etc.)

```
[3] R. Benson and L. Torres, "Magic Quadrant for DCIM Tools," *Gartner*, Report ID G00798123, Jun. 2025. [Online]. Available: https://gartner.com/report/798123. Accessed: Apr. 9, 2026.
```

## Vendor whitepaper or technical document

```
[4] Schneider Electric, "EcoStruxure IT: Architecture Overview," White Paper WP-2025-041, 2025. [Online]. Available: https://se.com/wp041. Accessed: Apr. 9, 2026.
```

## Competitor product or pricing page

```
[5] Nlyte Software, "Nlyte DCIM Platform — Pricing," 2026. [Online]. Available: https://nlyte.com/pricing. Accessed: Apr. 9, 2026.
```

## Industry standard or specification

```
[6] ASHRAE, "Thermal Guidelines for Data Processing Environments," ASHRAE TC 9.9, 4th ed., 2015. [Online]. Available: https://ashrae.org/tc99. Accessed: Apr. 9, 2026.
```

## Internal project document (cross-reference by document ID)

```
[7] PROJECT-DOC-001, "Document Title," see path/to/document.md.
```

## Punctuation and formatting rules

- Bracketed reference number `[N]` at the start, followed by a single space
- Author name(s) in `First Initial. Last Name` form, or full organizational name
- Title in straight double quotation marks `"..."`, followed by comma
- Publication name italicized with `*...*` (rendered as italic in markdown)
- Dates as `Mon. DD, YYYY` or `Mon. YYYY` (three-letter month abbreviation, period after)
- The `[Online]. Available: ` prefix introduces every URL — this is IEEE convention for online sources
- URL is a bare URL (not a hyperlinked phrase), terminated by a period
- `Accessed: Mon. DD, YYYY.` is the final element for online sources, terminated by a period
- For analyst reports, the Report ID immediately follows the publication and precedes the date
