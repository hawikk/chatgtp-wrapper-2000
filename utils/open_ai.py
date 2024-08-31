from openai import OpenAI

def generate_ai_summary(news_data):
    client = OpenAI()

    # Combine all news articles into a single string
    combined_news = " ".join([article['title'] + " " + article['description'] for article in news_data])

    # Generate AI summary
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI summarizing news articles about companies for mid to long-term investment analysis. Focus on company overview, recent news, financial health, competitive landscape, industry trends, risks, market sentiment, and long-term growth drivers. You will receive a list of recent news articles and will carefully analyze them to extract the five most important points of the whole news cycle."},
            {"role": "user", "content": combined_news}
        ],
        max_tokens=100
    )

    return response.choices[0].message.content

def generate_ai_recommendation(stock_data):
    client = OpenAI()

    # Combine all stock data into a single string
    combined_data = " ".join([f"{key}: {value}" for key, value in stock_data.items()])

    # Generate AI recommendation
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates investment recommendations based on stock data."},
            {"role": "user", "content": combined_data}
        ],
        max_tokens=100
    )

    return response.choices[0].message.content
