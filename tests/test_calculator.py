import pytest
from rag_tax_calculator import calculate_tax_old_regime, calculate_tax_new_regime, compare_regimes

def test_education_loan_interest_80e():
    # Education loan interest should be fully deductible in old regime
    profile = {
        "gross_salary": 800000,
        "education_loan_interest": 100000,
        "investments_80c": 0,
        "insurance_80d": 0,
        "home_loan_interest": 0,
    }
    res = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=30)
    # Taxable income should be reduced by 1 lakh
    assert abs(res["taxable_income"] - 700000) < 1
    # New regime should ignore this deduction
    res_new = calculate_tax_new_regime(profile, fiscal_year="2024-25", age=30)
    assert abs(res_new["taxable_income"] - 800000) < 1


def test_basic_comparison():
    profile = {
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
    res = compare_regimes(profile, fiscal_year="2024-25", age=35)
    assert "old_regime" in res and "new_regime" in res
    # Ensure numeric values
    assert res["old_regime"]["tax_after_cess"] >= 0
    assert res["new_regime"]["tax_after_cess"] >= 0


def test_low_income_rebate():
    profile = {"gross_salary": 300000, "other_income": 0}
    old = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=30)
    new = calculate_tax_new_regime(profile, fiscal_year="2024-25", age=30)
    # Rebate should reduce tax to zero (our simplified rebate)
    assert old["tax_on_ordinary"] == 0
    assert new["tax_on_ordinary"] == 0


def test_senior_80d_cap():
    # Senior citizen should get higher 80D cap (50k) in our rules
    profile = {"gross_salary": 800000, "other_income": 0, "insurance_80d": 50000, "investments_80c": 0}
    old_non_senior = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=40)
    old_senior = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=65)
    # Senior should have larger deduction and thus lower taxable income
    assert old_senior["taxable_income"] < old_non_senior["taxable_income"]


def test_hra_lta_prof_tax_exempt_allowances():
    # All deductions should reduce taxable income
    profile = {
        "gross_salary": 1000000,
        "hra_exempt": 100000,
        "lta_exempt": 20000,
        "professional_tax": 2500,
        "exempt_allowances": 15000,
    }
    res = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=35)
    # Taxable income should be less than gross salary
    assert res["taxable_income"] < 1000000


def test_ltcg_indexation():
    # Indexed cost should reduce taxable LTCG
    profile = {
        "gross_salary": 0,
        "other_ltcg": 500000,
        "other_ltcg_indexed_cost": 300000,
    }
    res = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=35)
    # Tax should be on 200,000 only
    assert abs(res["tax_other_ltcg"] - 40000) < 1


def test_high_income_surcharge():
    # Surcharge should apply for very high income
    profile = {
        "gross_salary": 60000000,  # 6 crore
    }
    res = calculate_tax_old_regime(profile, fiscal_year="2024-25", age=35)
    # Surcharge should be nonzero
    assert res["surcharge"] > 0
    # Cess should be included in final tax
    assert res["tax_after_cess"] > res["tax_before_cess"]
