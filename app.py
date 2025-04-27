from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import yfinance as yf

app = Flask(__name__)
CORS(app)

#get stock data
@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not ticker or not start_date or not end_date:
            return jsonify({'error': 'Missing required parameters'}), 400

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start >= end:
                return jsonify({'error': 'Start date must be before end date'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        stock = yf.Ticker(f"{ticker}.KA")
        hist_data = stock.history(start=start_date, end=end_date, auto_adjust=False)

        if hist_data.empty:
            return jsonify({'error': 'No data found for the given ticker and date range'}), 404

        hist_data = hist_data[['Close']].reset_index()
        hist_data["Close"] = hist_data["Close"].round(2)
        hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
        result = hist_data[['Date', 'Close']].to_dict(orient='records')
        return jsonify({"data": result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#run
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)