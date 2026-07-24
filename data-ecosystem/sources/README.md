# Sources

Raw source datasets for the FemHealth Data Collaborative, organized by publisher (per the registry's `Publisher` field), with one subfolder per dataset inside each publisher folder. Datasets with no registry `Publisher` value stay at the top level. Each dataset folder has its own `README.md` describing its files and relevant metadata.

Full metadata for every tracked dataset (links, indicators, coverage, license, etc.) lives in [`../knowledge_graph/data_registry.csv`](../knowledge_graph/data_registry.csv) — the per-folder READMEs summarize the fields relevant to that dataset. Registry `Assignee` values are excluded from these READMEs as they are personal information.

## By publisher

| Publisher folder | Datasets |
|---|---|
| [`ministry_of_health_and_family_welfare_mohfw/`](ministry_of_health_and_family_welfare_mohfw/) | NFHS-5 District Factsheets, Item-wise HMIS Report, CNNS 2016-2018 (joint w/ UNICEF India), NHM Report |
| [`ministry_of_statistics_and_programme_implementation_mospi/`](ministry_of_statistics_and_programme_implementation_mospi/) | Time Use Survey (TUS), Household Consumption Expenditure Survey (HCES) |
| [`national_institute_of_mental_health_and_neuro_sciences_nimhans/`](national_institute_of_mental_health_and_neuro_sciences_nimhans/) | National Mental Health Survey (NMHS) Phase 1 |
| [`ministry_of_women_and_child_development_mwcd/`](ministry_of_women_and_child_development_mwcd/) | Union Gender Budget Statement |

## No registry publisher listed

| Folder | Registry title |
|---|---|
| [`ncaer_survey_des_study/`](ncaer_survey_des_study/) | NCAER Survey (DES Study) — Women's Condition in Assam *(registry `Publisher` field is blank; report itself credits NCAER as conductor, DES Assam as commissioner)* |

## Not in the registry

| Folder | Description |
|---|---|
| [`reference_data_catalog_qdf/`](reference_data_catalog_qdf/) | External source catalog, not a dataset tracked in the registry — see folder README |

## Registry entries with no data here yet

These datasets are tracked in `data_registry.csv` but have no files in this repo yet:

- Periodic Labour Force Survey (PLFS) — publisher: MoSPI
- Demand for Grants — Department of Health and Family Welfare — publisher: Ministry of Finance
- Poshan Tracker — District-wise Statistics — publisher: MWCD
