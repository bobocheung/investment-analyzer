#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
from data_collector import DataCollector
from simple_report_generator import SimpleReportGenerator

app = Flask(__name__)
CORS(app)

# 初始化組件
data_collector = DataCollector()
report_generator = SimpleReportGenerator()

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/test/stock/<symbol>')
def test_stock(symbol):
    try:
        stock_info = data_collector.get_stock_info(symbol)
        return jsonify(stock_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/report/<symbol>')
def test_report(symbol):
    try:
        # 創建測試數據
        test_data = {
            'symbol': symbol,
            'stock_info': data_collector.get_stock_info(symbol),
            'recommendation': {
                'recommendation': '買入',
                'confidence': '高',
                'risk_level': '中等',
                'current_price': 590.0,
                'target_price': 650.0,
                'upside_potential': 10.2,
                'overall_score': 75.5,
                'fundamental_score': 80.0,
                'technical_score': 71.0
            }
        }
        
        html_report = report_generator.generate_simple_html_report(test_data)
        return html_report, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting test app...")
    app.run(host='0.0.0.0', port=8080, debug=True)