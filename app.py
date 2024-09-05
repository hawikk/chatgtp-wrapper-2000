import os
import sys

from flask import Flask, render_template, request
from modules.symbol import Symbol

# Set Python path to include the current directory
sys.path.insert(0, os.path.dirname(__file__))

# Disable writing bytecode (.pyc files)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    symbols = request.form['symbols'].split(',')
    stock_data = {symbol.strip(): Symbol(symbol.strip()) for symbol in symbols}  # Create Symbol objects

    # Generate gauge charts for each symbol
    gauge_charts = {symbol: stock_data[symbol].financial_metrics['TI_recommendations'] for symbol in stock_data}

    for symbol_obj in stock_data.values():
        symbol_obj.generate_stock_overview()

    return render_template('results.html', stock_data=stock_data, gauge_charts=gauge_charts)


if __name__ == '__main__':
    app.run(debug=True)
