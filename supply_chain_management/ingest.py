import os
import pandas as pd
import numpy as np
import minsearch
from collections import Counter

# Define the data path with a default value
DATA_PATH = os.getenv("DATA_PATH", "../Data/supplier_contracts_dataset.csv")


def load_index(data_path=DATA_PATH):
    df = pd.read_csv(data_path)
    df = df.replace({np.nan: None})

    df = df.rename(columns={'supplier_id':'id'})
    # # Convert only the relevant text-based fields to string
    text_fields = ['supplier_name', 'supplier_type', 'risk_level',
       'compliance_issues', 'key_terms', 'past_performance',
       'negotiate_recommendation', 'supply_chain_disruption',
       'quality_metrics', 'cost_metrics']

    # Ensure the specified text fields are strings
    for field in text_fields:
        df[field] = df[field].astype(str)

    documents = df.to_dict(orient="records")


    # Create an index
    index = minsearch.Index(
        text_fields=text_fields,
        keyword_fields=["id"]
    )

    # Fit the index with the documents
    index.fit(documents)

    return index