# Time Use Survey (TUS), MoSPI

Household-level roster and sampling metadata from MoSPI's Time Use Survey.

## Registry metadata

| Field | Value |
|---|---|
| Category | Time use survey MOSPI |
| Publisher | Ministry of Statistics and Programme Implementation (MoSPI), Government of India |
| Creator | National Statistical Office (NSO), MoSPI |
| Theme | Demographics; Gender; Labour |
| Spatial coverage | India |
| Temporal coverage | 2024 |

The registry lists this dataset as two parts, `TUS_HH_2024` (household) and `TUS_Person_2024` (person). Only the household file is currently in this repository — the person-level file has not yet been added.

## Contents

**`tus_hh_2024.xlsx`** (`Sheet1`) — one row per sampled household, with columns including `schedule_id`, `schedule_code`, `survey_year`, `survey_quarter`, `fsu_serial_no`, `sample_household_no`, `hh_id`, `sector` (Rural/Urban), and further sampling/design fields.

## Missing

- `TUS_Person_2024` — person-level time-use records (not yet added)
