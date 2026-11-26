# Responsible data use

The FemHealth Data Collaborative publishes data and analysis on the health of women and girls in Assam so that officials, civil society organisations, researchers and journalists can make better decisions. These rules apply to everyone who adds to, analyses or republishes data from this repository, and to answers produced by the FemHealth query engine.

They are Stage 9 of the [SOP on dataset transformation and tagging](data-ecosystem/docs/%5BWIP%5D%20SOP_dataset_transformation_and_tagging.md), which applies them at every step from collecting data to publishing it.

## Rules

| Area | Rule |
| --- | --- |
| Personal data | Publish aggregates by district, scheme or department. Names of individuals that appear in official public records (for example sole-proprietor contractors in tender data) may stay in record-level files but are never ranked, profiled or highlighted. Household and person-level survey files (HCES, TUS, PLFS) are published only as aggregates. |
| Small numbers | Counts below 10 in survey-based indicators are suppressed. For administrative records such as tenders, small counts are shown but not ranked or turned into percentage changes. |
| Sensitive topics | Mental health, gender-based violence and reproductive health results are framed with care and reviewed by the UNICEF focal point before release. |
| Claims | Show associations, not causes. "Higher spending did not coincide with lower infant mortality" is fine; "spending failed to reduce infant mortality" is not. |
| Wrongdoing | Procurement patterns (single bids, rejections, delays) are reported neutrally and never presented as evidence of corruption. |
| Coverage | Every output states what the data does not cover, and that an absence of records is not an absence of activity. |
| Attribution | Third-party data keeps its original licence and credits the original publisher, not just this repository. |
| Law | Handling complies with India's Digital Personal Data Protection Act, 2023, and each source's terms of use. |

## Limits of the data

Anyone using this data should keep these limits in mind:

- **Coverage is partial.** Many sources cover only what was published. For example, the tender data includes only tenders on the Assam e-procurement portal, which the use case estimates at about 20% of all tenders.
- **Tags and districts are inferred.** Whether a record is "maternal and child health related", which scheme it belongs to, and which district it is in are often derived from keywords and place names, not reported by the source. Each use case documents its error checks and known mistakes.
- **Values can be placeholders.** Some source fields hold placeholder or per-unit values rather than totals. Dataset profiles and query engine references flag these; check them before adding numbers up.
- **Surveys and administrative data differ.** Survey estimates have sampling error; administrative records reflect what was reported, with reporting gaps and delays.
- **Boundaries change.** Districts and revenue circles in Assam were redrawn in recent years; compare areas across time only after aligning boundaries.
- **This is decision support.** Analyses here should inform decisions alongside local knowledge, never replace it. A low figure must not be used on its own to justify withdrawing services from an area.

## Privacy

Most datasets here are population-level statistics, administrative records or procurement records already published by government sources. Where a file contains information about identifiable people, it is because an official source published it, and the rules above limit how it is used. To report personal data that should not be here, follow [SECURITY.md](SECURITY.md).
