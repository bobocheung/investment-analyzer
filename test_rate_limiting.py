#!/usr/bin/env python3
"""
速率限制測試腳本
測試系統的速率限制和錯誤處理
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from multi_source_collector import multi_source_collector
from data_collector import DataCollector
import time

def test_rate_limiting():
    """測試速率限制功能"""
    print("🧪 測試速率限制功能...")
    print("=" * 60)
    
    # 測試多個股票，觀察速率限制
    test_symbols = ['0700.HK', '0005.HK', '0941.HK', '1398.HK', '3988.HK']
    
    print("📊 測試多個股票數據獲取...")
    print("-" * 40)
    
    start_time = time.time()
    
    for i, symbol in enumerate(test_symbols):
        print(f"\n{i+1}. 測試 {symbol}...")
        try:
            # 測試股票信息獲取
            success, data = multi_source_collector.get_stock_info_multi_source(symbol)
            
            if success:
                print(f"  ✅ 成功獲取 {symbol} 數據")
                print(f"     數據源: {data.get('data_source', 'unknown')}")
                print(f"     公司名稱: {data.get('name', 'N/A')}")
                print(f"     當前價格: {data.get('current_price', 'N/A')}")
            else:
                print(f"  ❌ 獲取 {symbol} 數據失敗")
            
            # 添加延遲避免速率限制
            if i < len(test_symbols) - 1:
                print(f"  ⏳ 等待 3 秒避免速率限制...")
                time.sleep(3)
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⏱️  總耗時: {total_time:.2f}秒")
    print(f"📊 平均每個股票: {total_time/len(test_symbols):.2f}秒")
    
    # 測試速率限制統計
    print("\n📈 速率限制統計:")
    print("-" * 40)
    
    stats = multi_source_collector.get_stats()
    print(f"總請求數: {stats['total_requests']}")
    print(f"成功請求: {stats['successful_requests']}")
    print(f"失敗請求: {stats['failed_requests']}")
    
    if stats['total_requests'] > 0:
        success_rate = (stats['successful_requests'] / stats['total_requests']) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    # 顯示各數據源使用情況
    print("\n🔍 數據源使用情況:")
    print("-" * 40)
    
    for source, count in stats['source_usage'].items():
        print(f"{source}: {count} 次請求")
    
    return stats

def test_economic_indicators_rate_limiting():
    """測試經濟指標的速率限制"""
    print("\n🧪 測試經濟指標速率限制...")
    print("=" * 60)
    
    collector = DataCollector()
    
    # 多次獲取經濟指標，觀察緩存效果
    print("📊 多次獲取經濟指標...")
    print("-" * 40)
    
    for i in range(3):
        print(f"\n{i+1}. 獲取經濟指標...")
        start_time = time.time()
        
        try:
            indicators = collector.get_economic_indicators()
            end_time = time.time()
            
            print(f"  ⏱️  耗時: {end_time - start_time:.2f}秒")
            print(f"  📊 獲取到 {len(indicators)} 個指標")
            
            for name, data in indicators.items():
                source = data.get('source', 'unknown')
                print(f"    {name}: {source}")
            
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
        
        if i < 2:
            print("  ⏳ 等待 2 秒...")
            time.sleep(2)

def test_cache_effectiveness():
    """測試緩存效果"""
    print("\n🧪 測試緩存效果...")
    print("=" * 60)
    
    collector = DataCollector()
    
    # 測試股票信息緩存
    test_symbol = '0700.HK'
    
    print(f"📊 測試 {test_symbol} 緩存效果...")
    print("-" * 40)
    
    # 第一次獲取（應該從API）
    print("1. 第一次獲取（從API）...")
    start_time = time.time()
    data1 = collector.get_stock_info_async(test_symbol)
    end_time = time.time()
    print(f"   ⏱️  耗時: {end_time - start_time:.2f}秒")
    
    # 第二次獲取（應該從緩存）
    print("2. 第二次獲取（從緩存）...")
    start_time = time.time()
    data2 = collector.get_stock_info_async(test_symbol)
    end_time = time.time()
    print(f"   ⏱️  耗時: {end_time - start_time:.2f}秒")
    
    # 比較數據
    if data1 == data2:
        print("   ✅ 緩存數據一致")
    else:
        print("   ⚠️  緩存數據不一致")

if __name__ == "__main__":
    print("🚀 速率限制測試")
    print("=" * 60)
    
    # 測試速率限制
    stats = test_rate_limiting()
    
    # 測試經濟指標速率限制
    test_economic_indicators_rate_limiting()
    
    # 測試緩存效果
    test_cache_effectiveness()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    
    print("\n💡 建議:")
    print("1. 如果遇到429錯誤，系統會自動使用緩存數據")
    print("2. 緩存時間已設置為5分鐘，減少API請求")
    print("3. 系統會自動跳過速率限制的數據源")
    print("4. 建議在非高峰時段使用系統")
    print("5. 考慮配置API密鑰以提高請求限制")
