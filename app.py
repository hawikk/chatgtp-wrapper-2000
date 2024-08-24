import logging.handlers
import os
import time
from datetime import datetime, timedelta
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_cors import CORS
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # Using in-memory cache

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FlaskApp')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Log Flask startup
logger.info("Flask application starting up...")


class FinancialData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.api_key = os.getenv('FINNHUB_API_KEY')

        # Initialize variables to store financial data
        self.company_name = None
        self.market_cap = None
        self.pe_ratio = None
        self.eps = None
        self.revenue = None
        self.revenue_growth = None
        self.net_income = None
        self.net_income_margin = None
        self.dividend_yield = None
        self.debt_to_equity_ratio = None
        self.roe = None
        self.current_ratio = None
        self.free_cash_flow = None
        self.pb_ratio = None
        self.roa = None
        self.operating_margin = None
        self.beta = None
        self.interest_coverage_ratio = None

        # Fetch data during initialization
        self.fetch_company_profile()
        self.fetch_basic_financials()
        self.fetch_financials()

    def fetch_company_profile(self):
        """Fetch company profile data that includes market cap, beta, and other data."""
        url = f'https://finnhub.io/api/v1/stock/profile2?symbol={self.ticker}&token={self.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.company_name = data.get('name')
            self.market_cap = data.get('marketCapitalization')
        else:
            print(f"Error fetching company profile for {self.ticker}: {response.status_code}")

    def fetch_basic_financials(self):
        """Fetch basic financials like P/E ratio, dividend yield, and more."""
        url = f'https://finnhub.io/api/v1/stock/metric?symbol={self.ticker}&metric=all&token={self.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('metric', {})

            # Extracting the correct metrics from the data
            self.beta = data.get('beta')
            self.pe_ratio = data.get('peTTM')  # P/E Ratio (Trailing Twelve Months)
            self.pb_ratio = data.get('pbAnnual')  # Price-to-Book Ratio (Annual)
            self.current_ratio = data.get('currentRatioAnnual')  # Current Ratio (Annual)
            self.debt_to_equity_ratio = data.get('totalDebt/totalEquityAnnual')  # Debt-to-Equity Ratio (Annual)
            self.free_cash_flow = data.get('freeCashFlowTTM')  # Free Cash Flow (TTM)
            self.interest_coverage_ratio = data.get('netInterestCoverageTTM')  # Interest Coverage Ratio (TTM)
            self.net_income = data.get('netIncomeEmployeeTTM')  # Net Income per Employee (TTM)
            self.net_income_margin = data.get('netProfitMarginTTM')  # Net Profit Margin (TTM)
            self.revenue = data.get('revenuePerShareTTM')  # Revenue Per Share (TTM)
            self.revenue_growth = data.get('revenueGrowthTTMYoy')  # Revenue Growth (TTM YoY)

        else:
            print(f"Error fetching basic financials for {self.ticker}: {response.status_code}")

    def fetch_financials(self):
        """Fetch detailed financials including revenue, net income, and growth rates."""
        url = f'https://finnhub.io/api/v1/stock/financials-reported?symbol={self.ticker}&token={self.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                latest_report = data[0].get('report', {})

                # Handling income statement
                income_statement = latest_report.get('ic', [])
                if isinstance(income_statement, list):
                    for item in income_statement:
                        if item.get('concept') == 'totalRevenue':
                            self.revenue = item.get('value')
                        if item.get('concept') == 'netIncome':
                            self.net_income = item.get('value')

                # Calculate net income margin
                if self.revenue and self.net_income:
                    self.net_income_margin = (self.net_income / self.revenue) * 100

                # Assume revenue growth is from the year-over-year percentage change
                if len(data) > 1:  # If there's at least one previous report
                    previous_income_statement = data[1].get('report', {}).get('ic', [])
                    previous_revenue = None
                    if isinstance(previous_income_statement, list):
                        for item in previous_income_statement:
                            if item.get('concept') == 'totalRevenue':
                                previous_revenue = item.get('value')
                                break

                    if previous_revenue:
                        self.revenue_growth = ((self.revenue - previous_revenue) / previous_revenue) * 100

                # Handling balance sheet
                balance_sheet = latest_report.get('bs', [])
                if isinstance(balance_sheet, list):
                    for item in balance_sheet:
                        if item.get('concept') == 'currentRatio':
                            self.current_ratio = item.get('value')
        else:
            print(f"Error fetching financials for {self.ticker}: {response.status_code}")


def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"Starting function '{func_name}' with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Finished function '{func_name}' with result: {result}")
            return result
        except Exception as e:
            logger.error(f"Exception in function '{func_name}': {e}")
            raise

    return wrapper


# Function to fetch relevant news
@log_function_call
def fetch_relevant_news(ticker):
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now() - timedelta(1)).strftime("%Y-%m-%d")}&to={time.strftime("%Y-%m-%d")}&token={FINNHUB_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data[:1]
    except requests.exceptions.RequestException as e:
        return []


# Function to summarize key points
@log_function_call
def summarize_key_points(articles, ticker):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    articles_text = ""
    for article in articles:
        articles_text += f"Headline: {article['headline']}\nSummary: {article['summary']}\n\n"

    messages = [
        {"role": "system",
         "content": "You are a senior financial advisor that summarizes weekly fundamentals analysis notes in weekly news articles for clients."},
        {"role": "user",
         "content": f"These are the latest market news about {ticker}. Carefully analyze the information and provide the 5 most important notes about the ticker:\n\n{articles_text}"}
    ]
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=750
        )
        return response
    except Exception as e:
        return str(e)


# Function to get summarized news
@log_function_call
def get_summarized_news(ticker):
    news_articles = fetch_relevant_news(ticker)
    if not news_articles:
        return "No news articles found."

    openai_response = summarize_key_points(news_articles, ticker)
    news_summary = openai_response.choices[0].message.content.strip()

    return news_summary


# Flask route with caching and logging
@app.route('/get-summary', methods=['GET'])
@cache.cached(timeout=900, query_string=True)  # Cache this route for 5 minutes
@log_function_call
def get_summary():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400

    summary = get_summarized_news(ticker)
    return jsonify({"summary": summary})


if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True)
