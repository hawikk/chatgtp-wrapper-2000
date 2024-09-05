import os
import sys

from flask import Flask, render_template, request, redirect, url_for
from modules.symbol import Symbol

# Set Python path to include the current directory
sys.path.insert(0, os.path.dirname(__file__))

# Disable writing bytecode (.pyc files)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symbols = request.form['symbols'].split(',')
        stock_data = {symbol.strip(): Symbol(symbol.strip()) for symbol in symbols}
        
        gauge_charts = {symbol: stock_data[symbol].financial_metrics['TI_recommendations'] for symbol in stock_data}

        for symbol_obj in stock_data.values():
            symbol_obj.generate_stock_overview()

        return render_template('home.html', stock_data=stock_data, gauge_charts=gauge_charts)
    else:
        # For GET requests, just show an empty home page
        return render_template('home.html', stock_data={}, gauge_charts={})

if __name__ == '__main__':
    app.run(debug=True)
