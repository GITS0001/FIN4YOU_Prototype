import os
import pandas as pd
from pathlib import Path

def generate_prototype_subset():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    proto_dir = base_dir / "data" / "prototype"

    proto_dir.mkdir(parents=True, exist_ok=True)

    # Pick some users from sample_requests (01-05) and some from requests (26-30)
    users_to_keep = {
        "user_01", "user_02", "user_03", "user_04", "user_05",
        "user_26", "user_27", "user_28", "user_29", "user_30"
    }

    # Files that contain user_id directly
    user_linked_files = [
        "financial_events.csv",
        "financial_profiles.csv",
        "requests.csv",
        "messages.csv",
        "images.csv",
        "sample_requests.csv"
    ]

    valid_request_ids = set()

    for file_name in user_linked_files:
        raw_path = raw_dir / file_name
        proto_path = proto_dir / file_name
        if raw_path.exists():
            df = pd.read_csv(raw_path)
            if "user_id" in df.columns:
                subset = df[df["user_id"].isin(users_to_keep)]
                subset.to_csv(proto_path, index=False)
                print(f"Subset created for {file_name} ({len(subset)} rows)")
                
                # Collect valid request IDs
                if "request_id" in subset.columns:
                    valid_request_ids.update(subset["request_id"].dropna().unique())

    # Files that need to be filtered by request_id
    request_linked_files = ["output.csv", "request_payment_options.csv"]
    for file_name in request_linked_files:
        raw_path = raw_dir / file_name
        proto_path = proto_dir / file_name
        if raw_path.exists():
            df = pd.read_csv(raw_path)
            if "request_id" in df.columns:
                subset = df[df["request_id"].isin(valid_request_ids)]
                subset.to_csv(proto_path, index=False)
                print(f"Subset created for {file_name} ({len(subset)} rows)")

    # Exchange rates can be copied entirely
    rates_path = raw_dir / "exchange_rates.csv"
    if rates_path.exists():
        df_rates = pd.read_csv(rates_path)
        df_rates.to_csv(proto_dir / "exchange_rates.csv", index=False)
        print(f"Subset created for exchange_rates.csv ({len(df_rates)} rows)")

if __name__ == "__main__":
    generate_prototype_subset()
