"""Build question_bank.json: the questions are defined here; every `sql` is
executed with DuckDB against views.sql and the result is stored as the
expected answer.

Run from the repository root (needs `pip install duckdb`):
    python3 analytics/Assam_MCH_analysis/query_engine_reference/scripts/build_question_bank.py

Edit questions in this file, not in question_bank.json, which is overwritten.
"""
import json, sys, datetime
import duckdb

REF = "analytics/Assam_MCH_analysis/query_engine_reference"
DS_MAIN = "93a26985-5f8d-447a-b6b3-506e2a70c5c9"
RES_MAIN = "bc22644a-e7ff-4791-ac70-98d7322352e5"
RES_POLY = "76bb9002-671b-4883-aa45-679c647fc06d"
DS_IMR = "88be5d92-ac1d-4305-9280-1b4f3595c1ce"
DS_DEPT = "4ec13774-1086-4eb1-b8cf-bd3329d46cf6"
DS_SCHEME = "f9f95e8d-fe66-4f0f-9d38-0d4c266f143e"
DS_DIST = "b2505437-cb9a-45f9-b85a-8a6f4868039d"

con = duckdb.connect()
con.execute(open(f"{REF}/views.sql").read())

Q = []

def q(id, intent, question, *, variants=None, template=None, sql=None, expected=None,
      datasets=None, notes=None, caveats=None, response=None):
    item = {"id": id, "intent": intent, "question": question}
    if variants: item["variants"] = variants
    if template: item["answer_template"] = template
    if datasets: item["expected_datasets"] = datasets
    if sql:
        item["sql"] = sql.strip()
        rel = con.execute(sql)
        cols = [d[0] for d in rel.description]
        rows = rel.fetchall()
        def conv(v):
            if isinstance(v, float): return round(v, 2)
            if isinstance(v, (datetime.date, datetime.datetime)): return v.isoformat()
            return v
        item["expected_result"] = {"columns": cols, "rows": [[conv(v) for v in r] for r in rows]}
    if expected: item["expected_answer"] = expected
    if caveats: item["must_mention"] = caveats
    if response: item["expected_response"] = response
    if notes: item["notes"] = notes
    Q.append(item)

# ---------------------------------------------------------------- DISCOVER
q("disc-01", "discover", "Is there any data on maternal and child health spending in Assam?",
  variants={"hi": "क्या असम में मातृ एवं शिशु स्वास्थ्य पर खर्च का कोई डेटा है?",
            "hinglish": "Assam me maternal and child health pe kitna kharcha hua, uska data hai kya?",
            "as": "অসমত মাতৃ আৰু শিশু স্বাস্থ্যৰ খৰচৰ কোনো তথ্য আছেনে?"},
  datasets=[{"dataset_id": DS_MAIN, "rank": 1}, {"dataset_id": DS_SCHEME}, {"dataset_id": DS_DEPT}, {"dataset_id": DS_DIST}],
  expected="Top result is 'MCH Procurement data Assam 2019 to 2025' (public tenders, not budget allocations). Mention the Union Gender Budget Statement in data-ecosystem as a budget-side source.")
q("disc-02", "discover", "District-wise tender data for maternal health in Assam",
  variants={"hinglish": "Assam district wise MCH tender data chahiye"},
  datasets=[{"dataset_id": DS_DIST, "rank": 1}, {"dataset_id": DS_MAIN}, {"dataset_id": DS_MAIN, "resource_id": RES_POLY}],
  expected="District-wise aggregate dataset, plus the tender-level dataset whose district column supports any district cut.")
q("disc-03", "discover", "Infant mortality rate by district in Assam",
  variants={"hi": "असम में जिलेवार शिशु मृत्यु दर"},
  datasets=[{"dataset_id": DS_IMR, "rank": 1}],
  expected="'IMR District-wise Assam 2018-19 to 2022-23'. Mention NFHS-5 district factsheets and HMIS as related health-outcome sources.")
q("disc-04", "discover", "Which dashboards show public spending on mothers and children in Assam?",
  expected="Superset dashboard 'Linking Public Spending to Maternal and Child Health Outcomes in Assam' (https://analytics.civicdataspace.in/superset/dashboard/p/xLKpnNXp6b2/) and the use case page https://civicdataspace.in/usecases/312.")

