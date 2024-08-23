from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import time
import requests
load_dotenv()

# todo : Construct a dictionary with the key company fundamentals (earnings, dividends, etc)
# todo : Consider expanding the time range for news analysis
# todo : Use analysis and fundamentals for a hollistic take on the ticker

# Function to fetch the most relevant news
def fetch_relevant_news(ticker):
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    # todo : Dynamic dates
    url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2024-08-22&to=2024-08-23&token={FINNHUB_API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        news_data = response.json()

        # Assuming we want the top 5 articles by relevance
        top_articles = news_data[:20]

        return top_articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []


# Function to aggregate articles and prompt OpenAI to summarize key points using ChatCompletion
def summarize_key_points(articles, ticker):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Construct the message with headlines and summaries
    articles_text = ""
    for article in articles:
        articles_text += f"Headline: {article['headline']}\nSummary: {article['summary']}\n\n"

    messages = [
        {"role": "system", "content": "You are a senior financial advisor that summarizes daily fundamentals analysis notes in daily news articles for clients."},
        {"role": "user",
         "content": f"These are the latest market news about {ticker}. Take into account the company for your analysis. Carefully analyze the information and provide the 5 most important notes about the ticker for today:\n\n{articles_text}"}
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
        return "Could not extract key points from the articles."


# Main function to get and summarize key points from news
def get_summarized_news(ticker):
    news_articles = fetch_relevant_news(ticker)

    if not news_articles:
        print('No news articles found.')
        return

    response = summarize_key_points(news_articles, ticker)
    key_points_summary = response.choices[0].message.content.strip()

    print(f"Key Points Summary:\n{key_points_summary}")

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_filename = f"openai_response_{timestamp}.json"
    with open(log_filename, 'w') as log_file:
        json.dump(response.to_dict(), log_file, indent=4)

    print(f"Full response saved to {log_filename}")


# Example usage
get_summarized_news('QCOM')
