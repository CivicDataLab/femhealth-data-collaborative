"""Build dataset_profiles/*.json from the tender CSVs.

Run from the repository root:
    python3 analytics/Assam_MCH_analysis/query_engine_reference/scripts/build_dataset_profiles.py

Statistics are computed from the data; column descriptions and quirks are
written by hand in this file. Re-run whenever the CSVs change, and review the
quirks text against the new numbers.
"""
import json, hashlib, datetime, os
import pandas as pd

REF = "analytics/Assam_MCH_analysis/query_engine_reference"
DATA = "analytics/Assam_MCH_analysis/TENDERS/data"
os.makedirs(f"{REF}/dataset_profiles", exist_ok=True)

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def colstats(s, top=True):
    raw = s.astype("string").str.strip()
    missing = int((s.isna() | raw.isin(["", "NA", "nan"])).sum())
    d = {"missing": missing, "distinct": int(raw.nunique(dropna=True))}
    if top and d["distinct"] <= 30:
        vc = raw.value_counts(dropna=True)
        d["values"] = {str(k): int(v) for k, v in vc.items()}
    else:
        d["examples"] = [str(x)[:140] for x in raw.dropna().unique()[:3]]
    return d

# ---------------------------------------------------------------- main file
f = f"{DATA}/MCH_tenderdata_Assam_2019_to_2025.csv"
df = pd.read_csv(f, dtype=str, keep_default_na=False)

