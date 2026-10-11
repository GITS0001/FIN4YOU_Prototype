"""
Artha AI Merchant & App Intelligence Registry
=============================================
Maps known consumer apps and merchants (Myntra, Amazon, Swiggy, Blinkit, Uber, Ola, etc.)
to standardized financial categories, display names, and flexibility tags.
Guarantees deterministic, accurate categorization and detailed app-level spending insights.
"""
import re
from typing import Optional, Dict, Any, List

# Standardized merchant & app knowledge base
MERCHANT_REGISTRY: Dict[str, Dict[str, str]] = {
    # ─── Shopping (e-commerce, fashion, electronics, retail) ─────────────────
    "myntra": {"category": "shopping", "display_name": "Myntra", "flexibility": "discretionary"},
    "amazon": {"category": "shopping", "display_name": "Amazon", "flexibility": "discretionary"},
    "flipkart": {"category": "shopping", "display_name": "Flipkart", "flexibility": "discretionary"},
    "ajio": {"category": "shopping", "display_name": "Ajio", "flexibility": "discretionary"},
    "meesho": {"category": "shopping", "display_name": "Meesho", "flexibility": "discretionary"},
    "nykaa": {"category": "shopping", "display_name": "Nykaa", "flexibility": "discretionary"},
    "zara": {"category": "shopping", "display_name": "Zara", "flexibility": "discretionary"},
    "tata cliq": {"category": "shopping", "display_name": "Tata CLiQ", "flexibility": "discretionary"},
    "tatacliq": {"category": "shopping", "display_name": "Tata CLiQ", "flexibility": "discretionary"},
    "croma": {"category": "shopping", "display_name": "Croma", "flexibility": "discretionary"},
    "reliance digital": {"category": "shopping", "display_name": "Reliance Digital", "flexibility": "discretionary"},
    "decathlon": {"category": "shopping", "display_name": "Decathlon", "flexibility": "discretionary"},
    "lenskart": {"category": "shopping", "display_name": "Lenskart", "flexibility": "discretionary"},
    "h&m": {"category": "shopping", "display_name": "H&M", "flexibility": "discretionary"},
    "westside": {"category": "shopping", "display_name": "Westside", "flexibility": "discretionary"},
    "ikea": {"category": "shopping", "display_name": "IKEA", "flexibility": "discretionary"},
    "shoppers stop": {"category": "shopping", "display_name": "Shoppers Stop", "flexibility": "discretionary"},
    "pantaloons": {"category": "shopping", "display_name": "Pantaloons", "flexibility": "discretionary"},
    "urbanic": {"category": "shopping", "display_name": "Urbanic", "flexibility": "discretionary"},
    "snitch": {"category": "shopping", "display_name": "Snitch", "flexibility": "discretionary"},
    "bewakoof": {"category": "shopping", "display_name": "Bewakoof", "flexibility": "discretionary"},
    "puma": {"category": "shopping", "display_name": "Puma", "flexibility": "discretionary"},
    "nike": {"category": "shopping", "display_name": "Nike", "flexibility": "discretionary"},
    "adidas": {"category": "shopping", "display_name": "Adidas", "flexibility": "discretionary"},

    # ─── Food & Dining & Quick Commerce ─────────────────────────────────────
    "blinkit": {"category": "food", "display_name": "Blinkit", "flexibility": "discretionary"},
    "swiggy": {"category": "food", "display_name": "Swiggy", "flexibility": "discretionary"},
    "zomato": {"category": "food", "display_name": "Zomato", "flexibility": "discretionary"},
    "zepto": {"category": "food", "display_name": "Zepto", "flexibility": "discretionary"},
    "instamart": {"category": "food", "display_name": "Instamart", "flexibility": "discretionary"},
    "bigbasket": {"category": "food", "display_name": "BigBasket", "flexibility": "essential"},
    "bb daily": {"category": "food", "display_name": "BBDaily", "flexibility": "essential"},
    "dmart": {"category": "food", "display_name": "DMart", "flexibility": "essential"},
    "eatclub": {"category": "food", "display_name": "EatClub", "flexibility": "discretionary"},
    "mcdonalds": {"category": "food", "display_name": "McDonald's", "flexibility": "discretionary"},
    "mcdonald": {"category": "food", "display_name": "McDonald's", "flexibility": "discretionary"},
    "dominos": {"category": "food", "display_name": "Domino's", "flexibility": "discretionary"},
    "pizza hut": {"category": "food", "display_name": "Pizza Hut", "flexibility": "discretionary"},
    "starbucks": {"category": "food", "display_name": "Starbucks", "flexibility": "discretionary"},
    "kfc": {"category": "food", "display_name": "KFC", "flexibility": "discretionary"},
    "burger king": {"category": "food", "display_name": "Burger King", "flexibility": "discretionary"},
    "subway": {"category": "food", "display_name": "Subway", "flexibility": "discretionary"},
    "haldiram": {"category": "food", "display_name": "Haldiram's", "flexibility": "discretionary"},
    "dunzo": {"category": "food", "display_name": "Dunzo", "flexibility": "discretionary"},
    "chaayos": {"category": "food", "display_name": "Chaayos", "flexibility": "discretionary"},
    "chai point": {"category": "food", "display_name": "Chai Point", "flexibility": "discretionary"},
    "barbeque nation": {"category": "food", "display_name": "Barbeque Nation", "flexibility": "discretionary"},

    # ─── Travel & Commute & Transit ─────────────────────────────────────────
    "uber": {"category": "travel", "display_name": "Uber", "flexibility": "variable"},
    "ola": {"category": "travel", "display_name": "Ola", "flexibility": "variable"},
    "rapido": {"category": "travel", "display_name": "Rapido", "flexibility": "variable"},
    "irctc": {"category": "travel", "display_name": "IRCTC", "flexibility": "variable"},
    "makemytrip": {"category": "travel", "display_name": "MakeMyTrip", "flexibility": "discretionary"},
    "mmt": {"category": "travel", "display_name": "MakeMyTrip", "flexibility": "discretionary"},
    "indigo": {"category": "travel", "display_name": "IndiGo", "flexibility": "discretionary"},
    "air india": {"category": "travel", "display_name": "Air India", "flexibility": "discretionary"},
    "spicejet": {"category": "travel", "display_name": "SpiceJet", "flexibility": "discretionary"},
    "akasa": {"category": "travel", "display_name": "Akasa Air", "flexibility": "discretionary"},
    "vistara": {"category": "travel", "display_name": "Vistara", "flexibility": "discretionary"},
    "redbus": {"category": "travel", "display_name": "redBus", "flexibility": "variable"},
    "yatra": {"category": "travel", "display_name": "Yatra", "flexibility": "discretionary"},
    "cleartrip": {"category": "travel", "display_name": "Cleartrip", "flexibility": "discretionary"},
    "goibibo": {"category": "travel", "display_name": "Goibibo", "flexibility": "discretionary"},
    "fastag": {"category": "travel", "display_name": "FASTag Toll", "flexibility": "variable"},
    "metro": {"category": "travel", "display_name": "Metro Rail", "flexibility": "essential"},
    "petrol": {"category": "travel", "display_name": "Fuel / Petrol", "flexibility": "essential"},
    "fuel": {"category": "travel", "display_name": "Fuel", "flexibility": "essential"},
    "hpcl": {"category": "travel", "display_name": "HPCL Fuel", "flexibility": "essential"},
    "bpcl": {"category": "travel", "display_name": "BPCL Fuel", "flexibility": "essential"},
    "iocl": {"category": "travel", "display_name": "IOCL Fuel", "flexibility": "essential"},
    "shell": {"category": "travel", "display_name": "Shell Fuel", "flexibility": "essential"},

    # ─── Entertainment & Digital Subscriptions ──────────────────────────────
    "netflix": {"category": "entertainment", "display_name": "Netflix", "flexibility": "discretionary"},
    "spotify": {"category": "entertainment", "display_name": "Spotify", "flexibility": "discretionary"},
    "hotstar": {"category": "entertainment", "display_name": "Disney+ Hotstar", "flexibility": "discretionary"},
    "disney": {"category": "entertainment", "display_name": "Disney+", "flexibility": "discretionary"},
    "prime video": {"category": "entertainment", "display_name": "Amazon Prime Video", "flexibility": "discretionary"},
    "youtube": {"category": "entertainment", "display_name": "YouTube Premium", "flexibility": "discretionary"},
    "bookmyshow": {"category": "entertainment", "display_name": "BookMyShow", "flexibility": "discretionary"},
    "pvr": {"category": "entertainment", "display_name": "PVR Cinemas", "flexibility": "discretionary"},
    "inox": {"category": "entertainment", "display_name": "INOX Cinemas", "flexibility": "discretionary"},
    "apple.com/bill": {"category": "entertainment", "display_name": "Apple Services", "flexibility": "discretionary"},
    "google play": {"category": "entertainment", "display_name": "Google Play", "flexibility": "discretionary"},
    "sony liv": {"category": "entertainment", "display_name": "SonyLIV", "flexibility": "discretionary"},
    "sonyliv": {"category": "entertainment", "display_name": "SonyLIV", "flexibility": "discretionary"},
    "zee5": {"category": "entertainment", "display_name": "ZEE5", "flexibility": "discretionary"},

    # ─── Utilities, Telecom & Household Bills ───────────────────────────────
    "airtel": {"category": "utilities", "display_name": "Airtel", "flexibility": "essential"},
    "jio": {"category": "utilities", "display_name": "Jio", "flexibility": "essential"},
    "vi": {"category": "utilities", "display_name": "Vodafone Idea", "flexibility": "essential"},
    "vodafone": {"category": "utilities", "display_name": "Vodafone Idea", "flexibility": "essential"},
    "bescom": {"category": "utilities", "display_name": "BESCOM Electricity", "flexibility": "essential"},
    "tneb": {"category": "utilities", "display_name": "TNEB Electricity", "flexibility": "essential"},
    "mseb": {"category": "utilities", "display_name": "MSEB Electricity", "flexibility": "essential"},
    "torrent power": {"category": "utilities", "display_name": "Torrent Power", "flexibility": "essential"},
    "tata power": {"category": "utilities", "display_name": "Tata Power", "flexibility": "essential"},
    "electricity": {"category": "utilities", "display_name": "Electricity Bill", "flexibility": "essential"},
    "water bill": {"category": "utilities", "display_name": "Water Bill", "flexibility": "essential"},
    "broadband": {"category": "utilities", "display_name": "Broadband Internet", "flexibility": "essential"},
    "act fibernet": {"category": "utilities", "display_name": "ACT Fibernet", "flexibility": "essential"},
    "tatasky": {"category": "utilities", "display_name": "Tata Sky / Play", "flexibility": "discretionary"},
    "tata play": {"category": "utilities", "display_name": "Tata Play", "flexibility": "discretionary"},
    "indane": {"category": "utilities", "display_name": "Indane Gas", "flexibility": "essential"},
    "hp gas": {"category": "utilities", "display_name": "HP Gas", "flexibility": "essential"},

    # ─── Healthcare & Wellness ──────────────────────────────────────────────
    "apollo": {"category": "healthcare", "display_name": "Apollo Pharmacy", "flexibility": "essential"},
    "pharmeasy": {"category": "healthcare", "display_name": "PharmEasy", "flexibility": "essential"},
    "1mg": {"category": "healthcare", "display_name": "Tata 1mg", "flexibility": "essential"},
    "practo": {"category": "healthcare", "display_name": "Practo", "flexibility": "essential"},
    "medplus": {"category": "healthcare", "display_name": "MedPlus", "flexibility": "essential"},
    "cult.fit": {"category": "healthcare", "display_name": "Cult.fit", "flexibility": "discretionary"},
    "cult fit": {"category": "healthcare", "display_name": "Cult.fit", "flexibility": "discretionary"},
    "curefit": {"category": "healthcare", "display_name": "Cure.fit", "flexibility": "discretionary"},
    "hospital": {"category": "healthcare", "display_name": "Hospital Care", "flexibility": "essential"},
    "clinic": {"category": "healthcare", "display_name": "Clinic Visit", "flexibility": "essential"},

    # ─── Rent & Housing ─────────────────────────────────────────────────────
    "rent": {"category": "rent", "display_name": "House Rent", "flexibility": "essential"},
    "nobroker": {"category": "rent", "display_name": "NoBroker Rent", "flexibility": "essential"},
    "society maintenance": {"category": "rent", "display_name": "Society Maintenance", "flexibility": "essential"},

    # ─── Investments & Savings ──────────────────────────────────────────────
    "zerodha": {"category": "investments", "display_name": "Zerodha", "flexibility": "discretionary"},
    "groww": {"category": "investments", "display_name": "Groww", "flexibility": "discretionary"},
    "upstox": {"category": "investments", "display_name": "Upstox", "flexibility": "discretionary"},
    "angel one": {"category": "investments", "display_name": "Angel One", "flexibility": "discretionary"},
    "kuvera": {"category": "investments", "display_name": "Kuvera", "flexibility": "discretionary"},
    "sip": {"category": "investments", "display_name": "Mutual Fund SIP", "flexibility": "discretionary"},

    # ─── Salary / Income ───────────────────────────────────────────────────
    "salary": {"category": "salary", "display_name": "Salary Credit", "flexibility": "fixed"},
    "payroll": {"category": "salary", "display_name": "Payroll", "flexibility": "fixed"},
    "stipend": {"category": "salary", "display_name": "Stipend", "flexibility": "fixed"},
}


