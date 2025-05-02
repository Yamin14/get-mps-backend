from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import yfinance as yf
import logging
import pandas as pd

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#home
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the Stock Data API'}), 200

#get stock data
@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        logger.info(f"Received request for ticker: {ticker}, start_date: {start_date}, end_date: {end_date}")

        if not ticker or not start_date or not end_date:
            return jsonify({'error': 'Missing required parameters'}), 400

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start >= end:
                return jsonify({'error': 'Start date must be before end date'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        ticker_with_suffix = f"{ticker}.KA"
        logger.info(f"Fetching data for ticker: {ticker_with_suffix} from {start_date} to {end_date}")
        stock = yf.Ticker(ticker_with_suffix)

        try:
            hist_data = stock.history(start=start_date, end=end_date, auto_adjust=False)
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance: {e}")
            hist_data = pd.DataFrame()

        if hist_data.empty:
            logger.info(f"No data found for ticker: {ticker_with_suffix}, trying ticker {ticker}")
            stock = yf.Ticker(ticker)
            try:
                hist_data = stock.history(start=start_date, end=end_date, auto_adjust=False)
            except Exception as e:
                logger.error(f"Error fetching data from Yahoo Finance: {e}")
                hist_data = pd.DataFrame()

        if hist_data.empty:
            logger.error(f"No data found for ticker: {ticker} or {ticker_with_suffix}")
            return jsonify({'error': 'No data found for the given ticker and date range'}), 404

        hist_data = hist_data[['Close']].reset_index()
        hist_data["Close"] = hist_data["Close"].round(2)
        hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
        result = hist_data[['Date', 'Close']].to_dict(orient='records')
        return jsonify({"data": result}), 200

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

#run
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)