from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from datetime import datetime
import json
from data_collector import DataCollector
from analyzer import InvestmentAnalyzer
from simple_report_generator import SimpleReportGenerator
from cache_manager import cache_manager

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# 初始化組件
collector = DataCollector()
analyzer = InvestmentAnalyzer()
report_generator = SimpleReportGenerator()

# 設置環境變量
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """獲取股票數據"""
    try:
        # 檢查緩存
        cached_data = cache_manager.get('analysis_result', symbol)
        if cached_data:
            print(f"📦 Using cached analysis for {symbol}")
            return jsonify(cached_data)
        
        # 收集數據（嘗試多源）
        try:
            stock_info = collector.get_stock_info_async(symbol)
            # 獲取價格數據
            price_data = collector.get_stock_prices(symbol, "5d")
            
            # 構建完整的數據結構
            data = {
                'symbol': symbol,
                'stock_info': stock_info,
                'price_data': price_data,
                'financial_data': {}
            }
        except Exception as multi_error:
            print(f"Multi-source collection failed for {symbol}: {multi_error}, falling back to sync")
            data = collector.collect_all_data(symbol)
        
        # 分析數據
        analysis_result = analyzer.analyze_stock(data)
        
        # 緩存分析結果
        cache_manager.set('analysis_result', symbol, analysis_result)
        print(f"💾 Cached analysis result for {symbol}")
        
        return jsonify(analysis_result)
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/report')
def generate_report(symbol):
    """生成股票分析報告"""
    try:
        # 檢查緩存
        cached_report = cache_manager.get('analysis_result', f"{symbol}_report")
        if cached_report:
            print(f"📦 Using cached report for {symbol}")
            return cached_report
        
        # 獲取數據
        data = collector.collect_all_data(symbol)
        
        # 生成報告
        report_html = report_generator.generate_simple_html_report(data)
        
        # 緩存報告
        cache_manager.set('analysis_result', f"{symbol}_report", report_html)
        print(f"💾 Cached report for {symbol}")
        
        return report_html
        
    except Exception as e:
        print(f"Error generating report for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/sectors')
def get_market_sectors():
    """獲取市場板塊數據"""
    try:
        # 檢查緩存
        cached_data = cache_manager.get('sector_performance', 'market_sectors')
        if cached_data:
            print("📦 Using cached market sectors data")
            return jsonify(cached_data)
        
        # 獲取數據
        sectors = collector.get_sector_performance()
        
        # 緩存數據
        cache_manager.set('sector_performance', 'market_sectors', sectors)
        print("💾 Cached market sectors data")
        
        return jsonify(sectors)
        
    except Exception as e:
        print(f"Error fetching market sectors: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market/economic')
def get_economic_indicators():
    """獲取經濟指標"""
    try:
        # 強制獲取新數據（不清除緩存，讓數據收集器處理）
        indicators = collector.get_economic_indicators()
        
        return jsonify(indicators)
        
    except Exception as e:
        print(f"Error fetching economic indicators: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/stats')
def get_cache_stats():
    """獲取緩存統計信息"""
    try:
        stats = cache_manager.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/info')
def get_cache_info():
    """獲取緩存詳細信息"""
    try:
        cache_type = request.args.get('type')
        info = cache_manager.get_cache_info(cache_type)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清空緩存"""
    try:
        cache_type = request.json.get('type')
        if cache_type:
            cache_manager.clear_type(cache_type)
            return jsonify({'message': f'Cleared {cache_type} cache'})
        else:
            cache_manager.clear_all()
            return jsonify({'message': 'All caches cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/invalidate/<symbol>', methods=['POST'])
def invalidate_stock_cache(symbol):
    """失效特定股票的緩存"""
    try:
        cache_manager.invalidate_stock_data(symbol)
        return jsonify({'message': f'Invalidated cache for {symbol}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/ttl', methods=['POST'])
def set_cache_ttl():
    """設置緩存TTL"""
    try:
        data = request.json
        cache_type = data.get('type')
        hours = data.get('hours', 1)
        
        from datetime import timedelta
        ttl = timedelta(hours=hours)
        cache_manager.set_ttl(cache_type, ttl)
        
        return jsonify({'message': f'Set TTL for {cache_type} to {hours} hours'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist')
def get_watchlist():
    """獲取監控列表"""
    try:
        watchlist_file = 'data/watchlist.json'
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 支持兩種格式：直接數組或帶symbols字段的對象
                if isinstance(data, list):
                    watchlist = data
                else:
                    watchlist = data.get('symbols', [])
            return jsonify(watchlist)
        return jsonify([])
    except Exception as e:
        print(f"Error reading watchlist: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """添加到監控列表"""
    try:
        data = request.json
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        watchlist_file = 'data/watchlist.json'
        
        # 讀取現有數據
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    watchlist = data
                else:
                    watchlist = data.get('symbols', [])
        else:
            watchlist = []
        
        if symbol not in watchlist:
            watchlist.append(symbol)
            
            # 保存為標準格式
            watchlist_data = {
                'symbols': watchlist,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(watchlist_file, 'w', encoding='utf-8') as f:
                json.dump(watchlist_data, f, ensure_ascii=False, indent=2)
            
            # 失效相關緩存
            cache_manager.invalidate_stock_data(symbol)
            
            return jsonify({'message': f'Added {symbol} to watchlist'})
        else:
            return jsonify({'message': f'{symbol} already in watchlist'})
            
    except Exception as e:
        print(f"Error adding to watchlist: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist/<symbol>', methods=['DELETE'])
def remove_from_watchlist(symbol):
    """從監控列表移除"""
    try:
        watchlist_file = 'data/watchlist.json'
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    watchlist = data
                else:
                    watchlist = data.get('symbols', [])
            
            if symbol in watchlist:
                watchlist.remove(symbol)
                
                # 保存為標準格式
                watchlist_data = {
                    'symbols': watchlist,
                    'last_updated': datetime.now().isoformat()
                }
                
                with open(watchlist_file, 'w', encoding='utf-8') as f:
                    json.dump(watchlist_data, f, ensure_ascii=False, indent=2)
                
                # 失效相關緩存
                cache_manager.invalidate_stock_data(symbol)
                
                return jsonify({'message': f'Removed {symbol} from watchlist'})
        
        return jsonify({'message': f'{symbol} not found in watchlist'})
        
    except Exception as e:
        print(f"Error removing from watchlist: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/sources')
def get_data_sources():
    """獲取數據源統計信息"""
    try:
        if hasattr(collector, 'multi_source') and collector.multi_source:
            stats = collector.multi_source.get_stats()
            return jsonify(stats)
        else:
            return jsonify({'message': 'Multi-source collector not available'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/sources/<source_name>/toggle')
def toggle_data_source(source_name):
    """啟用或禁用數據源"""
    try:
        enabled = request.args.get('enabled', 'true').lower() == 'true'
        if hasattr(collector, 'multi_source') and collector.multi_source:
            collector.multi_source.enable_source(source_name, enabled)
            return jsonify({'message': f'{source_name} {"enabled" if enabled else "disabled"}'})
        else:
            return jsonify({'error': 'Multi-source collector not available'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 靜態文件路由
@app.route('/manifest.json')
def manifest():
    """返回PWA manifest文件"""
    return send_from_directory('frontend', 'manifest.json')

@app.route('/icon.svg')
def icon():
    """返回應用圖標"""
    return send_from_directory('frontend', 'icon.svg')

@app.route('/sw.js')
def service_worker():
    """返回Service Worker文件"""
    return send_from_directory('frontend', 'sw.js')

if __name__ == '__main__':
    # 設置端口
    port = int(os.environ.get('PORT', 5000))
    
    # 根據環境設置調試模式
    debug = app.config['FLASK_ENV'] == 'development'
    
    print(f"🚀 Starting Flask app on port {port}")
    print(f"📊 Cache Manager initialized: {cache_manager.get_stats()['total_entries']} entries")
    
    app.run(host='0.0.0.0', port=port, debug=debug)