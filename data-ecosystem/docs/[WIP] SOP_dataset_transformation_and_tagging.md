# SOP: Dataset Transformation and Tagging for FemHealth Use Cases

Version 0.1, draft for internal review 

This SOP sets out how the FemHealth Data Collaborative turns raw public data into tagged, checked datasets that support analyses for a defined use case. This SOP also describes how datasets can be published on CivicDataSpace and queried by the FemHealth query engine. 


## Stage 1: Scope the use case

A use case starts with a question that can:
- drive policy implementation,
- assist with key decisions for relevant authorities,
- provide a astarting point to examine development and health related outcomes in a specified ecosystem
This can be defined by key stakeholders, or internally to identify where there are data and infrastructural gaps that we can address.

**Steps**

1. Write the use case question in one sentence, naming the decision it informs. Example: "Where does Assam's public procurement for maternal and child health go, and does it line up with district health needs?"
2. Name the intended users from the FemHealth user groups: health officials, finance and planning officials, civil society organisations, researchers, journalists.
3. Fix the geography - what administrative level you are operating in (state, district, revenue circle), the time window, and whether calendar or fiscal years apply.
4. List candidate sources and check each against the [data registry](../knowledge_graph/data_registry.csv) before looking elsewhere.
5. Define the tags the use case needs (for example "MCH-related", scheme, department) and what would count as a wrong tag.
6. Agree the scope if the use case touches sensitive topics (mental health, violence, individual-level survey data).
7. Create the use case folder: `analytics/<Use_case_name>/`, with a `README.md` stating the question, users, geography and time window.

**Output:** use case folder with README; draft list of sources and tags.

**Done when:** the use case lead and one other team member agree the question can be answered with the listed sources.

## Stage 2: Source intake and registration

Every dataset used by a use case, including ones the team creates (such as scraped tenders), gets a row in the data registry and a folder with a README before it is transformed. Today the MCH tenders dataset has neither; that is the gap this stage closes.

**Steps**

1. Add a row to [`data-ecosystem/knowledge_graph/data_registry.csv`](../knowledge_graph/data_registry.csv). Required fields: Title, Publisher, Creator, Dataset / Source, Access URL, Theme / Category, Spatial Coverage, Spatial resolution, Temporal Coverage (start and end), Accrual Periodicity, License, Format. Leave a field blank only if the source does not state it, and say so in Comments.
2. Store raw files under `data-ecosystem/sources/<publisher_folder>/<dataset_folder>/`:
    - publisher folder = publisher name in lower snake case with its acronym, e.g. `ministry_of_health_and_family_welfare_mohfw`
    - dataset folder = dataset name in lower snake case with its acronym, e.g. `national_family_health_survey_5_district_factsheets`
    - data the team generates (scrapes, surveys) sits in the use case folder under `analytics/`, and its registry row says so
