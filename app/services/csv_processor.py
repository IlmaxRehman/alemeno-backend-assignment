import pandas as pd


def analyze_csv(file_path: str):

    df = pd.read_csv(file_path)

    results = {
        "total_rows": len(df),

        "missing_txn_ids":
            int(df["txn_id"].isna().sum()),

        "missing_categories":
            int(df["category"].isna().sum()),

        "duplicate_txn_ids":
            int(df["txn_id"].duplicated().sum())
    }

    return results