# raw column -> (view column, type, unit, description, flags)
C = {
 "Tender ID": ("tender_id", "string", None, "Portal tender ID, e.g. '2023_NHM_34072_1' (year_issuer_number_part). Unique per row.", ["primary_key"]),
 "tender_externalreference": ("tender_reference", "string", None, "Issuer's own reference number. Not unique: several tenders can share one.", []),
 "tender_title": ("tender_title", "text", None, "Tender title as published. Some BTC titles are just codes like 'TN_217_D'.", ["searchable_text"]),
 "Work Description": ("work_description", "text", None, "Work description; often the same as the title, sometimes cut off.", ["searchable_text"]),
 "Tender Category": ("tender_category", "category", None, "Works, Goods or Services.", ["dimension"]),
 "Tender Type": ("tender_type", "category", None, "Open Tender, Open Limited, Limited or Single.", ["dimension"]),
 "Form of contract": ("form_of_contract", "category", None, "Item Rate, Item Wise, Supply, Buy, Turn-key, Works, Fixed-rate.", ["dimension"]),
 "Product Category": ("product_category", "category", None, "Portal product category (Civil Works, Medicines, Medical Equipments/Waste...).", ["dimension"]),
 "Is Multi Currency Allowed For BOQ": (None, "category", None, "Always 'No'. Not useful.", ["constant"]),
 "Allow Two Stage Bidding": (None, "category", None, "Always 'No'. Not useful.", ["constant"]),
 "Independent External Monitor/Remarks": (None, "category", None, "Always 'NA'. Not useful.", ["constant"]),
 "Published Date": ("published_at", "datetime", None, "Publication timestamp, format '02-Feb-2018 04:30 PM'.", ["time"]),
 "Pre Bid Meeting Date": (None, "datetime", None, "Pre-bid meeting timestamp; mostly 'NA'.", []),
 "Bid Validity(Days)": (None, "integer", "days", "Bid validity period.", []),
 "Should Allow NDA Tender": (None, "category", None, "Always 'No'. Not useful.", ["constant"]),
 "Allow Preferential Bidder": (None, "category", None, "Always 'No'. Not useful.", ["constant"]),
 "Payment Mode": (None, "category", None, "Online, Offline or Not Applicable (fee payment).", []),
 "Bid Opening Date": ("bid_opening_at", "datetime", None, "Bid opening timestamp, same format as Published Date.", ["time"]),
 "Organisation Chain": ("organisation_chain", "string", None, "Issuing organisation hierarchy, '||'-separated. Same as Department in this file.", []),
 "location": ("location_text", "string", None, "Free-text work location from the portal (town, facility or district). One input to geotagging.", []),
 "Pincode": ("pincode", "integer", None, "Work-location PIN code as entered by the issuer (read as float in pandas, e.g. 783370.0).", []),
 "No of Bids Received": ("bids_received", "integer", "bids", "Number of bids received (1 or 2 in this file).", ["measure"]),
 "Tender Value in ₹": ("tender_value_inr", "number", "INR", "Estimated tender value at publication. String with Indian digit grouping ('2,06,34,54,000'); strip commas.", ["measure"]),
 "Bidder Name": ("bidder_name", "string", None, "Name of the bidder in this row. Can be an individual's name.", ["personal_data_caution"]),
 "Awarded Value": ("bid_value_inr", "number", "INR", "Value of the bid in this row. Filled for rejected bids too, so only counts as spending when is_awarded is true (use awarded_amount_inr). For many goods / item-rate contracts it is a placeholder (0, 1) or a unit rate (awarded_value_suspect).", ["measure"]),
 "Status": ("status", "category", None, "Result for the listed bid: Accepted-AOC, Rejected-AOC, Not Admitted-Fee/PreQual/Technical, Rejected-Finance, Rejected-Technical.", ["dimension"]),
 "Contract Date :": ("contract_date", "date", None, "Contract date, format '07-Mar-2019'. Header has a trailing ' :'.", ["time"]),
 "Tender Stage": ("tender_stage", "category", None, "'AOC' or blank.", []),
 "Department": ("department", "string", None, "Issuing department chain, '||'-separated. department_top in the view is the first segment.", ["dimension"]),
 "is_mch_strict": ("is_mch_strict", "boolean", None, "Passed the strict MCH keyword rule (mch_filter_strict in mch_tenders.py).", ["derived"]),
 "positive_keywords_dict": (None, "json_string", None, "Python dict literal of MCH keyword hit counts. Audit trail for classification; not for analysis.", ["derived", "audit"]),
 "negative_keywords_dict": (None, "json_string", None, "Python dict literal of veterinary-term hit counts; all zero in this file.", ["derived", "audit"]),
 "Scheme": ("scheme_tags", "string", None, "';'-separated scheme codes (see glossary.json). Use the mch_tender_schemes view to count by scheme.", ["derived", "dimension", "multi_value"]),
 "is_awarded": ("is_awarded", "boolean", None, "Status is an award status. Use as the filter for spending.", ["derived", "filter"]),
 "is_mch_broad": (None, "boolean", None, "Passed the broad MCH rule; always True because the file is filtered on it.", ["derived", "constant"]),
 "month": ("result_month", "string", "YYYY_MM", "Results batch the tender was scraped from. Matches the contract-date month for 93% of rows. Use for year or month trends.", ["derived", "time"]),
 "tender_district_externalReference": (None, "string", None, "District guessed from the reference number. Empty for every row.", ["derived", "constant"]),
 "tender_district_title_description": (None, "string", None, "District guessed from title and description text.", ["derived"]),
 "tender_district_location": (None, "string", None, "District guessed from the location field.", ["derived"]),
 "BTC_flag": ("is_btc", "boolean", None, "Tender issued by a Bodoland Territorial Council body.", ["derived", "filter"]),
 "DISTRICT_FINALISED": ("district", "category", None, "Final district. 'NA' = not geotagged, 'CONFLICT' = sources disagree; both become NULL in the view (see district_geotag_status). 'SIVSAGAR' becomes 'SIVASAGAR'.", ["derived", "dimension", "geography"]),
}
assert list(C) == list(df.columns), set(df.columns) ^ set(C)

columns = []
for raw, (view, typ, unit, desc, flags) in C.items():
    entry = {"name": raw, "view_column": view, "type": typ}
    if unit: entry["unit"] = unit
    entry["description"] = desc
    if flags: entry["flags"] = flags
    entry["stats"] = colstats(df[raw], top=typ in ("category", "boolean"))
    columns.append(entry)

num = lambda s: pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
tv, bv = num(df["Tender Value in ₹"]), num(df["Awarded Value"])
aw = df["is_awarded"] == "True"
pub = pd.to_datetime(df["Published Date"].str.strip(), format="%d-%b-%Y %I:%M %p", errors="coerce")
cd = pd.to_datetime(df["Contract Date :"].str.strip(), format="%d-%b-%Y", errors="coerce")
for e in columns:
    if e["name"] == "Tender Value in ₹":
        e["stats"].update(min=float(tv.min()), median=float(tv.median()), max=float(tv.max()))
    if e["name"] == "Awarded Value":
        e["stats"].update(zeros=int((bv == 0).sum()), sum_all_rows=round(float(bv.sum()), 2),
                          sum_where_awarded=round(float(bv[aw].sum()), 2))

