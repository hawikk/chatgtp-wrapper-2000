import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask, render_template
import plotly.graph_objects as go
import plotly.io as pio

# Flask app setup
app = Flask(__name__)

# Get recommendations based on technical indicators
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
    score = recommendations.count('Strong Buy') * 2 + recommendations.count('Buy') - recommendations.count('Sell') - recommendations.count('Strong Sell') * 2
    
    return score


# Function to fetch and process stock data
def fetch_and_process_data(symbol):
    # Fetch stock data with weekly intervals
    stock_data = yf.download(symbol, period='1y', interval='1wk')
    
    # Ensure that no NaN values exist in the close price before calculations
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
    
    # Iterate through each row and generate a recommendation
    stock_data['Recommendation'] = stock_data.apply(get_recommendations, axis=1)
    
    # Drop any rows that contain NaN values in the relevant columns
    stock_data.dropna(subset=[
        'Adj Close', 'MACD_12_26_9', 'MACD_histogram_12_26_9', 'RSI_14',
        'SMA_20', 'EMA_50', 'STOCHk_14_3_3', 'STOCHd_14_3_3', 'ADX_14',
        'DMP_14', 'DMN_14'
    ], inplace=True)
    
    # Summarize the last week's recommendation
    last_week_indicators = stock_data.iloc[-1]

    return last_week_indicators

# Function to create Plotly chart
""" def create_plotly_chart(stock_data, symbol):
    fig = go.Figure()

    # Add adjusted close price line
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Adj Close'], mode='lines', name='Adj Close'))

    # Add SMA and EMA lines
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA_20'], mode='lines', name='SMA 20'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['EMA_50'], mode='lines', name='EMA 50'))

    # Add RSI as a subplot
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI_14'], mode='lines', name='RSI 14', yaxis="y2"))

    # Set up layout with secondary y-axis for RSI
    fig.update_layout(
        title=f"Technical Indicators for {symbol} (Weekly Data)",
        xaxis_title="Date",
        yaxis_title="Price",
        yaxis2=dict(title="RSI", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99)
    )

    return fig 

# Flask route to display the chart
@app.route('/')
def index():
    symbol = 'DIS'
    stock_data, last_week_summary = fetch_and_process_data(symbol)
    fig = create_plotly_chart(stock_data, symbol)

    # Render the plot as an HTML div
    chart_div = pio.to_html(fig, full_html=False)

    return render_template('test.html', chart_div=chart_div, last_week_summary=last_week_summary)

if __name__ == '__main__':
    app.run(debug=True) """
