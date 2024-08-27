from flask import Flask, render_template, request
from flask_caching import Cache
from openai import OpenAI
from dotenv import load_dotenv

import requests
import os

load_dotenv()

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

def calculate_income_growth(financial_reports):
    for item in financial_reports['data'][0]['report']['ic']:
        if item['concept'] == 'us-gaap_NetIncomeLoss':
            last_quarter = item['value']
            break
    
    for item in financial_reports['data'][1]['report']['ic']:
        if item['concept'] == 'us-gaap_NetIncomeLoss':
            previous_quarter = item['value']
            break

    return ((last_quarter - previous_quarter) / previous_quarter) * 100


class Symbol():
    def __init__(self, symbol):
        self.symbol = symbol

        data = fetch_stock_data(symbol)
        self.company_name = data['profile']['name']
        self.logo = data['profile']['logo']

        # Refactor financial metrics into a dictionary
        self.financial_metrics = {
            # Price Data
            'price_change_percentage' : data['quote']['dp'],
            'current_price' : data['quote']['c'],
            'market_cap': data['profile']['marketCapitalization'],
            'previous_close' : data['quote']['pc'],

            # Fundamentals
            'netIncomeGrowthQuarterly': calculate_income_growth(data['financials_reports']),
            'peBasicExclExtraTTM': data['financials'].get('metric', {}).get('peBasicExclExtraTTM'),
            'pbAnnual': data['financials'].get('metric', {}).get('pbAnnual'),
            'psAnnual': data['financials'].get('metric', {}).get('psAnnual'),
            'ebitdaInterimCagr5Y': data['financials'].get('metric', {}).get('ebitdaInterimCagr5Y'),
            'roeTTM': data['financials'].get('metric', {}).get('roeTTM'),
            'roa5Y': data['financials'].get('metric', {}).get('roa5Y'),
            'grossMarginTTM': data['financials'].get('metric', {}).get('grossMarginTTM'),
            'netProfitMarginTTM': data['financials'].get('metric', {}).get('netProfitMarginTTM'),
            'revenueGrowth5Y': data['financials'].get('metric', {}).get('revenueGrowth5Y'),
            'epsGrowth5Y': data['financials'].get('metric', {}).get('epsGrowth5Y'),
            'currentRatioAnnual': data['financials'].get('metric', {}).get('currentRatioAnnual'),
            'quickRatioAnnual': data['financials'].get('metric', {}).get('quickRatioAnnual'),
            'totalDebt/totalEquityAnnual': data['financials'].get('metric', {}).get('totalDebt/totalEquityAnnual'),
            'netInterestCoverageAnnual': data['financials'].get('metric', {}).get('netInterestCoverageAnnual'),
            'assetTurnoverAnnual': data['financials'].get('metric', {}).get('assetTurnoverAnnual'),
            'inventoryTurnoverAnnual': data['financials'].get('metric', {}).get('inventoryTurnoverAnnual'),
            'dividendYieldIndicatedAnnual': data['financials'].get('metric', {}).get('dividendYieldIndicatedAnnual'),
            'payoutRatioAnnual': data['financials'].get('metric', {}).get('payoutRatioAnnual'),
            'marketCapitalization': data['financials'].get('metric', {}).get('marketCapitalization'),
            'beta': data['financials'].get('metric', {}).get('beta'),
            'focfCagr5Y': data['financials'].get('metric', {}).get('focfCagr5Y')
        }


@cache.memoize(timeout=1200)   # Cache for 20 minutes
def fetch_stock_data(symbol):
    # Fetch data from Finnhub API
    quote_response = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}')
    profile_response = requests.get(f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}')
    financials_response = requests.get(f'https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}')
    financials_as_reported = requests.get(f"https://finnhub.io/api/v1/stock/financials-reported?symbol={symbol}&freq=quarterly&token={FINNHUB_API_KEY}")
    
    # Combine responses
    stock_data = {
        'quote': quote_response.json(),
        'profile': profile_response.json(),
        'financials': financials_response.json(),
        'financials_reports': financials_as_reported.json()
    }
    
    return stock_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    symbols = request.form['symbols'].split(',')
    stock_data = {symbol.strip(): Symbol(symbol.strip()) for symbol in symbols}  # Create Symbol objects
    return render_template('results.html', stock_data=stock_data)

if __name__ == '__main__':
    app.run(debug=True)

