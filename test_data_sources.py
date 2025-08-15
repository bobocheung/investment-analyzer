#!/usr/bin/env python3
"""
數據源測試腳本
用於驗證各個數據源是否能獲取真實的股票數據
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from multi_source_collector import multi_source_collector
from data_collector import DataCollector
import time

def test_data_sources():
    """測試所有數據源"""
    print("🧪 開始測試數據源...")
    print("=" * 50)
    
    # 測試股票列表
    test_symbols = ['0700.HK', '0005.HK', '0941.HK', '1398.HK', '3988.HK']
    
    for symbol in test_symbols:
        print(f"\n📊 測試股票: {symbol}")
        print("-" * 30)
        
        try:
            # 使用多源收集器
            start_time = time.time()
            data = multi_source_collector.get_stock_info_multi_source(symbol)
            end_time = time.time()
            
            print(f"⏱️  響應時間: {end_time - start_time:.2f}秒")
            print(f"📦 數據源: {data.get('data_source', 'unknown')}")
            print(f"🏢 公司名稱: {data.get('name', 'N/A')}")
            print(f"💰 當前價格: {data.get('current_price', 'N/A')}")
            print(f"📈 市值: {data.get('market_cap', 'N/A')}")
            print(f"📊 PE比率: {data.get('pe_ratio', 'N/A')}")
            print(f"🏭 行業: {data.get('sector', 'N/A')}")
            
            # 檢查數據質量
            if data.get('data_source') == 'fallback':
                print("⚠️  使用回退數據")
            elif data.get('current_price') and data.get('current_price') > 0:
                print("✅ 獲取到真實數據")
            else:
                print("❌ 數據不完整")
                
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
    
    # 顯示統計信息
    print("\n" + "=" * 50)
    print("📈 數據源統計信息:")
    stats = multi_source_collector.get_stats()
    print(f"總請求數: {stats['total_requests']}")
    print(f"成功請求: {stats['successful_requests']}")
    print(f"失敗請求: {stats['failed_requests']}")
    print(f"成功率: {stats['success_rate']:.2%}")
    
    print("\n各數據源使用情況:")
    for source, count in stats['source_usage'].items():
        print(f"  {source}: {count}次")
    
    print("\n數據源狀態:")
    for source in stats['sources']:
        status = "✅ 啟用" if source['enabled'] else "❌ 禁用"
        print(f"  {source['name']}: {status} (優先級: {source['priority']}, 成功率: {source['success_rate']:.2%})")

def test_individual_sources():
    """測試個別數據源"""
    print("\n🔍 測試個別數據源...")
    print("=" * 50)
    
    symbol = '0700.HK'
    
    # 測試Yahoo Finance
    print(f"\n📊 測試Yahoo Finance: {symbol}")
    try:
        success, data = multi_source_collector._fetch_from_yahoo_finance(symbol)
        if success:
            print(f"✅ Yahoo Finance成功: {data.get('name', 'N/A')} - ${data.get('currentPrice', 'N/A')}")
        else:
            print("❌ Yahoo Finance失敗")
    except Exception as e:
        print(f"❌ Yahoo Finance錯誤: {e}")
    
    # 測試Alpha Vantage
    print(f"\n📊 測試Alpha Vantage: {symbol}")
    try:
        success, data = multi_source_collector._fetch_from_alpha_vantage(symbol)
        if success:
            print(f"✅ Alpha Vantage成功: {data.get('name', 'N/A')} - ${data.get('current_price', 'N/A')}")
        else:
            print("❌ Alpha Vantage失敗")
    except Exception as e:
        print(f"❌ Alpha Vantage錯誤: {e}")
    
    # 測試Finnhub
    print(f"\n📊 測試Finnhub: {symbol}")
    try:
        success, data = multi_source_collector._fetch_from_finnhub(symbol)
        if success:
            print(f"✅ Finnhub成功: {data.get('name', 'N/A')} - ${data.get('current_price', 'N/A')}")
        else:
            print("❌ Finnhub失敗")
    except Exception as e:
        print(f"❌ Finnhub錯誤: {e}")
    
    # 測試Twelve Data
    print(f"\n📊 測試Twelve Data: {symbol}")
    try:
        success, data = multi_source_collector._fetch_from_twelve_data(symbol)
        if success:
            print(f"✅ Twelve Data成功: {data.get('name', 'N/A')} - ${data.get('current_price', 'N/A')}")
        else:
            print("❌ Twelve Data失敗")
    except Exception as e:
        print(f"❌ Twelve Data錯誤: {e}")

if __name__ == "__main__":
    print("🚀 港股投資分析器 - 數據源測試")
    print("=" * 50)
    
    # 測試多源收集
    test_data_sources()
    
    # 測試個別數據源
    test_individual_sources()
    
    print("\n" + "=" * 50)
    print("✅ 測試完成！")
    print("\n💡 提示:")
    print("1. 如果看到 '使用回退數據'，說明所有API源都失敗了")
    print("2. 如果看到 '獲取到真實數據'，說明成功從API獲取了數據")
    print("3. 可以配置API密鑰來提高成功率")
    print("4. 檢查網絡連接和API密鑰是否正確")
