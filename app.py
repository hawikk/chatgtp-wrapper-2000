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
        self.financial_metrics = {            # Price Data
            'price_change_percentage' : data['quote']['dp'],
            'current_price' : data['quote']['c'],
            'market_cap': data['profile']['marketCapitalization'],
            'previous_close' : data['quote']['pc'],
        }
        # Fundamentals
        fundamentals_keys = [
            'peBasicExclExtraTTM', 'pbAnnual', 'psAnnual', 'ebitdaInterimCagr5Y',
            'roeTTM', 'roa5Y', 'grossMarginTTM', 'netProfitMarginTTM',
            'revenueGrowth5Y', 'epsGrowth5Y', 'currentRatioAnnual',
            'quickRatioAnnual', 'totalDebt/totalEquityAnnual',
            'netInterestCoverageAnnual', 'assetTurnoverAnnual',
            'inventoryTurnoverAnnual', 'dividendYieldIndicatedAnnual',
            'payoutRatioAnnual', 'marketCapitalization', 'beta', 'focfCagr5Y'
        ]

        for key in fundamentals_keys:
            self.financial_metrics[key] = data['financials'].get('metric', {}).get(key)


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

