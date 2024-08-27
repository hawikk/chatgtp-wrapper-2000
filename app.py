from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

import requests
import os

load_dotenv()

app = Flask(__name__)

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

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
            'peBasicExclExtraTTM': data['financials'].get('metric', {}).get('peBasicExclExtraTTM'),
            'pbAnnual': data['financials'].get('metric', {}).get('pbAnnual'),
            'psAnnual': data['financials'].get('metric', {}).get('psAnnual'),
            'evEbitdaAnnual': data['financials'].get('metric', {}).get('evEbitdaAnnual'),
            'roeTTM': data['financials'].get('metric', {}).get('roeTTM'),
            'roa': data['financials'].get('metric', {}).get('roa'),
            'grossMarginTTM': data['financials'].get('metric', {}).get('grossMarginTTM'),
            'netProfitMarginTTM': data['financials'].get('metric', {}).get('netProfitMarginTTM'),
            'revenueGrowthYoY': data['financials'].get('metric', {}).get('revenueGrowthYoY'),
            'epsGrowth': data['financials'].get('metric', {}).get('epsGrowth'),
            'currentRatioAnnual': data['financials'].get('metric', {}).get('currentRatioAnnual'),
            'quickRatioAnnual': data['financials'].get('metric', {}).get('quickRatioAnnual'),
            'debtEquityRatio': data['financials'].get('metric', {}).get('debtEquityRatio'),
            'interestCoverage': data['financials'].get('metric', {}).get('interestCoverage'),
            'assetTurnoverAnnual': data['financials'].get('metric', {}).get('assetTurnoverAnnual'),
            'inventoryTurnoverAnnual': data['financials'].get('metric', {}).get('inventoryTurnoverAnnual'),
            'dividendYieldIndicatedAnnual': data['financials'].get('metric', {}).get('dividendYieldIndicatedAnnual'),
            'payoutRatioAnnual': data['financials'].get('metric', {}).get('payoutRatioAnnual'),
            'marketCapitalization': data['financials'].get('metric', {}).get('marketCapitalization'),
            'beta': data['financials'].get('metric', {}).get('beta'),
            'focfCagr5Y': data['financials'].get('metric', {}).get('focfCagr5Y')
        }


def fetch_stock_data(symbol):
    # Fetch data from Finnhub API
    quote_response = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}')
    profile_response = requests.get(f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}')
    financials_response = requests.get(f'https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}')
    
    # Combine responses
    stock_data = {
        'quote': quote_response.json(),
        'profile': profile_response.json(),
        'financials': financials_response.json()
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

