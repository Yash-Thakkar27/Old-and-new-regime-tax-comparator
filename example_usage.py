# example_usage.py
"""
Example usage of RAG-enabled tax calculator.

Setup:
1. Set EMINI_API_KEY environment variable or update config.py
2. Create ./legal_docs/ folder and add .txt files with tax law content
3. Set USE_RAG = True in config.py
4. Run this script to see RAG in action
"""

import json
from rag_tax_calculator import compare_regimes

# Example profile with various deductions
example_profile = {
    "gross_salary": 1200000,
    "other_income": 20000,
    "investments_80c": 150000,
    "insurance_80d": 15000,
    "home_loan_interest": 180000,
    "education_loan_interest": 0,
    "stcg_equity": 0,
    "ltcg_equity": 200000,
    "other_stcg": 0,
    "other_ltcg": 0,
    "hra_exempt": 100000,
    "lta_exempt": 15000,
    "professional_tax": 2500,
    "exempt_allowances": 10000,
    "other_ltcg_indexed_cost": None,
}

print("="*80)
print("RAG Tax Calculator Example")
print("="*80)

# Compare regimes for FY 2024-25
result = compare_regimes(example_profile, fiscal_year="2024-25", age=35)

print(f"\nFiscal Year: {result['fiscal_year']}")
print(f"Age: {result['age']}")
print("\n" + "-"*80)
print("OLD REGIME:")
print("-"*80)
for key, value in result['old_regime'].items():
    print(f"  {key}: ₹{value:,.2f}")

print("\n" + "-"*80)
print("NEW REGIME:")
print("-"*80)
for key, value in result['new_regime'].items():
    print(f"  {key}: ₹{value:,.2f}")

print("\n" + "="*80)
print(f"TAX DIFFERENCE (Old - New): ₹{result['difference_old_minus_new']:,.2f}")
print("="*80)

print("\nEXPLANATION:")
print(result['explanation'])

print("\n" + "="*80)
print("LEGAL SNIPPETS (Retrieved via RAG):")
print("="*80)
for key, info in result['legal_snippets'].items():
    print(f"\n[{key}]")
    if isinstance(info, dict):
        print(f"  Text: {info.get('text', info)}")
        print(f"  Score: {info.get('score', 'N/A')}")
        print(f"  Source: {info.get('source', 'N/A')}")
    else:
        print(f"  {info}")

print("\n" + "="*80)