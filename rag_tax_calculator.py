import re

# --- RAG snippet mapping (very basic, can be extended) ---
_RAG_SNIPPETS = {
    "standard deduction": "Section 16(ia): Standard deduction of Rs 50,000 is available from salary income.",
    "80C": "Section 80C: Deduction up to Rs 1,50,000 for eligible investments (e.g., PPF, ELSS, LIC, etc.).",
    "80D": "Section 80D: Deduction for medical insurance premium (Rs 25,000, or Rs 50,000 for senior citizens).",
    "home loan interest": "Section 24(b): Deduction up to Rs 2,00,000 for interest on home loan (self-occupied property).",
    "HRA": "Section 10(13A): HRA exemption is available as per least of actual HRA, rent paid minus 10% salary, or 50%/40% of salary (metro/non-metro).",
    "LTA": "Section 10(5): LTA exemption is available for travel within India, subject to conditions.",
    "professional tax": "Section 16(iii): Professional tax paid is allowed as deduction from salary income.",
    "exempt allowances": "Section 10: Certain allowances (e.g., children education, hostel, transport) are exempt up to specified limits.",
    "equity LTCG": "Section 112A: Long-term capital gains on listed equity shares above Rs 1 lakh taxed at 10% (without indexation).",
    "equity STCG": "Section 111A: Short-term capital gains on listed equity shares taxed at 15%.",
    "other LTCG": "Section 48/112: Long-term capital gains on non-equity assets taxed at 20% with indexation.",
    "rebate": "Section 87A: Rebate up to Rs 12,500 for resident individuals with total income up to Rs 5 lakh.",
    "surcharge": "Surcharge applies on total income exceeding Rs 50 lakh as per Finance Act slabs.",
    "cess": "Health & Education Cess: 4% on income-tax plus surcharge.",
}

def _explain_regime_comparison(profile, result):
    """Generate a short explanation of why one regime is better, based on deductions/capital gains."""
    old = result["old_regime"]
    new = result["new_regime"]
    diff = result["difference_old_minus_new"]
    if abs(diff) < 1:
        return "Both regimes result in nearly the same tax. Choose based on future income/deductions."
    better = "old" if diff > 0 else "new"
    worse = "new" if diff > 0 else "old"
    reason = []
    # Check which deductions are present and allowed only in old regime
    if (profile.get("investments_80c", 0) or 0) > 0:
        reason.append("80C deduction")
    if (profile.get("insurance_80d", 0) or 0) > 0:
        reason.append("80D deduction")
    if (profile.get("home_loan_interest", 0) or 0) > 0:
        reason.append("home loan interest deduction")
    if (profile.get("hra_exempt", 0) or 0) > 0:
        reason.append("HRA exemption")
    if (profile.get("lta_exempt", 0) or 0) > 0:
        reason.append("LTA exemption")
    if (profile.get("professional_tax", 0) or 0) > 0:
        reason.append("professional tax deduction")
    if (profile.get("exempt_allowances", 0) or 0) > 0:
        reason.append("other exempt allowances")
    # Capital gains
    if (profile.get("ltcg_equity", 0) or 0) > 0:
        reason.append("equity LTCG")
    if (profile.get("stcg_equity", 0) or 0) > 0:
        reason.append("equity STCG")
    if (profile.get("other_ltcg", 0) or 0) > 0:
        reason.append("other LTCG")
    if reason:
        reason_str = ", ".join(reason)
        if better == "old":
            return f"Old regime is better because you benefit from: {reason_str}."
        else:
            return f"New regime is better because you have fewer deductions or more slab benefit."
    else:
        if better == "old":
            return "Old regime is better due to available deductions."
        else:
            return "New regime is better due to lower slab rates or less taxable income."

