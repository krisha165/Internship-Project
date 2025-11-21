from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import calendar
from typing import Dict, Any

app = Flask(__name__)

class ExpiryCalculator:
    def __init__(self):
        self.market_holidays = {
            '2024-01-26': 'Republic Day',
            '2024-03-25': 'Holi',
            '2024-03-29': 'Good Friday',
            '2024-04-11': 'Eid-ul-Fitr',
            '2024-05-01': 'Maharashtra Day',
            '2024-06-17': 'Bakri Eid',
            '2024-07-17': 'Muharram',
            '2024-08-15': 'Independence Day',
            '2024-10-02': 'Mahatma Gandhi Jayanti',
            '2024-11-01': 'Diwali',
            '2024-11-15': 'Gurunanak Jayanti',
            '2024-12-25': 'Christmas'
        }
    
    def is_holiday(self, date_str: str) -> bool:
        return date_str in self.market_holidays
    
    def get_last_thursday(self, year: int, month: int) -> datetime:
        last_day = calendar.monthrange(year, month)[1]
        last_date = datetime(year, month, last_day)
        
        while last_date.weekday() != 3:
            last_date -= timedelta(days=1)
        
        return last_date
    
    def adjust_for_holiday(self, date_obj: datetime) -> datetime:
        current_date = date_obj
        while self.is_holiday(current_date.strftime('%Y-%m-%d')):
            current_date -= timedelta(days=1)
        return current_date
    
    def get_monthly_expiry(self, for_date: str) -> Dict[str, Any]:
        try:
            input_date = datetime.strptime(for_date, '%Y-%m-%d')
            year = input_date.year
            month = input_date.month
            
            expiry_date = self.get_last_thursday(year, month)
            adjusted_expiry = self.adjust_for_holiday(expiry_date)
            
            if adjusted_expiry.month != month:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                expiry_date = self.get_last_thursday(year, month)
                adjusted_expiry = self.adjust_for_holiday(expiry_date)
            
            days_to_expiry = (adjusted_expiry - input_date).days
            
            return {
                'expiry_date': adjusted_expiry.strftime('%Y-%m-%d'),
                'days_to_expiry': max(0, days_to_expiry),
                'is_weekly': False,
                'expiry_type': 'monthly'
            }
            
        except ValueError as e:
            raise ValueError(f"Invalid date format: {for_date}. Use YYYY-MM-DD format.")
    
    def get_weekly_expiry(self, for_date: str) -> Dict[str, Any]:
        try:
            input_date = datetime.strptime(for_date, '%Y-%m-%d')
            
            days_ahead = 3 - input_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            expiry_date = input_date + timedelta(days=days_ahead)
            adjusted_expiry = self.adjust_for_holiday(expiry_date)
            
            days_to_expiry = (adjusted_expiry - input_date).days
            
            return {
                'expiry_date': adjusted_expiry.strftime('%Y-%m-%d'),
                'days_to_expiry': max(0, days_to_expiry),
                'is_weekly': True,
                'expiry_type': 'weekly'
            }
            
        except ValueError as e:
            raise ValueError(f"Invalid date format: {for_date}. Use YYYY-MM-DD format.")

expiry_calc = ExpiryCalculator()

@app.route('/api/expiry', methods=['GET', 'POST'])
def get_expiry():
    try:
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                index = data.get('index', 'NIFTY').upper()
                date_str = data.get('date')
                expiry_type = data.get('expiry_type', 'both')
            else:
                index = request.form.get('index', 'NIFTY').upper()
                date_str = request.form.get('date')
                expiry_type = request.form.get('expiry_type', 'both')
        else:
            index = request.args.get('index', 'NIFTY').upper()
            date_str = request.args.get('date')
            expiry_type = request.args.get('expiry_type', 'both')
        
        if not date_str:
            return jsonify({
                'error': 'Date parameter is required',
                'example_get': '/api/expiry?index=NIFTY&date=2024-01-15',
                'example_post': 'Send JSON: {"index": "NIFTY", "date": "2024-01-15"}'
            }), 400
        
        datetime.strptime(date_str, '%Y-%m-%d')
        
        result = {
            'index': index,
            'for_date': date_str,
            'timestamp': datetime.now().isoformat(),
            'request_method': request.method
        }
        
        if expiry_type in ['monthly', 'both']:
            monthly_expiry = expiry_calc.get_monthly_expiry(date_str)
            result['monthly_expiry'] = monthly_expiry
        
        if expiry_type in ['weekly', 'both']:
            weekly_expiry = expiry_calc.get_weekly_expiry(date_str)
            result['weekly_expiry'] = weekly_expiry
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/expiry/monthly', methods=['GET'])
def get_monthly_expiry():
    index = request.args.get('index', 'NIFTY').upper()
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    try:
        monthly_expiry = expiry_calc.get_monthly_expiry(date_str)
        return jsonify({
            'index': index,
            'for_date': date_str,
            'monthly_expiry': monthly_expiry
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/expiry/weekly', methods=['GET'])
def get_weekly_expiry():
    index = request.args.get('index', 'NIFTY').upper()
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    try:
        weekly_expiry = expiry_calc.get_weekly_expiry(date_str)
        return jsonify({
            'index': index,
            'for_date': date_str,
            'weekly_expiry': weekly_expiry
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/holidays', methods=['GET'])
def get_holidays():
    return jsonify(expiry_calc.market_holidays)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Expiry Date API'
    })

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Expiry Date API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                code { background: #eee; padding: 2px 5px; }
            </style>
        </head>
        <body>
            <h1>Expiry Date API</h1>
            <p>Welcome to the Expiry Date Calculation API</p>
            
            <div class="endpoint">
                <h3>API Endpoints:</h3>
                <ul>
                    <li><code>GET /api/health</code> - Health check</li>
                    <li><code>GET /api/expiry?index=NIFTY&date=2024-01-15</code> - Get expiry dates</li>
                    <li><code>GET /api/expiry/monthly?index=NIFTY&date=2024-01-15</code> - Monthly expiry only</li>
                    <li><code>GET /api/expiry/weekly?index=NIFTY&date=2024-01-15</code> - Weekly expiry only</li>
                    <li><code>GET /api/holidays</code> - Market holidays</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <h3>Quick Test Links:</h3>
                <ul>
                    <li><a href="/api/health" target="_blank">Health Check</a></li>
                    <li><a href="/api/expiry?index=NIFTY&date=2024-01-15" target="_blank">Test Expiry</a></li>
                    <li><a href="/api/holidays" target="_blank">View Holidays</a></li>
                </ul>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting Expiry Date API Server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)


