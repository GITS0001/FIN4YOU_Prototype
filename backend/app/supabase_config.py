import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("fin4you.supabase")

# Environment configurations
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()

# Publishable key (client-safe anon key)
SUPABASE_PUBLISHABLE_KEY = (
    os.getenv("SUPABASE_PUBLISHABLE_KEY") or
    os.getenv("SUPABASE_ANON_KEY") or
    ""
).strip()

# Secret service-role key (server-side only, never send to frontend)
SUPABASE_SECRET_KEY = (
    os.getenv("SUPABASE_SECRET_KEY") or
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or
    ""
).strip()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

class SupabaseConfigError(RuntimeError):
    """Raised when required Supabase configuration is missing or invalid."""
    pass

def validate_supabase_env():
    """
    Validates Supabase configuration.
    In production mode, raises SupabaseConfigError if required credentials are missing.
    Never silently falls back to SQLite in production.
    """
    is_prod = ENVIRONMENT == "production"
    has_url = bool(SUPABASE_URL)
    has_key = bool(SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY)

    if is_prod and (not has_url or not has_key):
        missing = []
        if not has_url:
            missing.append("SUPABASE_URL")
        if not has_key:
            missing.append("SUPABASE_SECRET_KEY (or SUPABASE_PUBLISHABLE_KEY)")
        raise SupabaseConfigError(
            f"CRITICAL CONFIGURATION ERROR: Missing required Supabase environment variable(s) "
            f"in production: {', '.join(missing)}. "
            f"Production persistence requires valid Supabase credentials. Silent fallback to SQLite is disallowed."
        )

def is_supabase_configured() -> bool:
    """Returns True if Supabase URL and at least one key are provided."""
    return bool(SUPABASE_URL and (SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY))

_supabase_client_instance = None
_supabase_admin_instance = None

def get_supabase_client(use_secret_key: bool = False):
    """
    Returns an official Supabase client instance using the appropriate key.

    Args:
        use_secret_key: If True, uses SUPABASE_SECRET_KEY for server-privileged operations.
                        If False, uses SUPABASE_PUBLISHABLE_KEY.
    """
    global _supabase_client_instance, _supabase_admin_instance

    validate_supabase_env()

    if not is_supabase_configured():
        if ENVIRONMENT == "production":
            raise SupabaseConfigError("Supabase is not configured in production mode.")
        return None

    try:
        from supabase import create_client, Client
    except ImportError:
        raise SupabaseConfigError("supabase-py library is not installed. Please run: pip install supabase")

    if use_secret_key:
        if not SUPABASE_SECRET_KEY:
            # Fall back to publishable if secret key not provided, but log warning
            logger.warning("SUPABASE_SECRET_KEY not set; using SUPABASE_PUBLISHABLE_KEY for client.")
            key_to_use = SUPABASE_PUBLISHABLE_KEY
        else:
            key_to_use = SUPABASE_SECRET_KEY

        if _supabase_admin_instance is None:
            _supabase_admin_instance = create_client(SUPABASE_URL, key_to_use)
        return _supabase_admin_instance
    else:
        key_to_use = SUPABASE_PUBLISHABLE_KEY or SUPABASE_SECRET_KEY
        if _supabase_client_instance is None:
            _supabase_client_instance = create_client(SUPABASE_URL, key_to_use)
        return _supabase_client_instance

def reset_client_instances():
    """Resets cached client instances (primarily for testing)."""
    global _supabase_client_instance, _supabase_admin_instance
    _supabase_client_instance = None
    _supabase_admin_instance = None