3. Keep the raw file exactly as downloaded. Never edit it by hand; every change happens in a script (Stage 3).
4. Write the dataset folder README using the template in Appendix B: what the file is, registry metadata, contents by sheet or column group, and anything done to it (for example "filtered to Assam districts").
5. Record the licence. Government data is usually under the [Government Open Data License – India](https://data.gov.in/government-open-data-license-india); team-created datasets published on DataSpace use CC BY-SA 4.0. If the licence is unclear, do not publish until it is resolved.
6. Update the publisher table in [`data-ecosystem/sources/README.md`](../sources/README.md).
7. Do not record personal information about the people who did the work (the registry's Assignee column stays out of READMEs).

**Output:** registry row, source folder, README.

**Done when:** someone outside the team could find the original source again from the README alone.

## Stage 3: Transformation

Transformation turns a raw file into one tidy, typed table per use case question, produced by a script anyone on the team can re-run. The standards below apply to every published table.

**Table standards**

| Element | Standard | Example |
| --- | --- | --- |
| Grain | One row = one clearly stated thing; state it in the README | one tender; one district-year |
| Primary key | One unique ID column, checked for duplicates | `tender_id` |
| Column names | lower snake case, no spaces or symbols | `Tender Value in ₹` → `tender_value_inr` |
| Money | Numbers in rupees, suffix `_inr`; never lakh or crore in the data | `2,06,34,54,000` → `2063454000` |
| Dates | ISO 8601 (`YYYY-MM-DD`); add `_fiscal_year` (`2023-24`, April to March) where government readers will ask for it | `07-Mar-2019` → `2019-03-07` |
| Booleans | `true` / `false`, named `is_` or `has_` | `is_awarded` |
| Missing values | Empty cell. Codes such as `NA`, `CONFLICT` or `-` become empty plus a separate status column | `district_geotag_status` |
| Districts | Upper case, spelled as `dtname` in the current boundary file | `SIVSAGAR` → `SIVASAGAR` |
| Multi-value fields | Separator `;`, plus a long-format version (one row per value) for counting | scheme tags |
| Units | Unit in the column name or the profile, never only in a header note | `days_publish_to_contract` |

**Script standards**

1. One script per step (scrape, clean, tag, geotag), in `analytics/<Use_case>/<dataset>/scripts/` or the source folder's `scripts/`.
2. Input and output paths are arguments or set at the top of the script, not built from the current working directory.
3. Scripts are deterministic: the same input gives the same output.
4. Each script prints row counts in and out, and how many rows each filter dropped.
5. Comments and names describe this use case. Code copied from another project (for example the flood tender pipeline) is renamed and cleaned before it is committed.
6. Keep only the final published file and the scripts that make it in the main `data/` folder; move superseded files to `data/archive/` with a one-line note on what replaced them.
7. Raw scraped or downloaded files that are large or regenerated monthly are versioned with DVC (already in the project's requirements), not committed as plain files.

**Output:** published table(s) and the scripts that produce them.

**Done when:** a second team member re-runs the scripts from a clean checkout and gets an identical file.

## Stage 4: Tagging

Tags decide which records belong to a use case and how they are grouped, so a wrong tag changes every number downstream. Each tag therefore has a written definition, a single keyword source, a decision rule, and a measured error rate before it is published.

**Kinds of tag**

| Kind | Question it answers | Example (MCH tenders) |
| --- | --- | --- |
| Inclusion tag | Does this record belong to the use case? | `is_mch_strict`, `is_mch_broad` |
| Category tag | Which programme or theme does it fall under? (can be several) | scheme: `NHM`, `LAQSHYA`, `JSSK` |
| Organisation tag | Who issued or funds it? | department, `is_btc` |
| Status tag | What happened to it? | `is_awarded` |
| Data quality flag | Can its values be trusted? | `awarded_value_suspect` |

**Steps**

1. **Define each tag in one sentence**, including what it excludes. Example: "MCH-related: the tender buys works, goods or services mainly for pregnant women, mothers, newborns or children under 18; veterinary and animal husbandry tenders are excluded."
2. **Keep one keyword list per tag family**, in one machine-readable file (`tagging/keywords.yaml` in the use case folder). Scripts read it; nobody copies keywords into code. Each entry carries the tag, the keyword, the match type (whole word for acronyms of 4 letters or fewer, phrase otherwise), and a note on why it is there.
3. **Write the decision rule** in plain words next to the code: which fields are searched, what counts as a strong signal, what vetoes a match. Example: a core MCH, antenatal or immunisation term is enough on its own; a scheme name alone needs a health-facility word as well; any veterinary term vetoes.
4. **Separate departments from schemes.** A tag that marks who issued a record (H&FW, PWD) is an organisation tag, not a scheme tag, even if both come out of the same matcher.
5. **Check for collisions before running.** Test every short acronym against the organisation names in the data. `CHD` matched the office "Director Cum CHD - PWD BTC" and tagged 6 civil works tenders as the Congenital Heart Disease scheme.
6. **Run, then review by hand** (the reviewer, not the author), using the review sheet in Appendix D:
    - a random sample of 20 tagged records (or all, if fewer than 40) for false positives
    - a random sample of 20 untagged records from the wider pool for misses, chosen from those with any health word
    - every category tag with fewer than 10 records, in full
    - every value of every tag, to catch tags that match too much (generic phrases such as "labour room strengthening" put 28 tenders under LAQSHYA)
7. **Record the result**: precision on the sample (correct tagged ÷ tagged reviewed) and the misses found. Below 90% precision, fix the keywords or rule and repeat.
8. **Keep the audit trail.** Store which keywords matched for each record (as the MCH pipeline does in `positive_keywords_dict`) so any tag can be explained, but leave it out of the published analysis view.
9. **Version the tag set.** A change to keywords or rules bumps the tag version in the use case README and triggers Stage 6 checks and Stage 10 regeneration.

**Output:** tagged table, keyword file, decision rules, review sheet with precision.

**Done when:** every tag has a definition, a rule, and a review at or above 90% precision, and known residual errors are written down.

## Stage 5: Geotagging

When a source does not report a district, the team infers one from place names in the text, and every inferred district carries a status saying how it was reached. The target is at least 85% of records placed with no conflict; the MCH tenders reach 86% (96 of 112).

**Reference data** (in [`data-ecosystem/maps/`](../maps/))

| File | Use |
| --- | --- |
| `Geojson/assam_district_2024-11.geojson` | District boundaries and the canonical district spelling (`dtname`, 35 districts) |
| `Geojson/assam_rc_2024-11.geojson`, `assam_rc_2025-04.geojson` | Revenue circle boundaries; naming indicates the version date |
| `Extra/ASSAM_VILLAGES_RC_DISTRICT_MAPPING.csv` | Village, block, sub-district and revenue circle to district lookup |

**Steps**

1. Use the source's own district field when it has one; only infer when it does not.
2. Search fields in a fixed order, from most to least reliable, and keep each result in its own column. For tenders: reference number, then title and description, then the location field.
3. Match place names at each level (revenue circle, sub-district, block, village) only where the name is unique in the lookup; names shared by two districts are not used.
4. Keep a short, reviewed list of manual additions for names missing from the lookup, in a file next to the script, each with a source.
5. Combine: one district from all columns = that district; none = `not_geotagged`; more than one = `conflict`. 
6. Normalise spellings to the boundary file (`SIVSAGAR` → `SIVASAGAR`). Note districts created after the source period (Bajali, Tamulpur) and which parent district older records may sit under.
7. Hand-check all conflicts and a sample of 10 placed records. Fix the lookup where a pattern is wrong; resolve individual conflicts by hand only with a written note.
8. Report the result in the use case README: placed, not geotagged, conflict, and districts with no records.

**Output:** `district` and `district_geotag_status` columns; geotagging report.

**Done when:** the placed share is at or above 85%, every conflict has been looked at, and district names match the boundary file exactly.

## Stage 6: Quality checks before publishing

TBA

**Rules**

- A check that fails either gets fixed in the script, or gets a documented flag column and a written caveat. It is never fixed by editing the output file.
- Checks 1 to 9 are scripted (`scripts/checks.py` in the use case folder) so they rerun on every update; 10 to 12 need a person.
- The reviewer signs off in the use case README with the date and the check results.

**Output:** check results recorded in the README; flag columns and caveats where needed.

**Done when:** every check has passed or has a written flag and caveat, and the reviewer has signed off.

## Stage 7: Publishing to DataSpace and Superset

A published dataset must carry enough metadata on CivicDataSpace to be found and understood without the repository, and the repository must record every ID the platform assigns. Until November 2026 the MCH use case's dataset and dashboard IDs existed only on the platform.

**Steps**

1. **Create the dataset on DataSpace** with: a title that matches the data's actual coverage (state the results period if it differs from publication dates), a description covering grain, coverage, method and main caveats, sectors, tags, geography, licence, and source.
2. **Upload resources** with descriptions. A resource made for a dashboard (such as a map layer) says so and says it is not for totals.
3. **Publish aggregates only from the main table**, using a script kept in the repository, so district-, scheme- and department-wise files always reconcile with it.
4. **Create or update the use case on DataSpace**: summary, linked datasets, sectors, SDGs, geography, start date, running status, dashboard link.
5. **Build the Superset dashboard** on the published resources, and give it a public link.
6. **Record every ID back in the repository** in the use case's `query_engine_reference/usecase.json`: DataSpace use case ID, dataset and resource IDs, dashboard name and both URLs.
7. **Check the published figures**: every number in the use case narrative and dashboard titles is recomputed from the published table (Stage 6, check 11). Narrative claims from outside the data (for example "only about 20% of Assam's tenders are published") cite their source.
8. **Keep slugs meaningful.** Platform-generated slugs such as `new-dataset-10-dec-2025-104037` should be renamed to a readable form where the platform allows.

**Output:** DataSpace dataset(s) and use case, Superset dashboard, IDs recorded in the repository.

**Done when:** a reader can go from the use case page to the data, the dashboard and the repository, and back, using links alone.

## Stage 8: Query engine reference

Each use case ships a `query_engine_reference/` folder so the FemHealth query engine can find its data, describe it, compute answers from it correctly, and be tested against it. The folder follows the structure first built for the MCH tenders use case.

| File | Purpose | Query engine component |
| --- | --- | --- |
| `README.md` | What the folder holds and how to regenerate it | Maintainers |
| `usecase.json` | Use case card: IDs, links, coverage, linked datasets, published findings with provenance, limitations, sensitivity | Semantic search, Understand mode |
| `dataset_profiles/<resource>.json` | Per resource: grain, rows, columns (type, unit, description, missing, values), coverage, quirks, file checksum | Dataset profiles, analysis planner |
| `views.sql` | Cleaned, typed DuckDB views the planner queries instead of the raw CSV | Analysis engine |
| `analysis_reference.md` | Method, metric definitions, SQL patterns, caveats every answer must state, out-of-scope questions | Planner and narrator context |
| `glossary.json` | Codes, terms, units, spelling variants, Hindi and Assamese terms | Query parsing, narration |
| `question_bank.json` | Golden questions for discover, understand, analyse and out-of-scope, with SQL, executed results and required caveats | Evaluation |
| `scripts/` | Rebuild profiles and the question bank from the data | Maintainers |

**Steps**

1. Copy the folder structure and naming rules from [`analytics/Assam_MCH_analysis/query_engine_reference/README.md`](../../analytics/Assam_MCH_analysis/query_engine_reference/README.md).
2. Fill `usecase.json` from the DataSpace record (Stage 7) and the use case README.
3. Write `views.sql` so that every flag and caveat from Stage 6 is a column the planner can filter on.
4. Generate profiles with the script; write column descriptions and quirks by hand.
5. Write at least 25 questions: 4 or more discover, 5 or more understand, 10 or more analyse, 4 or more out-of-scope. Every analyse question has SQL that has been run; its result is stored as the expected answer.
6. Add Hindi, Assamese and Hinglish variants for the most common questions, and have a native speaker review them before they count as gold.
7. Separate claims taken from the use case narrative (`published_findings`) from figures computed from data.

**Done when:** the question bank builds without errors and every caveat in Stage 6 appears in at least one question's required caveats.

## Stage 9: Responsible data use

The rules below apply at every stage, and the use case lead confirms them before publishing. They replace the current [`RESPONSIBLE_DATA_USE.md`](../../RESPONSIBLE_DATA_USE.md).

| Area | Rule |
| --- | --- |
| Personal data | Publish aggregates by district, scheme or department. Names of individuals (for example sole-proprietor contractors) may stay in record-level public data but are never ranked, profiled or highlighted. Household and person-level survey files (HCES, TUS, PLFS) are published only as aggregates. |
| Small numbers | Counts below 10 in survey-based indicators are suppressed. For administrative records such as tenders, small counts are shown but not ranked or turned into percentage changes. |
| Sensitive topics | Mental health, gender-based violence and reproductive health results are framed with care and reviewed by the UNICEF focal point before release. |
| Claims | Show associations, not causes. "Higher spending did not coincide with lower infant mortality" is fine; "spending failed to reduce infant mortality" is not. |
| Wrongdoing | Procurement patterns (single bids, rejections, delays) are reported neutrally and never presented as evidence of corruption. |
| Coverage | Every output states what the data does not cover (for example, unpublished tenders) and that absence of records is not absence of activity. |
| Attribution | Third-party data keeps its original licence and credits the original publisher, not just this repository. |
| Law | Handling complies with the Digital Personal Data Protection Act, 2023, and each source's terms of use. |

**Done when:** the use case lead has checked each row against the use case and recorded any exceptions in the README.

## Stage 10: Maintenance and updates

A use case is refreshed on the schedule its source allows, and any change to data, tags or rules reruns the checks and regenerates the query engine reference. The checksum stored in each dataset profile shows when the reference no longer matches the data.

| Trigger | What to rerun |
| --- | --- |
| New source data (e.g. a month of tenders) | Stages 3 to 8 for that dataset |
| Keyword or tag rule change | Stage 4 review, then Stages 6 to 8 |
| New boundary or lookup version | Stage 5, then Stages 6 to 8 |
| Change to the DataSpace record or dashboard | Update `usecase.json` |
| Checksum in a profile no longer matches the file | Regenerate profiles and question bank; compare results with the previous run |

**Rules**

- Set the refresh frequency in the registry's Accrual Periodicity field (for tenders: monthly scrape, quarterly republish).
- Keep a dated changelog in each use case README: what changed, why, and its effect on headline numbers.
- When headline numbers move by more than 5%, the use case lead checks the DataSpace narrative and dashboard titles and updates them.
- Review this SOP once a year, or when the query engine's needs change.

## Worked example: Assam MCH tenders

The [MCH tenders use case](https://civicdataspace.in/usecases/312) was built before this SOP and fully meets it at 2 of 10 stages and partly at 5; the table shows what is left to do. Its data: 112 MCH-related tenders from [assamtenders.gov.in](https://assamtenders.gov.in/nicgep/app), 59 awarded, worth ₹268.29 crore, with results from March 2019 to October 2025, shown on the [Superset dashboard](https://analytics.civicdataspace.in/superset/dashboard/p/xLKpnNXp6b2/).

| Stage | Status | What exists | What is left |
| --- | --- | --- | --- |
| 1. Scope | Partly | Question and findings on the DataSpace page; TENDERS README | Use case README with users, geography and time window |
| 2. Source intake | Not yet | Scraper README, source portal named | Registry row; licence recorded in the repository |
| 3. Transformation | Partly | Scripts for scraping, tagging and geotagging | Paths built from the working directory; raw headers kept; "flood" wording in comments; README lists a missing `geocode_rc.py` |
| 4. Tagging | Partly | Written keyword logic; keyword audit columns | Two keyword lists that differ; no review sample or precision; CHD and LAQSHYA over-matching |
| 5. Geotagging | Meets SOP | 3-source method with conflict status; 86% placed | Conflicts not hand-checked; `SIVSAGAR` spelling in the published file |
| 6. Quality checks | Partly | Checks run once in November 2026; flags added to the query view | Not scripted; placeholder values still in the published file |
| 7. Publishing | Partly | DataSpace dataset, 4 linked datasets, use case, dashboard; IDs now in `usecase.json` | Aggregates not reproducible from the repository; map file incomplete; generated slugs |
| 8. Query engine reference | Meets SOP | Full [`query_engine_reference/`](../../analytics/Assam_MCH_analysis/query_engine_reference/) folder, 30 tested questions | Native-speaker review of language variants |
| 9. Responsible use | Not yet | Sensitivity notes in `usecase.json` | Repository-level policy still describes a flood model |
| 10. Maintenance | Not yet | Checksums and regeneration scripts | No changelog; no refresh schedule in the registry |

## Appendix A: Naming conventions

| Item | Convention | Example |
| --- | --- | --- |
| Use case folder | `analytics/<Place>_<Theme>_analysis/` | `Assam_MCH_analysis` |
| Source publisher folder | lower snake case + acronym | `ministry_of_women_and_child_development_mwcd` |
| Source dataset folder | lower snake case + acronym | `time_use_survey_tus` |
| Published file | `<Theme>_<content>_<Place>_<start>_to_<end>.csv` | `MCH_tenderdata_Assam_2019_to_2025.csv` |
| Profile file | resource file name, lower snake case, `.json` | `mch_tenderdata_assam_2019_to_2025.json` |
| Columns | lower snake case; `_inr`, `_date`, `_fiscal_year`, `is_` | `awarded_amount_inr` |
| Question IDs | `disc-`, `und-`, `ana-`, `oos-` + two digits | `ana-03` |

## Appendix B: Dataset README template

```markdown
# <Dataset title>

<One sentence: what the file is and what was done to it.>

## Registry metadata

| Field | Value |
|---|---|
| Source | <URL> |
| Publisher | <name> |
| Creator | <name> |
| Theme | <themes> |
| Spatial coverage | <coverage; subset used> |
| Temporal coverage | <start to end> |
| License | <licence> |

## Contents

**`<file name>`**

- Grain: one row per <thing>
- <sheet or column group>: <what it holds>

## Processing

- <script name>: <what it does>, rows in <n>, rows out <n>

## Quality checks

Reviewed by <role> on <date>: <results, flags, caveats>

## Changelog

| Date | Change | Effect on headline numbers |
|---|---|---|
```

## Appendix C: Keyword file format

```yaml
# tagging/keywords.yaml
tag_version: 1.0
tags:
  mch_core:
    definition: Works, goods or services mainly for pregnant women, mothers, newborns or children
    keywords:
      - {term: labour room, match: phrase}
      - {term: sncu, match: word, note: Special Newborn Care Unit}
  veto:
    keywords:
      - {term: veterinary, match: word}
  scheme_LAQSHYA:
    kind: scheme
    keywords:
      - {term: laqshya, match: word}
```

## Appendix D: Tagging review sheet

One row per record reviewed; the reviewer fills it in, and precision is computed from it.

| Record ID | Tag | Sample (tagged / untagged) | Correct? | If wrong, why | Fix proposed |
| --- | --- | --- | --- | --- | --- |
| `2024_BTC_41642_1` | `CHD_SCHEME` | tagged | No | "CHD" is part of the office name | Drop bare `chd`; keep the full scheme name |

## Appendix E: Pre-publication checklist

- [ ] Registry row and source README complete (Stage 2)
- [ ] Scripts rerun from a clean checkout give an identical file (Stage 3)
- [ ] Every tag defined, reviewed, precision at or above 90% (Stage 4)
- [ ] Geotagging at or above 85% placed; conflicts reviewed (Stage 5)
- [ ] Checks 1 to 12 passed or flagged; reviewer signed off (Stage 6)
- [ ] DataSpace metadata complete; IDs recorded in `usecase.json` (Stage 7)
- [ ] Query engine reference built and question bank passes (Stage 8)
- [ ] Responsible-use rules checked (Stage 9)

## Open questions for review

- The thresholds in this draft (90% tagging precision, 85% geotagged, 10 as the small-count cut-off for survey data, 5% change to trigger a narrative update) are proposals. Do they match what UNICEF expects?
- Should the UNICEF focal point sign off each use case, or only those with sensitive topics?
- Should keyword files move from Python code to `keywords.yaml` for existing use cases now, or at their next update?