def _rag_snippets_for_profile(profile):
    """Return a dict of deduction/capital gain keys to legal snippets."""
    keys = []
    if (profile.get("investments_80c", 0) or 0) > 0:
        keys.append("80C")
    if (profile.get("insurance_80d", 0) or 0) > 0:
        keys.append("80D")
    if (profile.get("home_loan_interest", 0) or 0) > 0:
        keys.append("home loan interest")
    if (profile.get("hra_exempt", 0) or 0) > 0:
        keys.append("HRA")
    if (profile.get("lta_exempt", 0) or 0) > 0:
        keys.append("LTA")
    if (profile.get("professional_tax", 0) or 0) > 0:
        keys.append("professional tax")
    if (profile.get("exempt_allowances", 0) or 0) > 0:
        keys.append("exempt allowances")
    if (profile.get("ltcg_equity", 0) or 0) > 0:
        keys.append("equity LTCG")
    if (profile.get("stcg_equity", 0) or 0) > 0:
        keys.append("equity STCG")
    if (profile.get("other_ltcg", 0) or 0) > 0:
        keys.append("other LTCG")
    # Always include standard deduction, surcharge, cess, rebate
    keys.append("standard deduction")
    keys.append("surcharge")
    keys.append("cess")
    keys.append("rebate")
    # Remove duplicates
    keys = list(dict.fromkeys(keys))
    return {k: _RAG_SNIPPETS.get(k, "[No snippet found]") for k in keys}
"""
Rule-based RAG tax calculator for comparing old vs new tax regimes.

This module implements a small, configurable set of rules to compute
income tax under two regimes (old vs new) with common Indian provisions.

Assumptions (configurable in code):
- Cess: 4% on income-tax
- Rebate (section 87A): tax rebate to bring tax to zero for taxable income <= 5,00,000
- Old regime allows limited deductions: standard deduction (50,000), 80C (cap 150,000), 80D (medical/insurance cap 25,000) and home loan interest (sec 24) cap 200,000
- New regime uses alternate slab rates and disallows most deductions (user can toggle allowances in config)
- Capital gains handling (simplified):
  - Equity STCG taxed at 15%
  - Equity LTCG taxed at 10% on amount exceeding 100,000 (0% for first 100k)
  - Other STCG/LTCG fall back to slab or 20% long-term (this implementation keeps it simple and treats non-equity gains as slab for STCG and 20% for LTCG with indexation ignored)

These are simplified, educational rules to compare regimes. They are not legal advice.

Public functions:
- compare_regimes(profile) -> dict with 'old' and 'new' results
- calculate_tax_old_regime(profile)
- calculate_tax_new_regime(profile)

Profile is a dict with keys (all amounts in INR, integers or floats):
- gross_salary: salary component
- other_income: interest, rent, etc.
- investments_80c: eligible amount (will be capped to 150000)
- insurance_80d: medical insurance premium (capped in old regime)
- home_loan_interest: interest eligible under section 24 (cap applied)
- stcg_equity: short-term capital gains from equity (15% tax)
- ltcg_equity: long-term gains from equity (10% over 100k)
- other_stcg: other short term capital gains
- other_ltcg: other long term capital gains
- occupation: string (informational)

You can extend the profile fields and tax rules as needed.
"""

from typing import Dict


# Configurable policy constants
CESS_RATE = 0.04
MAX_80C = 150000
# 80D base cap; for senior citizens some years allow higher cap — handled per fiscal year rules
BASE_80D = 25000
MAX_HOME_LOAN_INTEREST = 200000
LTGC_EQUITY_EXEMPTION = 100000


