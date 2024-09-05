import datetime
import requests


def collect_news(symbol, FINNHUB_API_KEY):
    """
    Collect news for a given symbol from the last week.
    returns: list of strings with news summaries (~5K words)
    """
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)

    today_str = today.strftime('%Y-%m-%d')
    last_week_str = last_week.strftime('%Y-%m-%d')

    # Fetch news from Finnhub API
    news_response = requests.get(
        f'https://finnhub.io/api/v1/company-news?symbol={symbol}&from={last_week_str}&to={today_str}&token={FINNHUB_API_KEY}')
    news_list = news_response.json()

    # Create a new list of strings with 'datetime' and 'summary', skipping specific summaries
    news_summary_list = [
        f"{item['datetime']}: {item['summary']}"
        for item in news_list
        if item[
               'summary'] != "Looking for stock market analysis and research with proves results? Zacks.com offers in-depth financial research with over 30years of proven results."
    ]

    return news_summary_list