# ---------------------------------------------------------------- UNDERSTAND
q("und-01", "understand", "What time period does the MCH tender dataset cover?",
  template="dataset_overview",
  sql="""
SELECT min(published_at)::DATE AS first_published, max(published_at)::DATE AS last_published,
       min(contract_date) AS first_contract, max(contract_date) AS last_contract,
       min(result_month) AS first_result_month, max(result_month) AS last_result_month
FROM mch_tenders""",
  caveats=["The title says 2019 to 2025, but some tenders were published in Dec 2017 and 2018; the 2019 to 2025 range refers to when results (contracts) came out.",
           "There is no data for most months; 37 result months contain tenders."])
q("und-02", "understand", "What does one row in the MCH tender dataset represent?",
  template="dataset_overview",
  expected="One MCH-related tender from the Assam e-procurement portal (assamtenders.gov.in), with the bidder and bid value recorded at the results stage. 112 tenders, 112 unique tender IDs. A tender reference (e.g. 'TN 109/1') can be shared by several tenders.")
q("und-03", "understand", "Can I add up the Awarded Value column to get total spending?",
  template="dataset_overview",
  sql="""
SELECT is_awarded, count(*) AS tenders, sum(bid_value_inr) AS sum_bid_value_inr
FROM mch_tenders GROUP BY is_awarded ORDER BY is_awarded DESC""",
  caveats=["No. 'Awarded Value' holds the listed bid's value even for rejected or not-admitted tenders. Sum it only where is_awarded is true (awarded_amount_inr in the view).",
           "One tender, the 500-bed Mother and Child Hospital at GMCH (₹214 crore), is about 80% of all awarded value."])
q("und-04", "understand", "How were tenders identified as maternal and child health related?",
  template="dataset_overview",
  expected="Keyword rules in TENDERS/scripts/mch_tenders.py run on the tender title, reference and work description: core MCH terms (maternity, labour room, newborn, SNCU...), ANC/PNC, immunisation and child health, nutrition and named schemes. Tenders mentioning veterinary/animal husbandry/livestock are excluded. A broader rule also keeps health-department tenders tagged with an MCH scheme or MCH infrastructure words. 100 of the 112 tenders pass the strict rule.",
  sql="SELECT is_mch_strict, count(*) AS tenders FROM mch_tenders GROUP BY 1 ORDER BY 1 DESC")
q("und-05", "understand", "How many tenders could not be assigned to a district?",
  template="dataset_overview",
  sql="SELECT district_geotag_status, count(*) AS tenders FROM mch_tenders GROUP BY 1 ORDER BY 2 DESC",
  caveats=["Districts are inferred from place names in the text, not reported by the portal.",
           "Conflict means two text fields pointed to different districts."])
q("und-06", "understand", "Does this dataset show how much the government budgeted for maternal health?",
  template="dataset_overview",
  expected="No. It covers tenders published on the state e-procurement portal, which is a subset of spending. The use case notes only about 20% of Assam's tenders are published. Budget allocations are in the Union Gender Budget Statement (data-ecosystem/sources/ministry_of_women_and_child_development_mwcd).")
q("und-07", "understand", "What do the scheme codes like LAQSHYA, SOPD and MSDP mean?",
  template="dataset_overview",
  expected="Answer from glossary.json. LAQSHYA = Labour room Quality Improvement Initiative; SOPD = State Owned Priority Development; MSDP = Multi-sectoral Development Programme; HFW = Health and Family Welfare Department (a department tag, not a scheme).")

# ---------------------------------------------------------------- ANALYSE
q("ana-01", "analyse", "How many MCH tenders were awarded in Assam and what was their total value?",
  variants={"hinglish": "Assam me kitne MCH tenders award hue aur total value kitni thi?",
            "hi": "असम में कितने मातृ-शिशु स्वास्थ्य टेंडर दिए गए और उनका कुल मूल्य कितना था?"},
  template="trend",
  sql="""
SELECT count(*) AS tenders_total,
       count(*) FILTER (WHERE is_awarded) AS tenders_awarded,
       sum(awarded_amount_inr) AS awarded_amount_inr,
       round(sum(awarded_amount_inr) / 1e7, 2) AS awarded_amount_crore
FROM mch_tenders""",
  caveats=["Only published tenders on assamtenders.gov.in.", "One ₹214 crore hospital tender is most of the total."])
q("ana-02", "analyse", "How did awarded MCH tender value change year by year?",
  template="trend",
  sql="""
SELECT result_year, count(*) AS tenders, count(*) FILTER (WHERE is_awarded) AS awarded,
       round(coalesce(sum(awarded_amount_inr), 0) / 1e7, 2) AS awarded_crore
FROM mch_tenders GROUP BY 1 ORDER BY 1""",
  caveats=["Year is the year results came out, not when the tender was published.",
           "2020 is dominated by a single ₹214 crore tender; do not describe it as a spending peak without saying so.",
           "Small counts per year: avoid percentage-change language."])
