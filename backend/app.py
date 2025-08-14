from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import schedule
import time

from models import DatabaseManager
from data_collector import DataCollector
from analyzer import InvestmentAnalyzer
from simple_report_generator import SimpleReportGenerator

app = Flask(__name__, template_folder='../templates', static_folder='../frontend', static_url_path='')
CORS(app)

# 初始化組件
db_manager = DatabaseManager()
data_collector = DataCollector()
analyzer = InvestmentAnalyzer()
report_generator = SimpleReportGenerator()

# 全局變量存儲分析結果
analysis_cache = {}

@app.route('/')
def index():
    """主頁"""
    return app.send_static_file('index.html')

@app.route('/api/analyze/<symbol>')
def analyze_stock(symbol):
    """分析指定股票"""
    try:
        symbol = symbol.upper()
        
        # 檢查緩存
        if symbol in analysis_cache:
            cache_time = analysis_cache[symbol].get('timestamp', '')
            if cache_time:
                cache_datetime = datetime.fromisoformat(cache_time.replace('Z', '+00:00'))
                if (datetime.now() - cache_datetime).seconds < 3600:  # 1小時緩存
                    return jsonify(analysis_cache[symbol])
        
        # 收集數據
        stock_data = data_collector.collect_all_data(symbol)
        if not stock_data.get('stock_info'):
            return jsonify({'error': f'無法獲取 {symbol} 的數據'}), 404
        
        # 存儲數據到數據庫
        db_manager.insert_stock_data(symbol, stock_data['stock_info'])
        if stock_data.get('price_data'):
            db_manager.insert_price_data(symbol, stock_data['price_data'])
        
        # 進行分析
        analysis_result = analyzer.analyze_stock(stock_data)
        
        # 存儲分析結果
        if 'recommendation' in analysis_result:
            db_manager.insert_analysis_result(symbol, analysis_result['recommendation'])
        
        # 緩存結果
        analysis_result['timestamp'] = datetime.now().isoformat()
        analysis_cache[symbol] = analysis_result
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/info')
def get_stock_info(symbol):
    """獲取股票基本信息"""
    try:
        symbol = symbol.upper()
        stock_info = data_collector.get_stock_info(symbol)
        
        if not stock_info:
            return jsonify({'error': f'無法獲取 {symbol} 的信息'}), 404
        
        return jsonify(stock_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/prices')
def get_stock_prices(symbol):
    """獲取股票價格數據"""
    try:
        symbol = symbol.upper()
        period = request.args.get('period', '1y')
        
        # 先嘗試從數據庫獲取
        db_prices = db_manager.get_stock_prices(symbol, limit=252)
        
        if not db_prices:
            # 從API獲取
            price_data = data_collector.get_stock_prices(symbol, period)
            if price_data:
                db_manager.insert_price_data(symbol, price_data)
                return jsonify(price_data)
            else:
                return jsonify({'error': f'無法獲取 {symbol} 的價格數據'}), 404
        
        return jsonify(db_prices)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/sectors')
def get_sector_performance():
    """獲取行業表現"""
    try:
        sector_data = data_collector.get_sector_performance()
        return jsonify(sector_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/economic')
def get_economic_indicators():
    """獲取經濟指標"""
    try:
        economic_data = data_collector.get_economic_indicators()
        return jsonify(economic_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<symbol>/news')
def get_stock_news(symbol):
    """獲取股票新聞"""
    try:
        symbol = symbol.upper()
        limit = int(request.args.get('limit', 10))
        
        news_data = data_collector.get_market_news(symbol, limit)
        return jsonify(news_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<symbol>')
def generate_report(symbol):
    """生成投資報告"""
    try:
        symbol = symbol.upper()
        
        # 獲取最新分析結果
        if symbol not in analysis_cache:
            # 如果沒有緩存，先進行分析
            analyze_result = analyze_stock(symbol)
            if hasattr(analyze_result, 'status_code') and analyze_result.status_code != 200:
                return analyze_result
        
        analysis_data = analysis_cache.get(symbol, {})
        
        # 生成報告
        report_html = report_generator.generate_simple_html_report(analysis_data)
        
        return report_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<symbol>/pdf')
def generate_pdf_report(symbol):
    """生成PDF報告"""
    try:
        symbol = symbol.upper()
        
        # 獲取分析數據
        if symbol not in analysis_cache:
            analyze_result = analyze_stock(symbol)
            if hasattr(analyze_result, 'status_code') and analyze_result.status_code != 200:
                return analyze_result
        
        analysis_data = analysis_cache.get(symbol, {})
        
        # 生成報告文件
        report_path = report_generator.generate_pdf_report(analysis_data)
        
        if report_path and os.path.exists(report_path):
            # 檢查文件類型
            if report_path.endswith('.pdf'):
                return send_file(report_path, as_attachment=True, 
                               download_name=f'{symbol}_investment_report.pdf',
                               mimetype='application/pdf')
            elif report_path.endswith('.html'):
                # 如果是HTML文件，直接返回HTML內容
                with open(report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
            else:
                return send_file(report_path, as_attachment=True, 
                               download_name=f'{symbol}_investment_report.html')
        else:
            # 如果文件生成失敗，直接返回HTML報告
            html_report = report_generator.generate_simple_html_report(analysis_data)
            return html_report, 200, {'Content-Type': 'text/html; charset=utf-8'}
            
    except Exception as e:
        return jsonify({'error': f'報告生成失敗: {str(e)}'}), 500

@app.route('/api/watchlist', methods=['GET', 'POST'])
def manage_watchlist():
    """管理觀察清單"""
    if request.method == 'GET':
        # 返回觀察清單
        watchlist_file = 'data/watchlist.json'
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r') as f:
                watchlist = json.load(f)
        else:
            watchlist = []
        
        return jsonify(watchlist)
    
    elif request.method == 'POST':
        # 添加到觀察清單
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'error': '股票代碼不能為空'}), 400
        
        watchlist_file = 'data/watchlist.json'
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r') as f:
                watchlist = json.load(f)
        else:
            watchlist = []
        
        if symbol not in watchlist:
            watchlist.append(symbol)
            
            # 確保目錄存在
            os.makedirs('data', exist_ok=True)
            
            with open(watchlist_file, 'w') as f:
                json.dump(watchlist, f)
        
        return jsonify({'message': f'{symbol} 已添加到觀察清單'})

@app.route('/api/watchlist/<symbol>', methods=['DELETE'])
def remove_from_watchlist(symbol):
    """從觀察清單移除"""
    try:
        symbol = symbol.upper()
        watchlist_file = 'data/watchlist.json'
        
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r') as f:
                watchlist = json.load(f)
            
            if symbol in watchlist:
                watchlist.remove(symbol)
                
                with open(watchlist_file, 'w') as f:
                    json.dump(watchlist, f)
                
                return jsonify({'message': f'{symbol} 已從觀察清單移除'})
            else:
                return jsonify({'error': f'{symbol} 不在觀察清單中'}), 404
        else:
            return jsonify({'error': '觀察清單不存在'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """批量分析股票"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': '股票代碼列表不能為空'}), 400
        
        results = {}
        for symbol in symbols:
            try:
                symbol = symbol.upper()
                stock_data = data_collector.collect_all_data(symbol)
                if stock_data.get('stock_info'):
                    analysis_result = analyzer.analyze_stock(stock_data)
                    results[symbol] = analysis_result
                    
                    # 緩存結果
                    analysis_result['timestamp'] = datetime.now().isoformat()
                    analysis_cache[symbol] = analysis_result
                    
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def scheduled_data_update():
    """定時數據更新任務"""
    print("Running scheduled data update...")
    
    # 獲取觀察清單
    watchlist_file = 'data/watchlist.json'
    if os.path.exists(watchlist_file):
        with open(watchlist_file, 'r') as f:
            watchlist = json.load(f)
        
        # 更新觀察清單中的股票數據
        for symbol in watchlist:
            try:
                stock_data = data_collector.collect_all_data(symbol)
                if stock_data.get('stock_info'):
                    # 更新數據庫
                    db_manager.insert_stock_data(symbol, stock_data['stock_info'])
                    if stock_data.get('price_data'):
                        db_manager.insert_price_data(symbol, stock_data['price_data'])
                    
                    # 更新分析結果
                    analysis_result = analyzer.analyze_stock(stock_data)
                    if 'recommendation' in analysis_result:
                        db_manager.insert_analysis_result(symbol, analysis_result['recommendation'])
                    
                    # 更新緩存
                    analysis_result['timestamp'] = datetime.now().isoformat()
                    analysis_cache[symbol] = analysis_result
                    
                    print(f"Updated data for {symbol}")
                    
            except Exception as e:
                print(f"Error updating {symbol}: {e}")

def run_scheduler():
    """運行定時任務"""
    schedule.every().day.at("09:00").do(scheduled_data_update)  # 每天9點更新
    schedule.every().day.at("15:30").do(scheduled_data_update)  # 每天15:30更新
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分鐘檢查一次

@app.route('/api/health')
def health_check():
    """健康檢查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(analysis_cache)
    })

if __name__ == '__main__':
    print("🚀 Starting Investment Analyzer...")
    
    # 確保數據目錄存在
    os.makedirs('data', exist_ok=True)
    print("📁 Data directory created")
    
    # 啟動定時任務線程
    try:
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("⏰ Scheduler thread started")
    except Exception as e:
        print(f"⚠️ Warning: Scheduler failed to start: {e}")
    
    # 啟動Flask應用
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Starting Flask app on http://0.0.0.0:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    if __name__ == '__main__':
        app.run(debug=debug_mode, host='0.0.0.0', port=port, threaded=True)