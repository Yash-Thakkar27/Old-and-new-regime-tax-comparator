from flask import Flask, render_template, request, jsonify
from rag_tax_calculator import compare_regimes

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/compare', methods=['POST'])
def api_compare():
    data = request.json
    fiscal_year = data.get('fiscal_year', '2024-25')
    age = int(data.get('age', 0))
    profile = {k: float(data.get(k, 0)) for k in [
        'gross_salary', 'other_income', 'investments_80c', 'insurance_80d', 'home_loan_interest',
        'education_loan_interest', 'stcg_equity', 'ltcg_equity', 'other_stcg', 'other_ltcg',
        'hra_exempt', 'lta_exempt', 'professional_tax', 'exempt_allowances', 'other_ltcg_indexed_cost'
    ]}
    result = compare_regimes(profile, fiscal_year=fiscal_year, age=age)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