q("ana-03", "analyse", "Which districts received the most awarded MCH tender value?",
  variants={"hinglish": "Sabse zyada MCH tender paisa kaunse district ko mila?"},
  template="cross_region_comparison",
  sql="""
SELECT coalesce(district, 'Not geotagged / conflict') AS district,
       count(*) AS awarded_tenders, round(sum(awarded_amount_inr) / 1e7, 2) AS awarded_crore
FROM mch_tenders WHERE is_awarded
GROUP BY 1 ORDER BY sum(awarded_amount_inr) DESC LIMIT 10""",
  caveats=["Kamrup Metro's total is mainly the GMCH Mother and Child Hospital.",
           "Districts with 1 or 2 tenders should not be ranked as meaningful differences."])
q("ana-04", "analyse", "Which districts lead in awarded MCH value if we exclude the GMCH Mother and Child Hospital?",
  template="cross_region_comparison",
  sql="""
SELECT district, count(*) AS awarded_tenders, round(sum(awarded_amount_inr) / 1e7, 2) AS awarded_crore
FROM mch_tenders
WHERE is_awarded AND tender_id <> '2020_PWBNH_17202_1' AND district IS NOT NULL
GROUP BY 1 ORDER BY sum(awarded_amount_inr) DESC LIMIT 5""")
q("ana-05", "analyse", "Which departments issued the most MCH tenders?",
  template="cross_region_comparison",
  sql="""
SELECT department_top, count(*) AS tenders, count(*) FILTER (WHERE is_awarded) AS awarded,
       round(coalesce(sum(awarded_amount_inr), 0) / 1e7, 2) AS awarded_crore
FROM mch_tenders GROUP BY 1 ORDER BY tenders DESC""",
  caveats=["Bodoland Territorial Council appears under two spellings of its top-level department name.",
           "Health and Family Welfare's awarded value is understated: most of its awards are drug and equipment contracts recorded as ₹0, ₹1 or unit rates (awarded_value_suspect). Compare departments by tender count, not value."])
q("ana-06", "analyse", "Which schemes are most MCH tenders tagged with?",
  template="cross_region_comparison",
  sql="""
SELECT scheme, count(*) AS tenders, count(*) FILTER (WHERE is_awarded) AS awarded
FROM mch_tender_schemes GROUP BY 1 ORDER BY tenders DESC, scheme""",
  caveats=["A tender can carry more than one scheme tag; scheme counts add up to more than the number of tenders.",
           "15 tenders have no scheme tag.",
           "HFW and PWD_NH are department tags, not schemes.",
           "CHD_SCHEME is a false positive for BTC tenders: 'CHD' in 'Director Cum CHD - PWD BTC' is an office name, not the Congenital Heart Disease scheme."])
q("ana-07", "analyse", "What were the five largest awarded MCH tenders?",
  template="dataset_overview",
  sql="""
SELECT tender_id, left(tender_title, 120) AS tender_title, district, contract_date,
       round(awarded_amount_inr / 1e7, 2) AS awarded_crore
FROM mch_tenders WHERE is_awarded ORDER BY awarded_amount_inr DESC LIMIT 5""")
q("ana-08", "analyse", "What share of MCH tenders were rejected or not admitted?",
  template="dataset_overview",
  sql="""
SELECT coalesce(status, 'Missing') AS status, count(*) AS tenders,
       round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM mch_tenders GROUP BY 1 ORDER BY tenders DESC""")
q("ana-09", "analyse", "How long does it take from publishing an MCH tender to signing the contract?",
  template="trend",
  sql="""
SELECT count(*) AS tenders_with_dates,
       round(median(days_publish_to_contract)) AS median_days,
       round(avg(days_publish_to_contract)) AS mean_days,
       min(days_publish_to_contract) AS min_days, max(days_publish_to_contract) AS max_days
FROM mch_tenders WHERE is_awarded AND days_publish_to_contract IS NOT NULL""",
  caveats=["This is publish-to-contract time, not the contract-award disclosure delay (~250 days on average) cited on the use case page; do not present them as the same measure."])
q("ana-10", "analyse", "How many MCH tenders received only one bid?",
  template="dataset_overview",
  sql="""
SELECT bids_received, count(*) AS tenders, count(*) FILTER (WHERE is_awarded) AS awarded
FROM mch_tenders GROUP BY 1 ORDER BY 1""",
  caveats=["Do not draw conclusions about wrongdoing from bid counts."])
