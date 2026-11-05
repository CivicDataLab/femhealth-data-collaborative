# Analysis reference: Assam MCH tenders

This is the reference the query engine's planner and narrator use when answering questions about this use case. It says how the data was made, what each measure means, how to write SQL against it, and what every answer must disclose.

- Use case: [civicdataspace.in/usecases/312](https://civicdataspace.in/usecases/312)
- Dashboard: [Linking Public Spending to Maternal and Child Health Outcomes in Assam](https://analytics.civicdataspace.in/superset/dashboard/p/xLKpnNXp6b2/)
- Data: `MCH_tenderdata_Assam_2019_to_2025.csv` (DataSpace resource `bc22644a-e7ff-4791-ac70-98d7322352e5`)
- Query against: the `mch_tenders` and `mch_tender_schemes` views in [views.sql](views.sql)

## 1. How the data was produced

| Step | What happens | Code |
|---|---|---|
| 1. Scrape | Monthly tender results downloaded from [assamtenders.gov.in](https://assamtenders.gov.in/nicgep/app), one CSV per month in `TENDERS/data/monthly_tenders/` | `TENDERS/scripts/scraper/` |
| 2. Classify as MCH | Keyword rules on title, reference and work description (details below). Veterinary, animal husbandry and sericulture departments are excluded | `TENDERS/scripts/mch_tenders.py` |
| 3. Tag schemes | Pattern match against scheme names and acronyms; several tags per tender allowed | `mch_tenders.py` (`SCHEMES_IDENTIFIER_BASE`) |
| 4. Mark awards | `is_awarded` = Status is an award status (`Accepted-AOC`, `AOC`, `AWARDED`...) | `mch_tenders.py` (`VALID_AWARDED_STATUSES`) |
| 5. Geotag district | Village, revenue circle and sub-district names found in the reference, title and location text are looked up in `ASSAM_VILLAGES_RC_DISTRICT_MAPPING.csv`. One answer gives that district; disagreeing answers give `CONFLICT`; no match gives `NA` | `TENDERS/scripts/geocode_district.py` |
| 6. Flag BTC | Tenders from Bodoland Territorial Council bodies get `BTC_flag` | `geocode_district.py` |
| 7. Publish | Output copied to `MCH_tenderdata_Assam_2019_to_2025.csv`; a polygon version is built for Superset maps | `TENDERS/data/Superset prep/` |

### MCH classification rule

A tender is **strict MCH** (`is_mch_strict`) if its text has at least one hit from:

- **Core MCH**: maternal, maternity, mother and child, labour room, maternity ward, newborn, neonatal, infant, NICU, SNCU...
- **ANC/PNC**: antenatal care, postnatal care, gestational diabetes screening...
- **Immunisation and child health**: immunisation, vaccine, cold chain, ILR, child health, RBSK, DEIC...

A named-scheme hit (JSSK, JSY, PMSMA, LaQshya, Mamoni...) also counts when nutrition terms or a health-facility word (PHC, CHC, district hospital, medical college...) appears too. Any veterinary or livestock word vetoes the tender.

A tender is **broad MCH** (`is_mch_broad`, the filter used for this file) if it is strict MCH, **or** the issuing department is a health body (NHM, H&FW, medical college, PWD building) **and** the tender has an MCH scheme tag or MCH infrastructure words (MCH wing, maternity OT...).

In this file 100 of the 112 tenders are strict MCH and all 112 are broad MCH.

## 2. Metric definitions

Use these names in plans shown to users, so the same words always mean the same thing.

| Metric | Definition (view column) | Plain words for the plan |
|---|---|---|
| MCH tenders | `count(*)` | "counting MCH-related tenders" |
| Awarded tenders | `count(*) FILTER (WHERE is_awarded)` | "counting tenders that were awarded" |
| **Awarded value** | `sum(awarded_amount_inr)` | "adding up the value of awarded contracts" |
| Estimated value | `sum(tender_value_inr)` | "adding up the estimated value at publication" (19 tenders have no estimate) |
| Time to contract | `median(days_publish_to_contract)` where `is_awarded` | "days from publication to contract date" |
| Single-bid share | `bids_received = 1` / all | "share of tenders with one bid" |

**Spending always means awarded value.** Never sum `bid_value_inr` over all rows: it includes rejected bids and overstates spending by about ₹58.7 crore.

**Awarded value is reliable for works, not goods.** 19 of the 59 awarded tenders (`awarded_value_suspect`) record a placeholder or a unit rate instead of the contract value: ₹0 (7 tenders), ₹1 (5, including a JE vaccine tender estimated at ₹10 crore), or per-unit prices such as ₹375 per Samahar kit. Almost all are Health and Family Welfare or NHM drug, equipment and kit contracts. So:

- Awarded value for **goods**, and for **Health and Family Welfare**, is a large undercount. Compare those by tender count.
- Whenever a money answer includes suspect tenders, say how many there are, and give their `tender_value_inr` estimate where one exists.

### Time

- **Year or month trends** use `result_year` or `result_month` (when results came out, close to the contract date). Say "by year of award" in the plan.
- **Fiscal years** (April to March) use `contract_fiscal_year`. Government users often mean fiscal year when they say "2023-24".
- `published_at` gives the publication date when a question is about when tenders were advertised.

### Geography

- `district` is NULL for 16 tenders (13 not geotagged, 3 conflicting). Show them as their own row ("district unknown") in district tables, so the totals still add up.
- District names follow `dtname` in `data-ecosystem/maps/Geojson/assam_district_2024-11.geojson`. Map user spellings with `glossary.json`.
- 10 of Assam's 35 districts have no MCH tender in the data. "No tenders" does not mean "no spending".

### Schemes

- Count by scheme with the `mch_tender_schemes` view (one row per tender and scheme).
- Scheme totals add up to more than the overall total. Never present them as shares of the total.
- `HFW` and `PWD_NH` are department tags; leave them out of "which schemes" answers or label them.
- `CHD_SCHEME` is a known false positive (see section 5).

### Money formatting

Answers are written for Indian government readers: give values in **crore** (≥ ₹1 crore) or **lakh**, with the rupee figure in the citation. 1 crore = 1e7, 1 lakh = 1e5.

## 3. SQL patterns

All SQL runs in DuckDB after loading `views.sql`. Each pattern below has been run; results are in `question_bank.json`.

```sql
-- Headline total
SELECT count(*) FILTER (WHERE is_awarded) AS awarded_tenders,
       round(sum(awarded_amount_inr) / 1e7, 2) AS awarded_crore
FROM mch_tenders;

-- Trend by year of award
SELECT result_year, count(*) AS tenders,
       round(coalesce(sum(awarded_amount_inr), 0) / 1e7, 2) AS awarded_crore
FROM mch_tenders GROUP BY 1 ORDER BY 1;

-- District comparison, keeping unknown districts visible
SELECT coalesce(district, 'District unknown') AS district,
       count(*) FILTER (WHERE is_awarded) AS awarded_tenders,
       round(sum(awarded_amount_inr) / 1e7, 2) AS awarded_crore
FROM mch_tenders GROUP BY 1 ORDER BY sum(awarded_amount_inr) DESC NULLS LAST;

-- Sensitivity check without the dominant GMCH tender
... WHERE tender_id <> '2020_PWBNH_17202_1'

-- Per scheme (double counts across schemes by design)
SELECT scheme, count(*) AS tenders
FROM mch_tender_schemes
WHERE scheme NOT IN ('HFW', 'PWD_NH', 'CHD_SCHEME')
GROUP BY 1 ORDER BY 2 DESC;
```

Planner rules:

1. Filter on `is_awarded` (or use `awarded_amount_inr`) for any money question, and count `awarded_value_suspect` rows in the same query.
2. For questions about totals, trends or Kamrup Metro, also run the version without `2020_PWBNH_17202_1` and report both if the answer changes a lot.
3. Never filter on `district = ...` without also reporting how many tenders have an unknown district.
4. Do not select `positive_keywords_dict`, `negative_keywords_dict` or polygon geometry; they are large audit or map columns.
5. Keep `bidder_name` out of results unless the user asks about a specific tender.

## 4. Answer templates for this use case

| Archetype | Typical questions | Must include |
|---|---|---|
| `trend` | Value or count by year or fiscal year | Year basis (award year or fiscal year), GMCH effect, small-count warning |
| `cross_region_comparison` | District or department rankings | Unknown-district row, GMCH effect for Kamrup Metro, small-count warning |
| `dataset_overview` | Coverage, columns, how it was built | Portal-only coverage, keyword classification, link to use case and dashboard |

Each answer cites: dataset `93a26985-5f8d-447a-b6b3-506e2a70c5c9`, resource `bc22644a-e7ff-4791-ac70-98d7322352e5`, the SQL that ran, and the dashboard link when a map or chart would help.

## 5. Caveats to disclose

Say the first two in **every** analysis answer; the rest only when relevant.

1. **Partial coverage.** Only tenders published on assamtenders.gov.in. The use case reports that only about 20% of Assam's tenders are published.
2. **Keyword classification.** "MCH tender" is defined by keyword rules, not by an official tag.
3. **Goods values are missing.** Most awarded goods contracts are recorded as ₹0, ₹1 or a unit rate; awarded value covers construction works well and goods poorly.
4. **One project dominates.** The 500-bed Mother and Child Hospital at GMCH (₹214 crore, awarded Dec 2020, SOPD-ODS) is about 80% of all awarded value.
5. **Unknown districts.** 16 of 112 tenders cannot be placed in a district.
6. **Small numbers.** Most districts and months have 1 to 5 tenders. Do not rank them or quote percentage changes.
7. **Scheme tags are inferred.** LAQSHYA is over-assigned (generic labour-room phrases match it). CHD_SCHEME comes from the BTC office name "Director Cum CHD", not the heart disease scheme.
8. **Published findings vs data.** The use case narrative (2020-2023 analysis) says LAQSHYA saw limited activity. In the current file it is the second most common scheme tag (28 tenders, all also tagged NHM; NHM has 49). If asked, give both and explain the tagging difference.
9. **Award-disclosure delay.** The ~250-day delay on the use case page is a different measure from `days_publish_to_contract`.

## 6. Questions this use case cannot answer (v1)

| Question type | Why | Point to |
|---|---|---|
| Did spending improve IMR or other outcomes? | Needs a second dataset, and causal claims are out of scope | IMR District-wise dataset (`88be5d92-...`), dashboard |
| Total MCH budget or expenditure | Tenders are not budgets | Union Gender Budget Statement (data-ecosystem) |
| Tenders outside Assam | Out of coverage | — |
| Forecasts | Not supported | Year-wise trend |
| Contractor wrongdoing or contact details | Not in the data; protects individuals | Aggregate views only |

## 7. Keeping this reference current

When `MCH_tenderdata_Assam_2019_to_2025.csv` changes (new months are scraped), its sha256 will no longer match `dataset_profiles/*.json`. Then:

1. Regenerate the profiles and the question bank's expected results with `scripts/build_dataset_profiles.py` and `scripts/build_question_bank.py`.
2. Update the headline numbers in sections 2 and 5 and in `usecase.json`.
3. Re-run the golden query set and compare with the previous run.