def detect_merchant_info(description: str) -> Optional[Dict[str, str]]:
    """
    Scans a transaction description for known apps or merchants.
    Uses word boundary or substring matching to avoid false positives.
    """
    if not description:
        return None
    desc_clean = re.sub(r"[^a-zA-Z0-9\s&.+/]", " ", str(description).lower())

    # Sort keywords by length descending so multi-word keys match first (e.g. 'tata cliq' before 'tata')
    for kw in sorted(MERCHANT_REGISTRY.keys(), key=len, reverse=True):
        pattern = r"(?:\b|_)" + re.escape(kw) + r"(?:\b|_)"
        if re.search(pattern, desc_clean) or kw in desc_clean:
            return MERCHANT_REGISTRY[kw]

    return None


def resolve_category_from_description(description: str, fallback_category: Optional[str] = None) -> str:
    """
    Determines the definitive category for a transaction description.
    If a known app/merchant (Myntra, Blinkit, Uber, etc.) is detected, returns its canonical category.
    Otherwise falls back to the provided fallback or 'unknown'.
    """
    info = detect_merchant_info(description)
    if info:
        return info["category"]

    if fallback_category and fallback_category.strip() and fallback_category.lower() not in ["unknown", "uncategorized", "other", "debit", "expense"]:
        return fallback_category.strip().lower()

    return "unknown"


