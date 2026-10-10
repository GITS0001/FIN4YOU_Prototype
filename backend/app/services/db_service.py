from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.models import Profile, Transaction, CopilotRequest
from app.schemas.financial import FinancialProfile
from app.schemas.financial import Transaction as SchemaTransaction
from app.supabase_config import is_supabase_configured
from app.services.supabase_repository import supabase_repository

def get_user_profile(db: Optional[Session], user_id: Any) -> Optional[FinancialProfile]:
    """
    Retrieves user profile. Uses Supabase repository if configured,
    otherwise queries the SQLAlchemy session for local tests.
    """
    if is_supabase_configured():
        sp_profile = supabase_repository.get_profile(str(user_id))
        if sp_profile:
            fp_priorities = sp_profile.get("financial_priorities") or ""
            if isinstance(fp_priorities, str):
                priorities = [p.strip() for p in fp_priorities.split("|") if p.strip()]
            else:
                priorities = list(fp_priorities)

            fp_protect = sp_profile.get("expense_categories_to_protect") or ""
            protect = [p.strip() for p in fp_protect.split("|") if p.strip()] if isinstance(fp_protect, str) else list(fp_protect)

            fp_reduce = sp_profile.get("expense_categories_user_is_willing_to_reduce") or ""
            reduce_cats = [p.strip() for p in fp_reduce.split("|") if p.strip()] if isinstance(fp_reduce, str) else list(fp_reduce)

            fp_stop = sp_profile.get("expense_categories_user_is_willing_to_stop") or ""
            stop_cats = [p.strip() for p in fp_stop.split("|") if p.strip()] if isinstance(fp_stop, str) else list(fp_stop)

            fp_methods = sp_profile.get("payment_methods_user_will_consider") or ""
            methods = [p.strip() for p in fp_methods.split("|") if p.strip()] if isinstance(fp_methods, str) else list(fp_methods)

            return FinancialProfile(
                user_id=str(sp_profile.get("user_id")),
                home_currency=sp_profile.get("home_currency", "USD"),
                current_available_balance=float(sp_profile.get("current_available_balance", 0.0)),
                minimum_balance_to_keep=float(sp_profile.get("minimum_balance_to_keep", 0.0)),
                financial_priorities=priorities,
                expense_categories_to_protect=protect,
                expense_categories_user_is_willing_to_reduce=reduce_cats,
                expense_categories_user_is_willing_to_stop=stop_cats,
                payment_methods_user_will_consider=methods,
                max_installment_months=sp_profile.get("max_installment_months", 12)
            )

    if db is not None:
        try:
            uid_int = int(user_id) if str(user_id).isdigit() else user_id
            db_profile = db.query(Profile).filter(Profile.user_id == uid_int).first()
        except Exception:
            db_profile = None

        if not db_profile:
            return None

        return FinancialProfile(
            user_id=str(db_profile.user_id),
            home_currency=db_profile.home_currency,
            current_available_balance=db_profile.current_available_balance,
            minimum_balance_to_keep=db_profile.minimum_balance_to_keep,
            financial_priorities=db_profile.financial_priorities.split("|") if db_profile.financial_priorities else [],
            expense_categories_to_protect=db_profile.expense_categories_to_protect.split("|") if db_profile.expense_categories_to_protect else [],
            expense_categories_user_is_willing_to_reduce=db_profile.expense_categories_user_is_willing_to_reduce.split("|") if db_profile.expense_categories_user_is_willing_to_reduce else [],
            expense_categories_user_is_willing_to_stop=db_profile.expense_categories_user_is_willing_to_stop.split("|") if db_profile.expense_categories_user_is_willing_to_stop else [],
            payment_methods_user_will_consider=db_profile.payment_methods_user_will_consider.split("|") if db_profile.payment_methods_user_will_consider else [],
            max_installment_months=db_profile.max_installment_months
        )

    return None

def get_user_transactions(db: Optional[Session], user_id: Any) -> List[SchemaTransaction]:
    """
    Retrieves user transactions. Uses Supabase repository if configured,
    otherwise queries the SQLAlchemy session for local tests.
    """
    if is_supabase_configured():
        sp_txs = supabase_repository.get_transactions(str(user_id), limit=1000)
        transactions = []
        for t in sp_txs:
            ev_date = t.get("event_date")
            if isinstance(ev_date, str):
                ev_date = datetime.strptime(ev_date, "%Y-%m-%d").date()

            set_date = t.get("settlement_date")
            if isinstance(set_date, str):
                set_date = datetime.strptime(set_date, "%Y-%m-%d").date()

            transactions.append(SchemaTransaction(
                transaction_id=t.get("transaction_id"),
                user_id=str(t.get("user_id")),
                event_type=t.get("event_type"),
                description=t.get("description"),
                category=t.get("category"),
                direction=t.get("direction"),
                amount=float(t.get("amount", 0.0)),
                currency=t.get("currency", "USD"),
                event_date=ev_date,
                settlement_date=set_date,
                status=t.get("status", "SETTLED"),
                flexibility=t.get("flexibility", "variable"),
                ml_confidence=t.get("ml_confidence"),
                ml_status=t.get("ml_status"),
                ml_confidence_level=t.get("ml_confidence_level")
            ))
        if transactions:
            return transactions

    if db is not None:
        try:
            uid_int = int(user_id) if str(user_id).isdigit() else user_id
            db_transactions = db.query(Transaction).filter(Transaction.user_id == uid_int).all()
        except Exception:
            db_transactions = []

        transactions = []
        for t in db_transactions:
            transactions.append(SchemaTransaction(
                transaction_id=t.transaction_id,
                user_id=str(t.user_id),
                event_type=t.event_type,
                description=t.description,
                category=t.category,
                direction=t.direction,
                amount=t.amount,
                currency=t.currency,
                event_date=t.event_date,
                settlement_date=t.settlement_date,
                status=t.status,
                flexibility=t.flexibility,
                ml_confidence=t.ml_confidence,
                ml_status=t.ml_status,
                ml_confidence_level=t.ml_confidence_level
            ))
        return transactions

    return []
