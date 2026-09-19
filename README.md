# Clinical Trials Intelligence Explorer

**🔗 [Live Dashboard](https://clinical-trials-intelligence-explorer-76auropkugzkzas8oynj5w.streamlit.app/)** | **📊 [GitHub Repo](https://github.com/brijvachhani2311/clinical-trials-intelligence-explorer)**

An end-to-end analytics project on clinical trials conducted in Germany,
across therapeutic areas relevant to major pharma R&D pipelines — built to
demonstrate SQL, Python, dashboarding, and LLM-augmented analytics skills
on a genuinely relevant, non-tutorial dataset.

## Key findings

- **Non-small cell lung cancer trials terminate early at ~15%** — more
  than double the rate for COPD or type 2 diabetes (~6%). Consistent with
  oncology trials' higher exposure to futility stops and a fast-moving
  competitive landscape.
- **Boehringer Ingelheim is the #3 sponsor** by trial count among trials
  with a German site (243 trials), behind AstraZeneca and Novartis.
- **Berlin, Hamburg, and Leipzig** are the top German clinical trial hubs
  by site count.
- A search for "cardiovascular disease" on ClinicalTrials.gov initially
  pulled in 4,428 trials via related-term expansion — only 7.9% of which
  actually mentioned a cardio-related condition themselves (the rest
  included things like multiple myeloma studies). Caught and filtered
  down to 2,850 genuine matches — see `data/trials_clean_v1.csv` and the
  cleaning logic in the EDA notebook.

## Why this project

Most portfolio projects use the same recycled Kaggle datasets (Titanic, HR
attrition, Netflix). This one uses live, public, real-world clinical trials
data — the kind of dataset that's directly relevant to pharma/healthcare
analyst roles — and pairs standard analytics with a natural-language query
layer, which is the fastest-growing skill gap in analyst hiring right now.

## Roadmap

- [x] **Week 1 — Data acquisition & cleaning**
  - Pulled 7,506 trials from ClinicalTrials.gov API v2, cleaned to 5,928
    after fixing a broad-search-term data quality issue (documented below)
- [x] **Week 2 — SQL & EDA**
  - Normalized schema (5 tables), analytical SQL with joins/CTEs/window
    functions — see `sql/analysis_queries.sql`
  - Full EDA notebook with 5 findings — see `notebooks/eda.ipynb`
- [x] **Week 3 — Dashboard**
  - Interactive Streamlit dashboard, deployed live (link above)
  - Power BI version — in progress
- [ ] **Week 4 — LLM query layer**
  - Natural-language question → SQL query → answer + chart
  - Document validation: where the LLM got it right, where it didn't
- [ ] **Week 5 — Deploy & document**
  - Write the case study
  - Publish on LinkedIn

## Setup

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cd data
python pull_data.py
```

This runs from your own machine — ClinicalTrials.gov blocks automated
requests from some sandboxed cloud environments.

## Project structure

```
clinical-trials-intel/
├── data/           # raw + cleaned datasets, acquisition script
├── notebooks/       # EDA notebooks
├── sql/              # schema + analysis queries
├── app/               # dashboard / Streamlit app
└── docs/               # case study write-up
```