profile = {
  "resource_name": "MCH_tenderdata_Assam_2019_to_2025.csv",
  "dataspace_dataset_id": "93a26985-5f8d-447a-b6b3-506e2a70c5c9",
  "dataspace_resource_id": "bc22644a-e7ff-4791-ac70-98d7322352e5",
  "repo_path": f,
  "identical_copies": [f"{DATA}/mchtenders_districtgeotagged.csv (same columns and rows; pipeline output)",
                       f"{DATA}/Superset prep/MCH_tenderdata_Assam_2019_to_2025.csv (byte-identical)"],
  "sha256": sha(f),
  "profiled_on": datetime.date.today().isoformat(),
  "produced_by": ["analytics/Assam_MCH_analysis/TENDERS/scripts/mch_tenders.py",
                  "analytics/Assam_MCH_analysis/TENDERS/scripts/geocode_district.py"],
  "analysis_view": "views.sql -> mch_tenders",
  "grain": "One row per MCH-related tender (unique Tender ID), with the bid listed at the results stage.",
  "row_count": len(df),
  "column_count": len(df.columns),
  "coverage": {
    "geography": "Assam; district (DISTRICT_FINALISED)",
    "districts_present": sorted(set(df["DISTRICT_FINALISED"]) - {"", "NA", "CONFLICT"}),
    "districts_present_count": len(set(df["DISTRICT_FINALISED"]) - {"", "NA", "CONFLICT"}),
    "published_from": str(pub.min().date()), "published_to": str(pub.max().date()),
    "contract_from": str(cd.min().date()), "contract_to": str(cd.max().date()),
    "result_months": sorted(set(df["month"])),
  },
  "headline_numbers": {
    "tenders": len(df),
    "awarded_tenders": int(aw.sum()),
    "awarded_amount_inr": round(float(bv[aw].sum()), 2),
    "largest_awarded_tender": {"tender_id": "2020_PWBNH_17202_1", "title": "Mother and Child Hospital (500 bedded) at GMCH, Guwahati, SOPD-ODS",
                               "awarded_amount_inr": float(bv[df["Tender ID"] == "2020_PWBNH_17202_1"].iloc[0]),
                               "share_of_awarded_amount": round(float(bv[df["Tender ID"] == "2020_PWBNH_17202_1"].iloc[0] / bv[aw].sum()), 3)},
  },
  "quirks": [
    {"id": "bid_value_not_award", "text": "'Awarded Value' is filled for rejected and not-admitted bids too. Summing all rows overstates spending by ~₹58.7 crore. Use awarded_amount_inr (is_awarded only)."},
    {"id": "goods_award_placeholders", "text": f"{int((aw & (bv.fillna(0) < 100000)).sum())} awarded tenders, almost all goods or item-rate drug/equipment contracts, record a placeholder or unit rate instead of the contract value: ₹0 ({int((aw & (bv == 0)).sum())}), ₹1 ({int((aw & (bv == 1)).sum())}, e.g. a JE vaccine tender estimated at ₹10 crore), ₹375 per Samahar kit. Spending on goods, and by Health and Family Welfare, is therefore badly understated. Flag: awarded_value_suspect in the view. Report these tenders separately, and use tender_value_inr as the estimate where it exists."},
    {"id": "single_tender_dominates", "text": "One ₹214 crore GMCH hospital tender is ~80% of awarded value. Say so in any total, trend or Kamrup Metro answer; offer a view without it."},
    {"id": "indian_digit_grouping", "text": "'Tender Value in ₹' is text like '2,06,34,54,000'. Values are rupees, not lakh or crore."},
    {"id": "title_period_mismatch", "text": "Title says 2019 to 2025, but 10 tenders were published in Dec 2017 or 2018; the range is the results period."},
    {"id": "result_month_not_publish_month", "text": "'month' is the results batch, close to the contract month, not the publication month."},
    {"id": "fiscal_vs_calendar", "text": "Source has calendar dates only. Government readers often expect fiscal years (Apr to Mar); contract_fiscal_year in the view provides it."},
    {"id": "district_missing", "text": "13 tenders not geotagged (NA) and 3 CONFLICT. District totals do not add up to the state total."},
    {"id": "district_spelling", "text": "'SIVSAGAR' here vs 'SIVASAGAR' in the boundary file; normalised in the view."},
    {"id": "scheme_multi_value", "text": "Scheme holds several codes separated by ';'. Counting per scheme double counts tenders across schemes."},
    {"id": "chd_false_positive", "text": "CHD_SCHEME (6 tenders) comes from the office name 'Director Cum CHD - PWD BTC', not the Congenital Heart Disease scheme."},
    {"id": "btc_department_spelling", "text": "Bodoland Territorial Council appears as both 'Bodoland Territorial Council' and 'Bodoland Territorial Council-PWD' at the top level."},
    {"id": "small_counts", "text": "Most districts have 1 to 3 tenders and most months have 1 to 5. Avoid rankings or % change on such small numbers."},
    {"id": "coverage_bias", "text": "Only tenders published on the portal (the use case cites ~20% of all tenders). Absence of tenders in a district does not mean absence of spending."},
    {"id": "pandas_na", "text": "pandas reads the string 'NA' as missing by default (DISTRICT_FINALISED, Pre Bid Meeting Date). Load with keep_default_na=False or use the view."},
  ],
  "suggested_dimensions": ["district", "department_top", "scheme (mch_tender_schemes)", "tender_category", "product_category", "result_year", "contract_fiscal_year", "status", "is_btc"],
  "suggested_measures": ["count(*)", "count(*) FILTER (WHERE is_awarded)", "sum(awarded_amount_inr)", "sum(tender_value_inr)", "median(days_publish_to_contract)"],
  "joins": {
    "district": "Joins to data-ecosystem/maps/Geojson/assam_district_2024-11.geojson on dtname, and to district-level outcome data (IMR, NFHS-5, HMIS) after name normalisation. Cross-dataset: not in v1."
  },
  "columns": columns,
}
json.dump(profile, open(f"{REF}/dataset_profiles/mch_tenderdata_assam_2019_to_2025.json", "w"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- polygons file
fp = f"{DATA}/MCH_tenderdata_Assam_2019_to_2025_polygons.csv"
p = pd.read_csv(fp, dtype=str, keep_default_na=False)
missing_ids = set(df["Tender ID"]) - set(p["tender_id"])
dropped = df[df["Tender ID"].isin(missing_ids)]["DISTRICT_FINALISED"].replace("", "NA").value_counts().to_dict()
pcols = []
for c in p.columns:
    desc = {"geometry": "District boundary as WKT POLYGON / MULTIPOLYGON.",
            "polygons": "Same boundary as a JSON array of [lon, lat] vertices, for Superset deck.gl Polygon charts.",
            "dtname": "District name from the boundary file joined to district_finalised.",
            "timeperiod": "result month as 'YYYY-MM' (the main file's 'month' with a hyphen)."}.get(c, "snake_case copy of the matching column in MCH_tenderdata_Assam_2019_to_2025.csv.")
    e = {"name": c, "description": desc}
    if c not in ("geometry", "polygons"):
        e["stats"] = colstats(p[c], top=False)
    pcols.append(e)
poly = {
  "resource_name": "MCH_tenderdata_Assam_2019_to_2025_polygons.csv",
  "dataspace_dataset_id": "93a26985-5f8d-447a-b6b3-506e2a70c5c9",
  "dataspace_resource_id": "76bb9002-671b-4883-aa45-679c647fc06d",
  "repo_path": fp,
  "sha256": sha(fp),
  "profiled_on": datetime.date.today().isoformat(),
  "produced_by": [f"{DATA}/Superset prep/polygon-to-vertices.ipynb"],
  "purpose": "Map layer for the Superset dashboard: each tender row carries its district polygon.",
  "v1_analysable": False,
  "grain": "One row per tender with a district boundary attached.",
  "row_count": len(p),
  "column_count": len(p.columns),
  "quirks": [
    {"id": "incomplete", "text": f"Has {len(p)} of the {len(df)} tenders in the main file. Missing tenders by DISTRICT_FINALISED: {dropped}. Why the geotagged ones were dropped is not documented. Never use for totals."},
    {"id": "large_text_columns", "text": "geometry and polygons hold full boundary coordinates (~2 MB file). Do not send them to the LLM; drop them before profiling or narration."},
    {"id": "dtname_mismatch", "text": f"dtname differs from district_finalised on {int((p['dtname'] != p['district_finalised']).sum())} rows (CONFLICT rows and the SIVSAGAR spelling)."},
  ],
  "columns": pcols,
}
json.dump(poly, open(f"{REF}/dataset_profiles/mch_tenderdata_assam_2019_to_2025_polygons.json", "w"), ensure_ascii=False, indent=2)
print("ok", len(columns), len(pcols), dropped)
print(p[p.dtname != p.district_finalised][["dtname", "district_finalised"]].to_string())