q("ana-11", "analyse", "How does MCH procurement split between construction works and goods?",
  template="cross_region_comparison",
  sql="""
SELECT tender_category, count(*) AS tenders, count(*) FILTER (WHERE is_awarded) AS awarded,
       count(*) FILTER (WHERE awarded_value_suspect) AS awarded_value_suspect,
       round(coalesce(sum(awarded_amount_inr), 0) / 1e7, 2) AS awarded_crore
FROM mch_tenders GROUP BY 1 ORDER BY tenders DESC""",
  caveats=["Goods value is not measurable from awarded value: most awarded goods tenders record ₹0, ₹1 or a unit rate. Say the goods figure is a large undercount and give counts instead."])
q("ana-14", "analyse", "How many awarded tenders have an unreliable awarded value?",
  template="dataset_overview",
  sql="""
SELECT tender_category, department_top, count(*) AS awarded_value_suspect,
       round(sum(tender_value_inr) / 1e7, 2) AS estimated_value_crore_where_known,
       count(tender_value_inr) AS with_estimate
FROM mch_tenders WHERE awarded_value_suspect
GROUP BY 1, 2 ORDER BY 3 DESC""")
q("ana-12", "analyse", "How much MCH tender value was awarded in Kokrajhar and by whom?",
  variants={"hinglish": "Kokrajhar me MCH tenders ka kitna paisa award hua?"},
  template="cross_region_comparison",
  sql="""
SELECT department_top, count(*) AS awarded_tenders, round(sum(awarded_amount_inr) / 1e5, 2) AS awarded_lakh
FROM mch_tenders WHERE is_awarded AND district = 'KOKRAJHAR'
GROUP BY 1 ORDER BY awarded_lakh DESC""",
  caveats=["Kokrajhar is in the Bodoland Territorial Region; BTC departments procure separately from state departments."])
q("ana-13", "analyse", "MCH tenders awarded by Indian fiscal year",
  template="trend",
  sql="""
SELECT contract_fiscal_year, count(*) AS awarded_tenders, round(sum(awarded_amount_inr) / 1e7, 2) AS awarded_crore
FROM mch_tenders WHERE is_awarded AND contract_fiscal_year IS NOT NULL
GROUP BY 1 ORDER BY 1""")

# ---------------------------------------------------------------- OUT OF SCOPE
q("oos-01", "out_of_scope", "Did higher MCH spending reduce infant mortality in Dibrugarh?",
  response="Decline the causal claim. This dataset shows tenders, not outcomes, and v1 answers single-dataset questions only. Point to the IMR district-wise dataset and the Superset dashboard, which places tender value next to IMR. The use case itself concludes that higher spending alone does not guarantee better IMR.",
  datasets=[{"dataset_id": DS_IMR}])
q("oos-02", "out_of_scope", "Give me the phone number of the contractor who built the Dhubri MCH wing.",
  response="Decline. The dataset has no contact details, and the engine does not look up personal information about named individuals.")
q("oos-03", "out_of_scope", "How much did Meghalaya spend on maternal health tenders?",
  response="Out of coverage: FemHealth data covers Assam only.")
q("oos-04", "out_of_scope", "Predict how much Assam will spend on MCH tenders in 2027.",
  response="Decline forecasting. Offer the year-wise trend (ana-02) with its caveats instead.")
q("oos-05", "out_of_scope", "Which contractors are corrupt?",
  response="Decline. Procurement records cannot establish wrongdoing. Offer factual views such as single-bid tenders (ana-10) or rejection rates (ana-08), with neutral framing.")

out = {
    "usecase_id": "assam_mch_tenders",
    "version": "1.0",
    "generated_on": datetime.date.today().isoformat(),
    "how_expected_results_were_produced": "Each analyse question's sql was executed with DuckDB against views.sql over TENDERS/data/MCH_tenderdata_Assam_2019_to_2025.csv. Regenerate if the data file changes (see sha256 in dataset_profiles).",
    "language_codes": {"en": "English", "hi": "Hindi", "as": "Assamese", "hinglish": "Hindi-English mix in Latin script"},
    "language_review_status": "Hindi, Assamese and Hinglish variants are machine drafted and need native-speaker review before use as evaluation gold.",
    "questions": Q,
}
json.dump(out, open(f"{REF}/question_bank.json", "w"), ensure_ascii=False, indent=2)
print(len(Q), "questions")
for item in Q:
    if "expected_result" in item:
        print("\n#", item["id"], item["question"]); print(item["expected_result"]["columns"])
        for r in item["expected_result"]["rows"]: print("  ", r)
