import requests

# todo: add more robust report search
def calculate_income_growth(financial_reports):
    try:
        for item in financial_reports['data'][0]['report']['ic']:
            if item['concept'] == 'us-gaap_NetIncomeLoss':
                last_quarter = item['value']
                break

        for item in financial_reports['data'][1]['report']['ic']:
            if item['concept'] == 'us-gaap_NetIncomeLoss':
                previous_quarter = item['value']
                break

        return ((last_quarter - previous_quarter) / previous_quarter) * 100
    except IndexError as e:
        return 0


def fetch_stock_data(symbol, FINNHUB_API_KEY):
    # Fetch data from Finnhub API
    quote_response = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}')
    profile_response = requests.get(f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}')
    financials_response = requests.get(
        f'https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}')
    financials_as_reported = requests.get(
        f"https://finnhub.io/api/v1/stock/financials-reported?symbol={symbol}&freq=quarterly&token={FINNHUB_API_KEY}")

    # Combine responses
    stock_data = {
        'quote': quote_response.json(),
        'profile': profile_response.json(),
        'financials': financials_response.json(),
        'financials_reports': financials_as_reported.json()
    }

    return stock_data
