# Query engine reference: Assam MCH tenders

Reference material the FemHealth query engine ingests for the use case **[Using Data Analysis to Spot Gaps in Maternal and Child Healthcare Service Delivery](https://civicdataspace.in/usecases/312)**. It tells the engine what the data is, how to query it correctly, and how to check its answers.

- Dashboard: [Linking Public Spending to Maternal and Child Health Outcomes in Assam](https://analytics.civicdataspace.in/superset/dashboard/p/xLKpnNXp6b2/)
- Source analysis: [`../TENDERS/`](../TENDERS/)

## Files

| File | Used by (query engine component) | Contents |
|---|---|---|
| [`usecase.json`](usecase.json) | Semantic search index, Understand mode | Use case card: DataSpace IDs and links, dashboard, coverage, linked datasets and resources, published findings with provenance, limitations, sensitivity |
| [`dataset_profiles/`](dataset_profiles/) | Dataset profiles, Understand mode, analysis planner | One JSON per DataSpace resource: grain, row counts, columns (type, unit, description, missing, values), coverage, quirks, file sha256 |
| [`views.sql`](views.sql) | Analysis engine (DuckDB sandbox) | Typed, cleaned views `mch_tenders` and `mch_tender_schemes`. The planner writes SQL against these, not the raw CSV |
| [`analysis_reference.md`](analysis_reference.md) | Planner and narrator system context | How the data was made, metric definitions, SQL patterns, caveats to disclose, out-of-scope questions |
| [`glossary.json`](glossary.json) | Query parsing, narration | Scheme codes, departments, procurement terms, units (lakh, crore, fiscal year), district name variants, Hindi and Assamese terms |
| [`question_bank.json`](question_bank.json) | Logging and evaluation (golden query set) | 30 questions across discover, understand, analyse and out of scope, with language variants, SQL, executed results and required caveats |
| [`scripts/`](scripts/) | Maintenance | Regenerate the profiles and question bank when the data changes |

## Regenerating

From the repository root:

```bash
pip install duckdb pandas
python3 analytics/Assam_MCH_analysis/query_engine_reference/scripts/build_dataset_profiles.py
python3 analytics/Assam_MCH_analysis/query_engine_reference/scripts/build_question_bank.py
```

Do this whenever `TENDERS/data/MCH_tenderdata_Assam_2019_to_2025.csv` changes. Its sha256 is recorded in the profile, so a mismatch shows the reference is stale. Then check the hand-written numbers (sections 2 and 5 of `analysis_reference.md`, `limitations` and `coverage` in `usecase.json`, and the `quirks` text in `scripts/build_dataset_profiles.py`) against the new output.

## Conventions for other use cases

Each use case folder under `analytics/` gets a `query_engine_reference/` folder with the same file names:

- `usecase.json` has the same top-level keys: `usecase_id`, `links`, `dataspace_record`, `coverage`, `datasets`, `related_repository_data`, `methodology_summary`, `published_findings`, `limitations`, `sensitivity`.
- Profile files are named after the resource file in lower snake case: `MCH_tenderdata_Assam_2019_to_2025.csv` becomes `dataset_profiles/mch_tenderdata_assam_2019_to_2025.json`.
- View columns are lower snake case, with units in the name for money (`_inr`) and explicit types. Raw column names are kept in the profile (`name`) next to the view name (`view_column`).
- Question IDs are `disc-NN`, `und-NN`, `ana-NN`, `oos-NN`, matching the engine's four intents. `answer_template` is one of `trend`, `cross_region_comparison` or `dataset_overview`.
- Language keys: `en`, `hi`, `as`, `hinglish`.
- Anything taken from the DataSpace page rather than computed from data sits under `published_findings` with its provenance.

## Open items

- The district-wise, scheme-wise and department-wise aggregates, and the IMR dataset, are on DataSpace but not in this repo, so they are listed in `usecase.json` but not profiled.
- The MCH tenders dataset has no row in `data-ecosystem/knowledge_graph/data_registry.csv`.
- The Hindi, Assamese and Hinglish question variants are machine drafted and need native-speaker review.
- `CHD_SCHEME` tagging and the LAQSHYA over-match come from `TENDERS/scripts/mch_tenders.py`. They are documented here, not fixed.
