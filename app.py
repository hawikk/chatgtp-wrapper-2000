from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

import requests
import os

load_dotenv()

app = Flask(__name__)

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

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
    stock_data = {symbol: fetch_stock_data(symbol.strip()) for symbol in symbols}
    return render_template('results.html', stock_data=stock_data)

if __name__ == '__main__':
    app.run(debug=True)

