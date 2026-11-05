-- Canonical analysis view for the Assam MCH tenders use case (DuckDB).
--
-- The analysis planner should write SQL against `mch_tenders`, not against the
-- raw CSV. The raw headers contain spaces, a trailing colon ("Contract Date :")
-- and a rupee symbol, values use Indian digit grouping ("2,06,34,54,000"), and
-- the "Awarded Value" column holds a bid amount even for rejected tenders and a
-- placeholder or unit rate for many awarded goods contracts.
-- This view fixes all of that once.
--
-- Paths are relative to the repository root. In the query engine, replace the
-- path with the DataSpace resource:
--   bc22644a-e7ff-4791-ac70-98d7322352e5  (MCH_tenderdata_Assam_2019_to_2025.csv)
--
-- The file is loaded with all_varchar=true so that every type conversion below
-- is explicit and does not depend on CSV type sniffing.

CREATE OR REPLACE VIEW mch_tenders AS
WITH raw AS (
    SELECT *
    FROM read_csv(
        'analytics/Assam_MCH_analysis/TENDERS/data/MCH_tenderdata_Assam_2019_to_2025.csv',
        header = true,
        all_varchar = true
    )
),
typed AS (
    SELECT
        -- Identity
        trim("Tender ID")                                             AS tender_id,
        trim(tender_externalreference)                                AS tender_reference,
        trim(tender_title)                                            AS tender_title,
        trim("Work Description")                                      AS work_description,

        -- What was procured
        trim("Tender Category")                                       AS tender_category,   -- Works / Goods / Services
        trim("Tender Type")                                           AS tender_type,       -- Open Tender / Open Limited / Limited / Single
        trim("Form of contract")                                      AS form_of_contract,
        trim("Product Category")                                      AS product_category,

        -- Who procured it
        trim("Department")                                            AS department,        -- full '||'-separated chain
        trim(split_part("Department", '||', 1))                       AS department_top,    -- top-level department
        trim("Organisation Chain")                                    AS organisation_chain,

        -- Where
        trim(location)                                                AS location_text,     -- free text from the portal
        TRY_CAST(TRY_CAST("Pincode" AS DOUBLE) AS INTEGER)            AS pincode,
        CASE
            WHEN "DISTRICT_FINALISED" IS NULL
              OR trim("DISTRICT_FINALISED") IN ('', 'NA', 'CONFLICT') THEN NULL
            -- Align spelling with data-ecosystem/maps (assam_district_2024-11 'dtname')
            WHEN upper(trim("DISTRICT_FINALISED")) = 'SIVSAGAR'       THEN 'SIVASAGAR'
            ELSE upper(trim("DISTRICT_FINALISED"))
        END                                                           AS district,
        CASE
            WHEN "DISTRICT_FINALISED" IS NULL
              OR trim("DISTRICT_FINALISED") IN ('', 'NA')            THEN 'not_geotagged'
            WHEN trim("DISTRICT_FINALISED") = 'CONFLICT'              THEN 'conflict'
            ELSE 'geotagged'
        END                                                           AS district_geotag_status,
        lower(trim("BTC_flag")) = 'true'                              AS is_btc,            -- Bodoland Territorial Council tender

        -- When
        try_strptime(trim("Published Date"),   '%d-%b-%Y %I:%M %p')   AS published_at,
        try_strptime(trim("Bid Opening Date"), '%d-%b-%Y %I:%M %p')   AS bid_opening_at,
        CAST(try_strptime(trim("Contract Date :"), '%d-%b-%Y') AS DATE) AS contract_date,
        trim(month)                                                   AS result_month,      -- 'YYYY_MM' results batch
        TRY_CAST(left(trim(month), 4) AS INTEGER)                     AS result_year,

        -- Money (rupees, not lakh or crore)
        TRY_CAST(replace(trim("Tender Value in ₹"), ',', '') AS DOUBLE) AS tender_value_inr,  -- estimate at publication
        TRY_CAST(trim("Awarded Value") AS DOUBLE)                     AS bid_value_inr,     -- value of the bid listed in this row

        -- Outcome
        trim("Bidder Name")                                           AS bidder_name,
        TRY_CAST(TRY_CAST("No of Bids Received" AS DOUBLE) AS INTEGER) AS bids_received,
        trim("Status")                                                AS status,
        trim("Tender Stage")                                          AS tender_stage,
        lower(trim(is_awarded)) = 'true'                              AS is_awarded,

        -- Classification (see analysis_reference.md)
        NULLIF(trim("Scheme"), '')                                    AS scheme_tags,       -- ';'-separated codes, see glossary.json
        lower(trim(is_mch_strict)) = 'true'                           AS is_mch_strict
    FROM raw
)
SELECT
    *,
    -- Spending measure: only counts money on tenders that were actually awarded.
    CASE WHEN is_awarded THEN bid_value_inr END                       AS awarded_amount_inr,
    -- Awarded tenders whose recorded value is a placeholder or a unit rate, not
    -- the contract value: 0, 1, 375 (per-kit rate)... Almost all are goods and
    -- item-rate drug/equipment contracts. Below ₹1 lakh is treated as suspect.
    is_awarded AND coalesce(bid_value_inr, 0) < 100000                AS awarded_value_suspect,
    -- Indian fiscal year (April to March) of the contract, e.g. '2023-24'.
    CASE WHEN contract_date IS NULL THEN NULL
         WHEN month(contract_date) >= 4
              THEN CAST(year(contract_date) AS VARCHAR) || '-' || right(CAST(year(contract_date) + 1 AS VARCHAR), 2)
         ELSE CAST(year(contract_date) - 1 AS VARCHAR) || '-' || right(CAST(year(contract_date) AS VARCHAR), 2)
    END                                                               AS contract_fiscal_year,
    date_diff('day', CAST(published_at AS DATE), contract_date)       AS days_publish_to_contract
FROM typed;

-- One row per (tender, scheme tag). Use for any per-scheme question: a tender
-- with tags 'LAQSHYA;NHM' appears once under each scheme, so do not add scheme
-- totals together to get an overall total.
CREATE OR REPLACE VIEW mch_tender_schemes AS
SELECT
    t.*,
    trim(s.scheme) AS scheme
FROM mch_tenders AS t,
     unnest(string_split(t.scheme_tags, ';')) AS s(scheme)
WHERE t.scheme_tags IS NOT NULL;
