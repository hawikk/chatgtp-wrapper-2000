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

    response = summarize_key_points(news_articles, ticker)
    if isinstance(response, str):
        return response

    key_points_summary = response.choices[0].message.content.strip()

    return key_points_summary


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
