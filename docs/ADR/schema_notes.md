
# The design and structure of data is supposed to be in tiers:
Bronze — raw data exactly as received from the source
             Never transformed, never cleaned
             In this project: raw JSON from CFPB API, landed in S3
             Also: a staging_complaints table in Postgres with a raw_payload JSONB column
             Purpose: you can always answer "where did this number come from"

Silver — cleaned, validated, normalized
             Field names standardized, types cast, bad rows flagged
             In this project: an intermediate step in your Airflow DAG
             Purpose: consistent input for gold-layer aggregation

Gold — business-ready, query-optimized tables
          What analysts, models, and the agent actually read from
          In this project: mart_complaint, mart_complaint_narrative, mart_daily_volume
          Purpose: fast, reliable, well-documented answers to real questions

# Relevant Columns (Complaints without narratives):

complaint_id — text, primary key. Why text not integer? CFPB IDs look numeric but you should never do arithmetic on them — treating them as text prevents accidental math and is safer if the format ever changes
 
date_received — date (not timestamp — CFPB only publishes date-level granularity, no time of day)

date_sent_to_company — date, nullable — complaints still in progress won't have this yet

product — text.

subproduct — text, nullable (not all complaints have a subproduct)

issue — text

subissue — text, nullable

company — text

state — char(2), nullable (some complaints have no state)

zip3 — char(3), nullable. CFPB publishes only the first 3 digits of ZIP code, not full ZIP. Full ZIP is never available. Any downstream code that tries to do precise geographic lookup will fail — this is a known, documented limitation.

submitted_via — text (web, phone, referral, etc. — low cardinality from your Day 5 exploration)

company_response — text (the full response string, e.g. "Closed with explanation")

timely_response — boolean. This is your urgency classifier's ground truth label. In the raw data it's "Yes"/"No" — cast it to true/false here so models can consume it directly without string parsing

-- Custom Fields:

response_lag_days — integer, nullable. This is date_sent_to_company - date_received in days.

ingested_at — timestamp, default now(). When did this row enter your system? Useful for debugging pipeline runs and for your audit trail.

-- Edge Cases:

Edge case 1: date_sent_to_company IS NULL
  → complaint is still in progress (company hasn't responded yet,
    and 15-day auto-publish hasn't triggered)
  → response_lag_days = NULL
  → models must handle NULL explicitly — never fill with 0 or mean
    (0 would mean "instant response", mean would fabricate a number)
  → in the urgency classifier, NULL lag = "unknown, complaint open"
    which is itself a signal worth encoding as a separate boolean flag

Edge case 2: date_sent_to_company < date_received
  → data quality issue — logically impossible
  → response_lag_days = NULL, flag in complaint_exceptions table
  → assert this doesn't happen in your Airflow data-quality check (Day 14)

Edge case 3: response_lag_days > 60
  → possible but suspicious — note as a data quality flag, not an error
  → keep the value, don't null it out, but worth surfacing in exploration


# Relevant Columns (Complaints with narratives - This is a separate table for complaints with narrative):
complaint_id — text, primary key, also a foreign key to mart_complaint.complaint_id. Write this constraint down — it enforces that you can never have a narrative row without a corresponding complaint row.

narrative_text — text, nullable. Nullable because this table will actually have a row for every complaint (has_narrative=false rows still exist here) — see next point

narrative_len — integer, nullable. Character count of the narrative. Pre-computed here so you never have to len() in application code. NULL when no narrative.

has_narrative — boolean, not null, default false.
    Option B: Store a row for every complaint, has_narrative = true/false
    → Slightly more rows, but every complaint_id has exactly one narrative row
    → "Does X have a narrative?" is just WHERE complaint_id = X — no JOIN needed
    → The agent and models can check has_narrative directly without outer joins

