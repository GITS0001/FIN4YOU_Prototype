from app.ingestion.loader import DataLoader

def run_pipeline(data_dir: str):
    print(f"Running Data Foundation Pipeline for directory: {data_dir}")
    loader = DataLoader(data_dir)
    
    print("Loading and cleaning events...")
    events = loader.load_events()
    print(f"-> Standardized {len(events)} events.")
    
    print("Loading and cleaning profiles...")
    profiles = loader.load_profiles()
    print(f"-> Standardized {len(profiles)} profiles.")
    
    print("Loading and cleaning requests...")
    requests = loader.load_requests()
    print(f"-> Standardized {len(requests)} requests.")
    
    return events, profiles, requests

if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    proto_dir = base_dir / "data" / "prototype"
    run_pipeline(str(proto_dir))
