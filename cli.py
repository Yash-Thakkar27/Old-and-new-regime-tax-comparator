"""Simple CLI for the RAG tax comparison tool."""
import json
from rag_tax_calculator import compare_regimes


def _ask_float(prompt: str, default: float = 0.0) -> float:
    try:
        raw = input(f"{prompt} [{default}]: ")
        if raw.strip() == "":
            return float(default)
        return float(raw)
    except Exception:
        print("Invalid number, using 0")
        return 0.0



def main():
    print("Welcome to the RAG Tax Regime Comparator!")
    print("I will help you compare your tax under the old and new regimes, and explain the result with legal citations.")
    fiscal_year = input("Fiscal year (e.g. 2024-25) [2024-25]: ") or "2024-25"
    try:
        age = int(input("Taxpayer age in years [0]: ") or "0")
    except Exception:
        age = 0
    profile = {}
    # Conversational Q&A
    print("Let's start with your income details.")
    profile["gross_salary"] = _ask_float("Gross salary", 0.0)
    profile["other_income"] = _ask_float("Other income (interest/rent)", 0.0)

    # Follow-up: If gross_salary is high but deductions are zero, prompt for common deductions
    if profile["gross_salary"] > 500000:
        print("You may be eligible for deductions. Let's check some common ones.")
    profile["investments_80c"] = _ask_float("Investments under 80C (e.g., PPF, ELSS)", 0.0)
    profile["insurance_80d"] = _ask_float("Medical insurance premium (80D)", 0.0)
    profile["home_loan_interest"] = _ask_float("Home loan interest (section 24)", 0.0)
    profile["education_loan_interest"] = _ask_float("Interest paid on education loan (80E, if any)", 0.0)

    print("Now, let's check for capital gains.")
    profile["stcg_equity"] = _ask_float("Short-term capital gains (equity)", 0.0)
    profile["ltcg_equity"] = _ask_float("Long-term capital gains (equity)", 0.0)
    profile["other_stcg"] = _ask_float("Other short-term capital gains (non-equity)", 0.0)
    profile["other_ltcg"] = _ask_float("Other long-term capital gains (non-equity, sale value)", 0.0)
    indexed_cost = input("Indexed cost for other LTCG (non-equity, optional, press Enter to skip): ")
    if indexed_cost.strip():
        try:
            profile["other_ltcg_indexed_cost"] = float(indexed_cost)
        except Exception:
            print("Invalid indexed cost, skipping.")

    print("Finally, let's check for salary-related exemptions.")
    profile["hra_exempt"] = _ask_float("HRA exempt amount (if any)", 0.0)
    profile["lta_exempt"] = _ask_float("LTA exempt amount (if any)", 0.0)
    profile["professional_tax"] = _ask_float("Professional tax paid (if any)", 0.0)
    profile["exempt_allowances"] = _ask_float("Other exempt allowances (if any)", 0.0)

    # Follow-up: If most fields are zero, offer to explain what each deduction is
    if sum([profile.get(k, 0) for k in ["investments_80c", "insurance_80d", "home_loan_interest", "education_loan_interest", "hra_exempt", "lta_exempt", "professional_tax", "exempt_allowances"]]) == 0:
        print("Tip: Deductions like 80C, 80D, home loan interest, HRA, LTA, and education loan interest can reduce your tax in the old regime.")
        print("Ask your employer or tax advisor if you are eligible for any of these.")

    print("\nCalculating your tax comparison...\n")
    result = compare_regimes(profile, fiscal_year=fiscal_year, age=age)

    # Conversational explanation
    print("--- Tax Comparison Summary ---")
    print(f"For fiscal year {fiscal_year}, age {age}:")
    print(f"Tax under old regime: ₹{result['old_regime']['tax_after_cess']:.2f}")
    print(f"Tax under new regime: ₹{result['new_regime']['tax_after_cess']:.2f}")
    diff = result['difference_old_minus_new']
    if abs(diff) < 1:
        print("Both regimes result in nearly the same tax. Choose based on future income/deductions.")
    elif diff > 0:
        print(f"You save ₹{abs(diff):.2f} by choosing the new regime.")
    else:
        print(f"You save ₹{abs(diff):.2f} by choosing the old regime.")

    print("\nExplanation:")
    print(result.get("explanation", ""))

    print("\nLegal citations for your deductions/claims:")
    for k, v in result.get("legal_snippets", {}).items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    main()
