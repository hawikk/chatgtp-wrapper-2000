from flask import Flask, render_template, request
from flask_caching import Cache

# Import Symbol class
from modules.symbol import Symbol

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    symbols = request.form['symbols'].split(',')
    stock_data = {symbol.strip(): Symbol(symbol.strip()) for symbol in symbols}  # Create Symbol objects
    
    # Generate gauge charts for each symbol
    gauge_charts = {symbol: stock_data[symbol].financial_metrics['TI_recommendations'] for symbol in stock_data}
    
    return render_template('results.html', stock_data=stock_data, gauge_charts=gauge_charts)

if __name__ == '__main__':
    app.run(debug=True)

