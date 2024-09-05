from cache_setup import app, cache
from flask import render_template, request, jsonify
from modules.symbol import Symbol
import re

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symbols = request.form['symbols'].split(',')
        stock_data = {symbol.strip(): Symbol(symbol.strip()) for symbol in symbols}
        
        gauge_charts = {symbol: stock_data[symbol].financial_metrics['TI_recommendations'] for symbol in stock_data}

        return render_template('home.html', stock_data=stock_data, gauge_charts=gauge_charts)
    else:
        return render_template('home.html', stock_data={}, gauge_charts={})

@app.route('/generate_overview', methods=['POST'])
def generate_overview():
    symbol = request.json.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400

    stock_symbol = Symbol(symbol)
    stock_symbol.generate_stock_overview()
    news_summary_list = stock_symbol.news_summary.split('\n')

    # Remove the prefix of a number followed by a dot and a space
    news_summary_list = [re.sub(r'^\d+\.\s', '', news_item) for news_item in news_summary_list]
    
    return jsonify({'news_summary': news_summary_list})

if __name__ == '__main__':
    app.run(debug=True)