def _fiscal_rules(fiscal_year: str, age: int = 0) -> dict:
    """Return year-specific slabs, surcharge, and deduction caps for supported fiscal years.
    Slabs and surcharges as per Finance Act 2024 for FY 2024-25 and assumed same for 2025-26.
    """
    rules = {}

    # --- Slabs and rules by year ---
    fy = str(fiscal_year).strip()
    # Old regime slabs (unchanged for both years)
    if age >= 80:
        rules["old_slabs"] = [
            (500000, 0.0),
            (1000000, 0.20),
            (None, 0.30),
        ]
    elif age >= 60:
        rules["old_slabs"] = [
            (300000, 0.0),
            (500000, 0.05),
            (1000000, 0.20),
            (None, 0.30),
        ]
    else:
        rules["old_slabs"] = [
            (250000, 0.0),
            (500000, 0.05),
            (1000000, 0.20),
            (None, 0.30),
        ]

    # New regime slabs and rules
    if fy == "2025-26":
        # FY 2025-26 new regime slabs (relaxed)
        rules["new_slabs"] = [
            (400000, 0.0),
            (800000, 0.05),
            (1200000, 0.10),
            (1600000, 0.15),
            (2000000, 0.20),
            (2400000, 0.25),
            (None, 0.30),
        ]
        rules["standard_deduction_new"] = 75000
        rules["rebate_new"] = (1200000, 60000)  # up to 12L, max 60k
    else:
        # FY 2024-25 new regime slabs
        rules["new_slabs"] = [
            (300000, 0.0),
            (700000, 0.05),
            (1000000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (None, 0.30),
        ]
        rules["standard_deduction_new"] = 50000
        rules["rebate_new"] = (700000, 25000)  # up to 7L, max 25k

    # Old regime rebate (both years): up to 5L, max 12,500
    rules["rebate_old"] = (500000, 12500)

    # Surcharge bands (Finance Act 2025)
    # Old regime: 50L-1Cr: 10%, 1Cr-2Cr: 15%, 2Cr-5Cr: 25%, 5Cr+: 37%
    rules["surcharge_bands_old"] = [
        (5000000, 0.0),
        (10000000, 0.10),
        (20000000, 0.15),
        (50000000, 0.25),
        (None, 0.37),
    ]
    # New regime: 50L-1Cr: 5%, 1Cr-2Cr: 15%, above 2Cr: 25%
    rules["surcharge_bands_new"] = [
        (5000000, 0.0),
        (10000000, 0.05),
        (20000000, 0.15),
        (None, 0.25),
    ]

    # 80D caps: base 25k for normal taxpayers, 50k for senior citizens for medical insurance
    rules["max_80d"] = 50000 if age >= 60 else BASE_80D
    # Standard deduction (old regime): 50,000 (both years)
    rules["standard_deduction"] = 50000
    rules["max_80c"] = MAX_80C
    rules["max_home_loan_interest"] = MAX_HOME_LOAN_INTEREST
    # HRA, LTA, professional tax, exempt allowances (user must provide eligible amounts)
    rules["hra_exempt"] = None  # calculated per user input
    rules["lta_exempt"] = None
    rules["professional_tax"] = None
    rules["exempt_allowances"] = None
    # LTCG indexation for non-equity: user must provide indexed cost, but we can show how to compute
    rules["ltcg_indexation"] = True
    return rules


def _apply_slabs(taxable: float, slabs: list) -> float:
    """Apply slab schedule. slabs: list of (limit, rate) where limit is upper bound or None for infinity.
    limits are cumulative top values.
    Example: [(250000,0),(500000,0.05),(1000000,0.2),(None,0.3)]
    """
    tax = 0.0
    lower = 0.0
    for limit, rate in slabs:
        if limit is None:
            amount = max(0.0, taxable - lower)
            tax += amount * rate
            break
        chunk = max(0.0, min(limit, taxable) - lower)
        tax += chunk * rate
        lower = limit
        if taxable <= limit:
            break
    return tax


def _add_cess(tax: float) -> float:
    return tax * (1 + CESS_RATE)



def _apply_rebate(taxable: float, tax_before_cess: float, regime: str, rules: dict) -> float:
    """Apply Section 87A-like rebate for old/new regime as per year/rules."""
    if regime == "old":
        limit, max_rebate = rules.get("rebate_old", (500000, 12500))
        if taxable <= limit:
            return max(0.0, tax_before_cess - min(tax_before_cess, max_rebate))
        return tax_before_cess
    elif regime == "new":
        limit, max_rebate = rules.get("rebate_new", (700000, 25000))
        if taxable <= limit:
            return max(0.0, tax_before_cess - min(tax_before_cess, max_rebate))
        return tax_before_cess
    else:
        return tax_before_cess


def calculate_tax_old_regime(profile: Dict, fiscal_year: str = "2024-25", age: int = 0) -> Dict:
    """Compute tax under old regime for a fiscal year. Returns dict with breakdown.

    profile: dict of amounts
    fiscal_year: '2024-25' or '2025-26' (falls back to defaults for unknown)
    age: taxpayer age to determine senior citizen caps
    """
    rules = _fiscal_rules(fiscal_year, age)

    # Aggregate income
    gross_salary = float(profile.get("gross_salary", 0.0))
    other_income = float(profile.get("other_income", 0.0))
    stcg_equity = float(profile.get("stcg_equity", 0.0))
    ltcg_equity = float(profile.get("ltcg_equity", 0.0))
    other_stcg = float(profile.get("other_stcg", 0.0))
    other_ltcg = float(profile.get("other_ltcg", 0.0))

    # Deductions
    standard = rules.get("standard_deduction", STANDARD_DEDUCTION)
    investments_80c = min(float(profile.get("investments_80c", 0.0)), rules.get("max_80c", MAX_80C))
    insurance_80d = min(float(profile.get("insurance_80d", 0.0)), rules.get("max_80d", BASE_80D))
    home_loan_interest = min(float(profile.get("home_loan_interest", 0.0)), rules.get("max_home_loan_interest", MAX_HOME_LOAN_INTEREST))
    # New deductions: HRA, LTA, professional tax, exempt allowances
    hra_exempt = float(profile.get("hra_exempt", 0.0))
    lta_exempt = float(profile.get("lta_exempt", 0.0))
    professional_tax = float(profile.get("professional_tax", 0.0))
    exempt_allowances = float(profile.get("exempt_allowances", 0.0))
    deductions = standard + investments_80c + insurance_80d + home_loan_interest + hra_exempt + lta_exempt + professional_tax + exempt_allowances

    # Capital gains treatment (simplified)
    # Equity STCG taxed separately at 15%
    tax_stcg_equity = stcg_equity * 0.15

    # Equity LTCG: first LTGC_EQUITY_EXEMPTION exempt, rest at 10%
    taxable_ltcg_eq = max(0.0, ltcg_equity - LTGC_EQUITY_EXEMPTION)
    tax_ltcg_equity = taxable_ltcg_eq * 0.10

    # Other STCG: taxed at slab rates as part of income (we'll add to ordinary income)
    # Other LTCG: taxed at 20% with indexation (user must provide indexed cost in profile)
    # If profile provides 'other_ltcg_indexed_cost', use it for indexation
    other_ltcg_indexed_cost = profile.get("other_ltcg_indexed_cost")
    if other_ltcg_indexed_cost is not None:
        # Assume other_ltcg is gross sale value, indexed_cost is cost after indexation
        taxable_other_ltcg = max(0.0, float(profile.get("other_ltcg", 0.0)) - float(other_ltcg_indexed_cost))
        tax_other_ltcg = taxable_other_ltcg * 0.20
    else:
        tax_other_ltcg = other_ltcg * 0.20

    # Ordinary income taxable base
    ordinary_income = gross_salary + other_income + other_stcg
    taxable_income = max(0.0, ordinary_income - deductions)

    # Old regime slabs from rules
    slabs_old = rules.get("old_slabs")


    tax_on_ordinary = _apply_slabs(taxable_income, slabs_old)
    # Apply rebate (old regime)
    tax_on_ordinary = _apply_rebate(taxable_income, tax_on_ordinary, "old", rules)

    # Surcharge (old regime):
    surcharge_bands = rules.get("surcharge_bands_old")
    surcharge = 0.0
    income_for_surcharge = taxable_income + stcg_equity + ltcg_equity + other_ltcg
    for limit, rate in surcharge_bands:
        if limit is None or income_for_surcharge <= limit:
            surcharge = tax_on_ordinary * rate
            break

    # Sum taxes
    tax_before_cess = tax_on_ordinary + surcharge + tax_stcg_equity + tax_ltcg_equity + tax_other_ltcg
    tax_after_cess = _add_cess(tax_before_cess)

    return {
        "taxable_income": taxable_income,
        "tax_on_ordinary": round(tax_on_ordinary, 2),
        "tax_stcg_equity": round(tax_stcg_equity, 2),
        "tax_ltcg_equity": round(tax_ltcg_equity, 2),
        "tax_other_ltcg": round(tax_other_ltcg, 2),
        "surcharge": round(surcharge, 2),
        "tax_before_cess": round(tax_before_cess, 2),
        "tax_after_cess": round(tax_after_cess, 2),
    }


def calculate_tax_new_regime(profile: Dict, fiscal_year: str = "2024-25", age: int = 0) -> Dict:
    """Compute tax under new regime for a fiscal year.

    New regime disallows many deductions. We accept fiscal_year and age for slab and cap rules.
    """
    rules = _fiscal_rules(fiscal_year, age)

    gross_salary = float(profile.get("gross_salary", 0.0))
    other_income = float(profile.get("other_income", 0.0))
    stcg_equity = float(profile.get("stcg_equity", 0.0))
    ltcg_equity = float(profile.get("ltcg_equity", 0.0))
    other_stcg = float(profile.get("other_stcg", 0.0))
    other_ltcg = float(profile.get("other_ltcg", 0.0))

    # Under new regime, standard deduction (from FY24-25) is allowed
    deductions = rules.get("standard_deduction_new", 0.0)

    # Capital gains: same simplified treatment
    tax_stcg_equity = stcg_equity * 0.15
    taxable_ltcg_eq = max(0.0, ltcg_equity - LTGC_EQUITY_EXEMPTION)
    tax_ltcg_equity = taxable_ltcg_eq * 0.10
    tax_other_ltcg = other_ltcg * 0.20

    ordinary_income = gross_salary + other_income + other_stcg
    taxable_income = max(0.0, ordinary_income - deductions)

    # New regime slabs from rules
    slabs_new = rules.get("new_slabs")


    tax_on_ordinary = _apply_slabs(taxable_income, slabs_new)
    # Apply rebate (new regime)
    tax_on_ordinary = _apply_rebate(taxable_income, tax_on_ordinary, "new", rules)

    # Surcharge (new regime):
    surcharge_bands = rules.get("surcharge_bands_new")
    surcharge = 0.0
    income_for_surcharge = taxable_income + stcg_equity + ltcg_equity + other_ltcg
    for limit, rate in surcharge_bands:
        if limit is None or income_for_surcharge <= limit:
            surcharge = tax_on_ordinary * rate
            break

    tax_before_cess = tax_on_ordinary + surcharge + tax_stcg_equity + tax_ltcg_equity + tax_other_ltcg
    tax_after_cess = _add_cess(tax_before_cess)

    return {
        "taxable_income": taxable_income,
        "tax_on_ordinary": round(tax_on_ordinary, 2),
        "tax_stcg_equity": round(tax_stcg_equity, 2),
        "tax_ltcg_equity": round(tax_ltcg_equity, 2),
        "tax_other_ltcg": round(tax_other_ltcg, 2),
        "surcharge": round(surcharge, 2),
        "tax_before_cess": round(tax_before_cess, 2),
        "tax_after_cess": round(tax_after_cess, 2),
    }


def compare_regimes(profile: Dict, fiscal_year: str = "2024-25", age: int = 0) -> Dict:
    """Return a comparison dict with both regimes, delta, explanation, and RAG legal snippets."""
    old = calculate_tax_old_regime(profile, fiscal_year=fiscal_year, age=age)
    new = calculate_tax_new_regime(profile, fiscal_year=fiscal_year, age=age)
    diff = round(old["tax_after_cess"] - new["tax_after_cess"], 2)
    result = {
        "fiscal_year": fiscal_year,
        "age": age,
        "old_regime": old,
        "new_regime": new,
        "difference_old_minus_new": diff,
    }
    result["explanation"] = _explain_regime_comparison(profile, result)
    result["legal_snippets"] = _rag_snippets_for_profile(profile)
    return result


if __name__ == "__main__":
    # Quick demo when run as script
    example = {
        "gross_salary": 1200000,
        "other_income": 20000,
        "investments_80c": 150000,
        "insurance_80d": 15000,
        "home_loan_interest": 180000,
        "stcg_equity": 0,
        "ltcg_equity": 200000,
        "other_stcg": 0,
        "other_ltcg": 0,
    }
    import json

    print(json.dumps(compare_regimes(example), indent=2))
