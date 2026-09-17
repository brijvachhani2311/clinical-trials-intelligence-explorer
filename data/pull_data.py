"""
Clinical Trials Intelligence Explorer — Data Acquisition
==========================================================
Pulls clinical trial records from the free, public ClinicalTrials.gov API v2.
No API key required. Respects the API's cursor-based pagination and the
1000-row pageSize cap.

WHY THIS SCOPE:
We pull trials with at least one site located in Germany, across a handful
of major therapeutic areas that overlap with Boehringer Ingelheim's actual
pipeline (respiratory, oncology, cardiometabolic, immunology). This gives
the project a genuine "I built this to understand my own industry better"
story instead of an arbitrary Kaggle download.

USAGE:
    pip install requests pandas
    python pull_data.py

OUTPUT:
    ../data/raw_trials.csv   (one row per study, key fields flattened)

Run this locally — ClinicalTrials.gov blocks automated requests from some
sandboxed/cloud environments, so this needs to run from your own machine.
"""

import requests
import pandas as pd
import time
import json

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

# Therapeutic areas aligned with Boehringer Ingelheim's core pipeline —
# adjust freely, this is just a sensible, defensible starting scope.
CONDITIONS = [
    "COPD",
    "asthma",
    "pulmonary fibrosis",
    "non-small cell lung cancer",
    "type 2 diabetes",
    "cardiovascular disease",
    "rheumatoid arthritis",
]

FIELDS = [
    "NCTId",
    "BriefTitle",
    "OverallStatus",
    "StartDate",
    "PrimaryCompletionDate",
    "CompletionDate",
    "StudyType",
    "Phase",
    "EnrollmentCount",
    "EnrollmentType",
    "LeadSponsorName",
    "LeadSponsorClass",
    "Condition",
    "InterventionType",
    "InterventionName",
    "LocationCountry",
    "LocationCity",
    "LocationFacility",
    "DesignAllocation",
    "DesignInterventionModel",
    "DesignMasking",
]


def flatten_study(study: dict) -> dict:
    """Pull the fields we care about out of the nested API response."""
    protocol = study.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    conditions = protocol.get("conditionsModule", {})
    interventions = protocol.get("armsInterventionsModule", {})
    locations = protocol.get("contactsLocationsModule", {}).get("locations", [])

    de_locations = [
        loc for loc in locations if loc.get("country") == "Germany"
    ]

    return {
        "nct_id": ident.get("nctId"),
        "title": ident.get("briefTitle"),
        "status": status.get("overallStatus"),
        "start_date": status.get("startDateStruct", {}).get("date"),
        "primary_completion_date": status.get("primaryCompletionDateStruct", {}).get("date"),
        "completion_date": status.get("completionDateStruct", {}).get("date"),
        "study_type": design.get("studyType"),
        "phases": ";".join(design.get("phases", []) or []),
        "enrollment_count": design.get("enrollmentInfo", {}).get("count"),
        "enrollment_type": design.get("enrollmentInfo", {}).get("type"),
        "allocation": design.get("designInfo", {}).get("allocation"),
        "intervention_model": design.get("designInfo", {}).get("interventionModel"),
        "masking": design.get("designInfo", {}).get("maskingInfo", {}).get("masking"),
        "lead_sponsor": sponsor.get("leadSponsor", {}).get("name"),
        "lead_sponsor_class": sponsor.get("leadSponsor", {}).get("class"),
        "conditions": ";".join(conditions.get("conditions", []) or []),
        "interventions": ";".join(
            i.get("name", "") for i in interventions.get("interventions", []) or []
        ),
        "n_germany_sites": len(de_locations),
        "germany_cities": ";".join(
            sorted(set(l.get("city", "") for l in de_locations))
        ),
        "n_total_sites": len(locations),
    }


def fetch_condition(condition: str, page_size: int = 100) -> list:
    """Page through all results for one condition, filtered to trials with a German site."""
    results = []
    params = {
        "query.cond": condition,
        "query.locn": "Germany",
        "pageSize": page_size,
        "fields": ",".join(FIELDS),
    }
    page_token = None
    page_num = 0

    while True:
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        studies = data.get("studies", [])
        results.extend(flatten_study(s) for s in studies)
        page_num += 1
        print(f"  [{condition}] page {page_num}: {len(studies)} studies (total so far: {len(results)})")

        page_token = data.get("nextPageToken")
        if not page_token or not studies:
            break
        time.sleep(0.3)  # be polite to a public health infrastructure endpoint

    return results


def main():
    all_rows = []
    for condition in CONDITIONS:
        print(f"Fetching: {condition}")
        rows = fetch_condition(condition)
        for r in rows:
            r["search_condition"] = condition
        all_rows.extend(rows)
        time.sleep(0.5)

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset="nct_id")
    print(f"\nTotal unique studies pulled: {len(df)}")

    out_path = "raw_trials.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")
    print("\nColumn summary:")
    print(df.dtypes)


if __name__ == "__main__":
    main()
