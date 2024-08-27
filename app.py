from flask import Flask, render_template, request
from flask_caching import Cache
from openai import OpenAI
from dotenv import load_dotenv

import requests
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import os
import plotly.graph_objects as go

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
        
        self.technical_indicators = get_technical_indicators(symbol)

        # Refactor financial metrics into a dictionary
        self.financial_metrics = {
            # Price Data
            'price_change_percentage' : data['quote']['dp'],
            'current_price' : data['quote']['c'],
            'market_cap': data['profile']['marketCapitalization'],
            'previous_close' : data['quote']['pc'],
            'TI_recommendations': get_recommendations(self.technical_indicators.iloc[-1]),

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

def get_recommendations(row):
    recommendations = []

    # RSI Recommendation
    rsi = row['RSI_14']
    if rsi < 20:
        recommendations.append('Strong Buy')
    elif rsi < 40:
        recommendations.append('Buy')
    elif rsi < 60:
        recommendations.append('Hold')
    elif rsi < 80:
        recommendations.append('Sell')
    else:
        recommendations.append('Strong Sell')
    
    # Moving Average (SMA and EMA) Recommendation
    price = row['Adj Close']
    sma = row['SMA_20']
    ema = row['EMA_50']
    if price > sma and sma > ema:
        recommendations.append('Strong Buy')
    elif price > sma:
        recommendations.append('Buy')
    elif price > ema:
        recommendations.append('Hold')
    elif price < sma:
        recommendations.append('Sell')
    else:
        recommendations.append('Strong Sell')
    
    # MACD Recommendation
    macd = row['MACD_12_26_9']
    signal = row['MACDs_12_26_9']
    hist = row['MACDh_12_26_9']
    if macd > signal and hist > 0:
        recommendations.append('Strong Buy' if hist > 0.5 else 'Buy')
    elif macd < signal and hist < 0:
        recommendations.append('Strong Sell' if hist < -0.5 else 'Sell')
    else:
        recommendations.append('Hold')
    
    # Stochastic Oscillator Recommendation
    stoch_k = row['STOCHk_14_3_3']
    stoch_d = row['STOCHd_14_3_3']
    if stoch_k > stoch_d and stoch_k < 20:
        recommendations.append('Strong Buy')
    elif stoch_k > stoch_d:
        recommendations.append('Buy')
    elif stoch_k < stoch_d and stoch_k > 80:
        recommendations.append('Strong Sell')
    elif stoch_k < stoch_d:
        recommendations.append('Sell')
    else:
        recommendations.append('Hold')
    
    # ADX Recommendation
    adx = row['ADX_14']
    di_plus = row['DMP_14']
    di_minus = row['DMN_14']
    if di_plus > di_minus and adx > 25:
        recommendations.append('Strong Buy')
    elif di_plus > di_minus and adx > 20:
        recommendations.append('Buy')
    elif adx < 20:
        recommendations.append('Hold')
    elif di_minus > di_plus and adx > 20:
        recommendations.append('Sell')
    else:
        recommendations.append('Strong Sell')
    
    # Aggregate recommendations into an overall score
    score = recommendations.count('Strong Buy') * 2 + recommendations.count('Buy') - recommendations.count('Sell') - recommendations.count('Strong Sell') * 2
    
    return score


# Function to fetch and process stock data
def get_technical_indicators(symbol):
    # Fetch stock data with weekly intervals
    stock_data = yf.download(symbol, period='1y', interval='1wk')
    
    # Ensure that no NaN values exist in the close price before calculations
    stock_data['Close'].fillna(method='ffill', inplace=True)
    
    # Calculate technical indicators using pandas-ta
    stock_data.ta.macd(append=True)
    stock_data.ta.rsi(append=True)
    stock_data.ta.bbands(append=True)
    stock_data.ta.obv(append=True)
    stock_data.ta.sma(length=20, append=True)
    stock_data.ta.ema(length=50, append=True)
    stock_data.ta.stoch(append=True)
    stock_data.ta.adx(append=True)
    stock_data.ta.willr(append=True)
    stock_data.ta.cmf(append=True)
    stock_data.ta.psar(append=True)
    
    # Convert OBV to millions
    stock_data['OBV_in_million'] = stock_data['OBV'] / 1e7
    stock_data['MACD_histogram_12_26_9'] = stock_data['MACDh_12_26_9']  # Rename for clarity
    
    #last_week_indicators = stock_data.iloc[-1]

    return stock_data


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
    
    # Generate gauge charts for each symbol
    gauge_charts = {symbol: create_gauge_chart(stock_data[symbol].financial_metrics['TI_recommendations']) for symbol in stock_data}
    
    return render_template('results.html', stock_data=stock_data, gauge_charts=gauge_charts)

def create_gauge_chart(score):
    # Define the gauge ranges and corresponding labels
    if score < -5:
        label = "Strong Sell"
        color = "red"
    elif score < 0:
        label = "Sell"
        color = "orange"
    elif score == 0:
        label = "Hold"
        color = "yellow"
    elif score > 0 and score <= 5:
        label = "Buy"
        color = "lightgreen"
    else:
        label = "Strong Buy"
        color = "green"

    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={'text': "Technical Indicator Recommendations"},
        gauge={
            'axis': {'range': [-10, 10]},
            'bar': {'color': color},
            'steps': [
                {'range': [-10, -5], 'color': 'darkred'},
                {'range': [-5, 0], 'color': 'orange'},
                {'range': [0, 5], 'color': 'yellow'},
                {'range': [5, 10], 'color': 'lightgreen'},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            },
        }
    ))

    # Add a needle indicator
    fig.update_traces(delta={'reference': 0}, number={'font': {'size': 20}})

    # Return the HTML representation of the figure
    return fig.to_html(full_html=False)

if __name__ == '__main__':
    app.run(debug=True)

