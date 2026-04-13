---
type: source
title: "Magna Content Calendar (Clean v4, XLSX)"
kind: spreadsheet
origin: reference/Magna_Content_Calendar___Clean_v4.xlsx
ingested: 2026-04-13
tags: [content-calendar, scheduling]
sources: []
corrected_by: []
---

## Status

Binary XLSX file. Not yet parsed — the spec-phase ingest does not include an xlsx reader. Phase 2 should add an xlsx → markdown converter (via `openpyxl` or similar) so the calendar feeds into `wiki/_index/` as a scheduling layer.

## Known from filename + reference

- Filename version: `v4`, suggesting active iteration.
- Correlates with the weekly rhythm grid in [[magna-content-platform]]:

```
       Mon       Tue         Wed             Thu        Fri            Sat                Sun
IG     #MagnaMondays  -     #WisdomWednesdays  -     #FounderFridays  -              #InspirationWeekends
LI        -        #ThePrinciple  -        #TheSharpTake  -        #DigitalLectures/
                                                                   #BehindTheBuild        -
```

## Open questions

- Actual dates, slugs, and status columns are unknown until parsed.
- Whether the calendar references post drafts in a Google Drive or Notion is unknown.
