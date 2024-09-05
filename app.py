from cache_setup import app, cache
from flask import render_template, request
from modules.symbol import Symbol

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
