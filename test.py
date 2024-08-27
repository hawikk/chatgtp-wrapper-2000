import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask, render_template
import plotly.graph_objects as go
import plotly.io as pio

# Flask app setup
app = Flask(__name__)

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
    
    # Summarize technical indicators for the last week
    last_week_summary = stock_data.iloc[-1][[
        'Adj Close', 'MACD_12_26_9', 'MACD_histogram_12_26_9', 'RSI_14',
        'BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'SMA_20', 'EMA_50',
        'OBV_in_million', 'STOCHk_14_3_3', 'STOCHd_14_3_3', 'ADX_14',
        'WILLR_14', 'CMF_20', 'PSARl_0.02_0.2'
    ]]

    # Only include indicators that are not NaN
    last_week_summary = last_week_summary.dropna()

    return stock_data, last_week_summary

# Function to create Plotly chart
def create_plotly_chart(stock_data, symbol):
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
    app.run(debug=True)
