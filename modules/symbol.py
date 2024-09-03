import os

from dotenv import load_dotenv

from utils.core_financials import fetch_stock_data, calculate_income_growth
from utils.technical_indicators import get_technical_indicators, get_recommendations
from utils.open_ai import generate_ai_news_summary

load_dotenv()

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class Symbol():
    def __init__(self, symbol):
        self.symbol = symbol

        data = fetch_stock_data(symbol, FINNHUB_API_KEY)  # Pass the API key
        self.company_name = data['profile']['name']
        self.logo = data['profile']['logo']

        self.technical_indicators = get_technical_indicators(symbol)
        self.financial_metrics = self.construct_financial_metrics(data)
        self.news_summary = ""

    def construct_financial_metrics(self, data):
        return {
            # Price Data
            'price_change_percentage': data['quote']['dp'],
            'current_price': data['quote']['c'],
            'market_cap': data['profile']['marketCapitalization'],
            'previous_close': data['quote']['pc'],
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
