# Contributing to the FemHealth Data Collaborative

Thank you for helping improve data on the health of women and girls in Assam. This repository holds source datasets, the scripts that clean and tag them, use case analyses, and the reference material the FemHealth query engine uses to answer questions. Contributions from researchers, civil society organisations, government partners and developers are all welcome.

Everyone taking part is expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Read this first

All data work in this repository follows the **[SOP on dataset transformation and tagging](data-ecosystem/docs/%5BWIP%5D%20SOP_dataset_transformation_and_tagging.md)**. It sets out the ten stages from scoping a use case to publishing it, with the standards for column names, units, tagging review, geotagging and quality checks. This guide covers how to send a change; the SOP covers what a good change looks like.

## Ways to contribute

| You want to | Do this |
| --- | --- |
| Report a wrong number, a mis-tagged record or a broken file | [Open an issue](#reporting-a-data-problem) |
| Suggest a dataset we should add | [Open an issue](#suggesting-a-dataset) with its source and licence |
| Add a source dataset | Follow SOP Stage 2, then open a pull request |
| Add or update a use case analysis | Follow SOP Stages 1 to 10, then open a pull request |
| Change tagging or geotagging rules | Follow SOP Stages 4 to 6, then open a pull request |
| Fix a script or improve documentation | Open a pull request |

### Reporting a data problem

Data problems are the most useful issues you can open. Please include:

- the file path, for example `analytics/Assam_MCH_analysis/TENDERS/data/MCH_tenderdata_Assam_2019_to_2025.csv`
- the record IDs or row numbers affected
- what is wrong and what you expected
- evidence, such as a link to the original source page or report

### Suggesting a dataset

Give as much as you can of what the [data registry](data-ecosystem/knowledge_graph/data_registry.csv) records: title, publisher, source URL, licence, geography, time period, update frequency and format. Say which use case or question the dataset would help answer.

## Repository layout

```
analytics/                     One folder per use case
  <Use_case>/
    <dataset>/                 Data, scripts and README for that analysis
    query_engine_reference/    Files the query engine ingests (see SOP Stage 8)
data-ecosystem/
  knowledge_graph/             data_registry.csv: metadata for every dataset
  sources/<publisher>/<dataset>/   Raw source data, one README per folder
  maps/                        District and revenue circle boundaries, lookups
  docs/                        SOP and other process documents
```

## Getting set up

You need Git and Python 3.12 or later.

```bash
git clone https://github.com/CivicDataLab/femhealth-data-collaborative.git
cd femhealth-data-collaborative
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pre-commit && pre-commit install
```

`requirements.txt` covers every script and notebook in the repository, grouped by what uses each package. The tender scraper also needs Google Chrome with a matching chromedriver and the Tesseract OCR engine installed on your system.

`pre-commit install` turns on checks that run on each commit: formatting Python with black and isort, validating YAML and JSON, blocking private keys, and stopping files over 50 MB. They never rewrite data files.

## Making a change

1. **Branch from `main`.** Name the branch after the kind of change:
    - `data/<dataset>` for a new or updated source dataset
    - `usecase/<use-case>` for analysis work
    - `tagging/<use-case>` for keyword or rule changes
    - `fix/<short-description>` or `docs/<short-description>`
2. **Keep pull requests focused.** One dataset, one use case or one fix per pull request makes review possible.
3. **Write clear commit messages** that say what changed and why, for example `Add NFHS-5 district factsheets for Assam` or `Drop bare "chd" keyword that matched a BTC office name`.
4. **Open a pull request** against `main` and fill in the description (see below).
5. **Get a review** from someone who did not build the change. For data and tagging changes, the reviewer runs the SOP checks.

### What to put in the pull request description

- What changed and why.
- For new data: source URL, publisher and licence.
- Effect on headline numbers, such as row counts, totals or tag counts before and after.
- Which SOP Stage 6 checks you ran, and any flags or caveats you added.
- Whether you regenerated the query engine reference (see below).

## Rules for data files

- **Never edit a raw file by hand.** Keep source files exactly as downloaded; every change happens in a script that is committed alongside the output.
- **Record the licence.** Only add data whose licence allows redistribution. Government data is usually under the [Government Open Data License – India](https://data.gov.in/government-open-data-license-india). If the licence is unclear, open an issue instead of committing the file.
- **No personal data.** Do not commit names, phone numbers, addresses or IDs of private individuals beyond what an official public source already publishes, and never commit individual-level survey data that has not already been released publicly by its publisher.
- **No secrets.** Never commit credentials, API keys, tokens or `.env` files.
- **Mind file sizes.** GitHub warns above 50 MB and rejects files above 100 MB. If a file is larger than 50 MB, mention it in the pull request; above 100 MB, open an issue so maintainers can agree where it should live.
- **Use the standard formats.** CSV in UTF-8 with a header row; column names, units, dates and district spellings as in the SOP Stage 3 table.
- **Write a README** for every new dataset folder, using the template in the SOP's Appendix B.
- **Register the dataset** with a row in `data-ecosystem/knowledge_graph/data_registry.csv`, and update the publisher table in `data-ecosystem/sources/README.md`.

## Rules for scripts

- Take input and output paths as arguments or set them at the top of the script; do not build them from the current working directory.
- Print row counts in and out, and how many rows each filter drops.
- Keep keyword lists and lookups in one place that scripts read, not copied between files.
- Format Python with [black](https://black.readthedocs.io/) and sort imports with [isort](https://pycqa.github.io/isort/) using the black profile. The pre-commit hooks do this on every commit; to run them by hand:

  ```bash
  pre-commit run --files <files you changed>
  ```

There is no automated test suite yet. Quality checks are run per use case as described in SOP Stage 6.

## Regenerating query engine references

If you change a dataset, tags or rules in a use case that has a `query_engine_reference/` folder, rebuild its profiles and question bank from the repository root. For the MCH tenders use case:

```bash
python3 analytics/Assam_MCH_analysis/query_engine_reference/scripts/build_dataset_profiles.py
python3 analytics/Assam_MCH_analysis/query_engine_reference/scripts/build_question_bank.py
```

Then check the hand-written figures listed in that folder's README against the new output, and include the changes in your pull request.

## Responsible use

Contributions must follow the responsible data use rules in SOP Stage 9: publish aggregates rather than details about individuals, do not rank or turn small counts into percentages, show associations rather than causes, and never present procurement patterns as evidence of wrongdoing.

## Security

Please do not report security problems in public issues. Email `tech@civicdatalab.in` instead.

## Questions

Open an issue in this repository and we will reply there.

## Licence

By contributing code, scripts or documentation, you agree that your contribution is licensed under the [MIT License](LICENSE). Third-party datasets keep their original publishers' licences and are not covered by the MIT License; credit the original publisher when you add or reuse them.
