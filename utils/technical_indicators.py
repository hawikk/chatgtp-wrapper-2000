import yfinance as yf
import pandas as pd
import pandas_ta as ta


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
    score = recommendations.count('Strong Buy') * 2 + recommendations.count('Buy') - recommendations.count(
        'Sell') - recommendations.count('Strong Sell') * 2

    return score


def get_technical_indicators(symbol):
    stock_data = yf.download(symbol, period='1y', interval='1wk')

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

    # last_week_indicators = stock_data.iloc[-1]

    return stock_data
