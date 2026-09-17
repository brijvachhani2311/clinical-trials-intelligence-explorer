# Clinical Trials Intelligence Explorer

An end-to-end analytics project on clinical trials conducted in Germany,
across therapeutic areas relevant to major pharma R&D pipelines — built to
demonstrate SQL, Python, dashboarding, and LLM-augmented analytics skills
on a genuinely relevant, non-tutorial dataset.

## Why this project

Most portfolio projects use the same recycled Kaggle datasets (Titanic, HR
attrition, Netflix). This one uses live, public, real-world clinical trials
data — the kind of dataset that's directly relevant to pharma/healthcare
analyst roles — and pairs standard analytics with a natural-language query
layer, which is the fastest-growing skill gap in analyst hiring right now.

## Roadmap

- [ ] **Week 1 — Data acquisition & cleaning**
  - Run `data/pull_data.py` locally to pull trial records
  - Clean nulls, standardize date formats, dedupe
  - Load into a local SQLite/Postgres DB
- [ ] **Week 2 — SQL & EDA**
  - Answer business questions with SQL (joins, window functions, CTEs)
  - Python EDA: phase duration distributions, sponsor patterns,
    enrollment trends, therapeutic-area comparisons
- [ ] **Week 3 — Dashboard**
  - Interactive dashboard (Power BI or Streamlit)
- [ ] **Week 4 — LLM query layer**
  - Natural-language question → SQL query → answer + chart
  - Document validation: where the LLM got it right, where it didn't
- [ ] **Week 5 — Deploy & document**
  - Deploy dashboard/app publicly
  - Write the case study
  - Publish on GitHub + LinkedIn

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
