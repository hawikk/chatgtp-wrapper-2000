from openai import OpenAI
from cache_config import cache
from utils.news_collector import collect_news

def generate_ai_news_summary(symbol, OPENAI_API_KEY, FINNHUB_API_KEY):
    news_data = collect_news(symbol, FINNHUB_API_KEY)
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI summarizing news articles about companies for mid to long-term investment analysis. Focus on company overview, recent news, financial health, competitive landscape, industry trends, risks, market sentiment, and long-term growth drivers. You will receive a list of recent news articles and will carefully analyze them to extract the five most important points of the whole news cycle. You want to be concise and professional, giving a very information dense list without text before of after."},
            {"role": "user", "content": f"Here is the news data: {news_data}"}
        ],
        max_tokens=10000
    )

    news_summary = response.choices[0].message.content
    ai_analysis = "AI Analysis: " + response.choices[0].message.content

    return {
        'news': news_summary,
        'analysis': ai_analysis
    }

def generate_ai_recommendation(stock_data, OPENAI_API_KEY):
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Combine all stock data into a single string
    combined_data = " ".join([f"{key}: {value}" for key, value in stock_data.items()])

    # Generate AI recommendation
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates investment recommendations based on stock data."},
            {"role": "user", "content": combined_data}
        ],
        max_tokens=250
    )

    return response.choices[0].message.content
