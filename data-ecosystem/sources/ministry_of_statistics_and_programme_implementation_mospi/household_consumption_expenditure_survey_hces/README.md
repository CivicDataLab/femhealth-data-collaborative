# Household Consumption Expenditure Survey (HCES), MoSPI

Household-level consumption and expenditure microdata, covering food, non-food consumables/services, and durable goods ownership.

## Registry metadata

| Field | Value |
|---|---|
| Category | MOSPI household consumption and expenditure |
| Source | https://microdata.gov.in/NADA/index.php/catalog/237 |
| Publisher | Ministry of Statistics and Programme Implementation (MoSPI), Government of India |
| Creator | National Statistical Office (NSO), MoSPI |
| Theme | Economy; Consumption |
| Spatial coverage | India, up to district level |

## Contents

**`hces_23_24/`** — 2024 survey wave, four linked files sharing a common household identifier (`hhid`) and sample design columns (`FSU_Serial_No`, `Sector`, `State`, `NSS_Region`, `District`, `Stratum`, etc.):

| File | Rows | Level | Covers |
|---|---|---|---|
| `houshold_characeristics.csv` | ~37K | Household / person | Demographics (age, gender, marital status, education), economic activity, religion, social group, land ownership, dwelling characteristics, cooking/lighting fuel, ration card type — ~68 indicators |
| `food_dairy.csv` | ~466K | Household × food item | Ration purchases, online grocery purchases, food item-wise quantity/value consumed — ~58 indicators |
| `consumables_and_services.csv` | ~348K | Household × item | Non-food consumables and services expenditure (fuel, health, education, communication, clothing, etc.), plus welfare scheme benefits received — ~54 indicators |
| `durable_goods.csv` | ~311K | Household × durable item | Durable goods purchases (item, quantity, value, purchase mode) — ~47 indicators |

Full indicator lists for each file are in the registry (`data-ecosystem/knowledge_graph/data_registry.csv`, row for this dataset).