def extract_merchant_breakdown(transactions: List[Any]) -> Dict[str, Any]:
    """
    Aggregates historical transactions into structured category groups,
    identifying detected apps / merchants within each category.
    """
    category_totals: Dict[str, float] = {}
    merchants_by_cat: Dict[str, Dict[str, float]] = {}
    app_transactions: List[Dict[str, Any]] = []

    for t in transactions:
        desc = getattr(t, "description", "") or ""
        amt = abs(float(getattr(t, "amount", 0.0) or 0.0))
        ev_type = str(getattr(t, "event_type", "") or "").lower()
        dir_type = str(getattr(t, "direction", "") or "").lower()

        # Skip internal transfers
        if ev_type in ["transfer", "internal_transfer"] or dir_type in ["transfer"]:
            continue

        # Detect merchant info
        merchant_info = detect_merchant_info(desc)
        cat = merchant_info["category"] if merchant_info else getattr(t, "category", "unknown")
        if not cat or cat.lower() in ["unknown", "uncategorized", "other", ""]:
            cat = "unknown"
        cat = cat.lower()

        # Accumulate debits / expenses
        if dir_type in ["debit", "outflow"] or ev_type in ["expense", "subscription", "debt_payment"]:
            category_totals[cat] = category_totals.get(cat, 0.0) + amt

            if merchant_info:
                d_name = merchant_info["display_name"]
                if cat not in merchants_by_cat:
                    merchants_by_cat[cat] = {}
                merchants_by_cat[cat][d_name] = merchants_by_cat[cat].get(d_name, 0.0) + amt

                app_transactions.append({
                    "merchant": d_name,
                    "category": cat,
                    "amount": amt,
                    "description": desc,
                    "date": str(getattr(t, "event_date", "")),
                })

    return {
        "category_totals": category_totals,
        "merchants_by_category": merchants_by_cat,
        "detected_app_transactions": app_transactions,
    }
