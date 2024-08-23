import json
import os
import time
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins (for development purposes)


# Function to fetch relevant news
def fetch_relevant_news(ticker):
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={(datetime.now() - timedelta(1)).strftime("%Y-%m-%d")}&to={time.strftime("%Y-%m-%d")}&token={FINNHUB_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data[:1]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []


# Function to summarize key points
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
        print(f"Error summarizing key points: {e}")
        return str(e)


# Flask route
@app.route('/get-summary', methods=['GET'])
def get_summary():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "No ticker provided"}), 400
    summary = get_summarized_news(ticker)
    return jsonify({"summary": summary})


# Function to get summarized news
def get_summarized_news(ticker):
    news_articles = fetch_relevant_news(ticker)
    if not news_articles:
        return "No news articles found."
    response = summarize_key_points(news_articles, ticker)
    if isinstance(response, str):
        return response
    key_points_summary = response.choices[0].message.content.strip()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_filename = f"openai_response_{timestamp}.json"
    with open(log_filename, 'w') as log_file:
        json.dump(response.to_dict(), log_file, indent=4)
    return key_points_summary


if __name__ == '__main__':
    app.run(debug=True)
