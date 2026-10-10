"""
FIN4YOU - Live Supabase Connectivity Verification Script
Safely tests live Supabase credentials without printing secret values or executing destructive queries.
"""
import os
import sys

# Ensure backend module is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.supabase_config import is_supabase_configured, get_supabase_client, ENVIRONMENT
from app.services.supabase_repository import supabase_repository, SupabaseRepositoryError

def test_live_supabase():
    print("=" * 60)
    print("FIN4YOU Supabase Live Connectivity Check")
    print("=" * 60)
    print(f"Environment Mode: {ENVIRONMENT}")

    if not is_supabase_configured():
        print("[STATUS] Supabase is NOT CONFIGURED in your .env.")
        print("Required environment variables in .env:")
        print("  - SUPABASE_URL=https://[project-ref].supabase.co")
        print("  - SUPABASE_SECRET_KEY=sb_secret_...")
        print("  - SUPABASE_PUBLISHABLE_KEY=sb_publishable_...")
        print("The backend is currently operating in local SQLite fallback mode.")
        return False

    print("[INFO] Credentials detected in environment. Attempting live handshake...")
    try:
        client = get_supabase_client(use_secret_key=True)
        if not client:
            print("[ERROR] Failed to instantiate Supabase client.")
            return False

        # Query Profiles table to check connectivity and schema presence
        res = client.table("Profiles").select("id").limit(1).execute()
        print(f"[SUCCESS] Successfully queried 'Profiles' table over HTTPS!")
        print(f"[STATUS] Live Supabase connection is VERIFIED and OPERATIONAL.")
        return True
    except Exception as e:
        print(f"[ERROR] Live connection check failed: {type(e).__name__}: {e}")
        print("Please check that your project is running and docs/supabase_schema_migration.sql has been applied.")
        return False

if __name__ == "__main__":
    success = test_live_supabase()
    sys.exit(0 if success else 1)
