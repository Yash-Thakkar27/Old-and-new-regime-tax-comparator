RAG Tax Regime Comparator
=========================

Simple rule-based calculator to compare tax under the old and new Indian tax regimes.

Files added:
- `rag_tax_calculator.py`: core logic and rules (simplified, educational).
- `cli.py`: interactive command-line input.
- `tests/test_calculator.py`: basic pytest unit tests.

Assumptions and limitations
- The implementation uses simplified, illustrative rules and is NOT legal or tax advice.
- Capital gains and many deductions are simplified. Extend the logic for production use.


How to run
----------

Install pytest if you want to run tests:

```powershell
python -m pip install -U pytest
python -m pytest -q
```

Run the CLI:

```powershell
python cli.py
```

Features
--------
- Compares tax under old and new regimes for FY 2024-25/2025-26, including all major slabs, surcharge, and cess.
- Supports itemized deductions: 80C, 80D, home loan interest, HRA, LTA, professional tax, exempt allowances, and indexed LTCG for non-equity assets.
- CLI prompts for all relevant fields.
- **Explanation layer:** After calculation, the CLI prints a short, user-friendly explanation of which regime is better and why (based on your deductions/capital gains).
- **Legal snippet (RAG) layer:** CLI attaches relevant legal snippets (from the Income Tax Act) for each deduction/claim cited in your input, so you see the law behind each benefit.

Example CLI output
------------------

```
Comparison result:
{
	"fiscal_year": "2024-25",
	"age": 35,
	"old_regime": { ... },
	"new_regime": { ... },
	"difference_old_minus_new": 12345.67,
	"explanation": "Old regime is better because you benefit from: 80C deduction, home loan interest deduction, HRA exemption."
}

Explanation:
Old regime is better because you benefit from: 80C deduction, home loan interest deduction, HRA exemption.

Relevant legal snippets:
- 80C: Section 80C: Deduction up to Rs 1,50,000 for eligible investments (e.g., PPF, ELSS, LIC, etc.).
- home loan interest: Section 24(b): Deduction up to Rs 2,00,000 for interest on home loan (self-occupied property).
- HRA: Section 10(13A): HRA exemption is available as per least of actual HRA, rent paid minus 10% salary, or 50%/40% of salary (metro/non-metro).
- standard deduction: Section 16(ia): Standard deduction of Rs 50,000 is available from salary income.
- surcharge: Surcharge applies on total income exceeding Rs 50 lakh as per Finance Act slabs.
- cess: Health & Education Cess: 4% on income-tax plus surcharge.
- rebate: Section 87A: Rebate up to Rs 12,500 for resident individuals with total income up to Rs 5 lakh.
```

Assumptions and limitations
--------------------------
- The implementation uses simplified, illustrative rules and is NOT legal or tax advice.
- Capital gains and many deductions are simplified. Extend the logic for production use.
