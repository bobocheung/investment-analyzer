#!/usr/bin/env python3
"""
緩存系統測試腳本
測試緩存管理器的各種功能和性能
"""

import time
import requests
import json
from datetime import datetime, timedelta

# 測試配置
BASE_URL = "http://localhost:5000"
TEST_SYMBOL = "0005.HK"  # 匯豐控股

def test_cache_basic_operations():
    """測試基本緩存操作"""
    print("🧪 測試基本緩存操作...")
    
    # 1. 測試股票數據獲取（應該緩存）
    print("   📊 第一次獲取股票數據...")
    start_time = time.time()
    response1 = requests.get(f"{BASE_URL}/api/stock/{TEST_SYMBOL}")
    time1 = time.time() - start_time
    
    if response1.status_code == 200:
        print(f"   ✅ 第一次請求成功，耗時: {time1:.3f}秒")
    else:
        print(f"   ❌ 第一次請求失敗: {response1.status_code}")
        return False
    
    # 2. 測試緩存命中（應該更快）
    print("   📊 第二次獲取股票數據（應該使用緩存）...")
    start_time = time.time()
    response2 = requests.get(f"{BASE_URL}/api/stock/{TEST_SYMBOL}")
    time2 = time.time() - start_time
    
    if response2.status_code == 200:
        print(f"   ✅ 第二次請求成功，耗時: {time2:.3f}秒")
        if time2 < time1:
            print(f"   🚀 緩存加速: {((time1 - time2) / time1 * 100):.1f}%")
        else:
            print(f"   ⚠️ 緩存未生效或數據已更新")
    else:
        print(f"   ❌ 第二次請求失敗: {response2.status_code}")
        return False
    
    return True

def test_cache_statistics():
    """測試緩存統計功能"""
    print("\n🧪 測試緩存統計功能...")
    
    try:
        # 獲取緩存統計
        response = requests.get(f"{BASE_URL}/api/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print("   📊 緩存統計信息:")
            print(f"     總緩存條目: {stats.get('total_entries', 0)}")
            print(f"     緩存命中: {stats.get('hits', 0)}")
            print(f"     緩存未命中: {stats.get('misses', 0)}")
            print(f"     命中率: {stats.get('hit_rate', '0%')}")
            print(f"     緩存類型: {stats.get('cache_types', {})}")
            return True
        else:
            print(f"   ❌ 獲取緩存統計失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 測試緩存統計時出錯: {e}")
        return False

def test_cache_info():
    """測試緩存信息功能"""
    print("\n🧪 測試緩存信息功能...")
    
    try:
        # 獲取所有緩存信息
        response = requests.get(f"{BASE_URL}/api/cache/info")
        if response.status_code == 200:
            info = response.json()
            print("   📊 緩存信息:")
            print(f"     緩存類型: {info.get('types', {})}")
            print(f"     TTL設置: {info.get('ttl_settings', {})}")
            return True
        else:
            print(f"   ❌ 獲取緩存信息失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 測試緩存信息時出錯: {e}")
        return False

def test_cache_management():
    """測試緩存管理功能"""
    print("\n🧪 測試緩存管理功能...")
    
    try:
        # 1. 測試設置TTL
        print("   ⏰ 設置股票信息緩存TTL為2小時...")
        ttl_response = requests.post(f"{BASE_URL}/api/cache/ttl", 
                                   json={'type': 'stock_info', 'hours': 2})
        if ttl_response.status_code == 200:
            print("   ✅ TTL設置成功")
        else:
            print(f"   ❌ TTL設置失敗: {ttl_response.status_code}")
        
        # 2. 測試清空特定類型緩存
        print("   🗑️ 清空股票信息緩存...")
        clear_response = requests.post(f"{BASE_URL}/api/cache/clear", 
                                     json={'type': 'stock_info'})
        if clear_response.status_code == 200:
            print("   ✅ 緩存清空成功")
        else:
            print(f"   ❌ 緩存清空失敗: {clear_response.status_code}")
        
        # 3. 測試失效特定股票緩存
        print(f"   🗑️ 失效 {TEST_SYMBOL} 的緩存...")
        invalidate_response = requests.post(f"{BASE_URL}/api/cache/invalidate/{TEST_SYMBOL}")
        if invalidate_response.status_code == 200:
            print("   ✅ 緩存失效成功")
        else:
            print(f"   ❌ 緩存失效失敗: {invalidate_response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ 測試緩存管理時出錯: {e}")
        return False

def test_market_data_caching():
    """測試市場數據緩存"""
    print("\n🧪 測試市場數據緩存...")
    
    try:
        # 1. 測試市場板塊數據
        print("   📈 獲取市場板塊數據...")
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}/api/market/sectors")
        time1 = time.time() - start_time
        
        if response1.status_code == 200:
            print(f"   ✅ 第一次獲取成功，耗時: {time1:.3f}秒")
        else:
            print(f"   ❌ 第一次獲取失敗: {response1.status_code}")
            return False
        
        # 2. 測試緩存命中
        print("   📈 再次獲取市場板塊數據（應該使用緩存）...")
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/api/market/sectors")
        time2 = time.time() - start_time
        
        if response2.status_code == 200:
            print(f"   ✅ 第二次獲取成功，耗時: {time2:.3f}秒")
            if time2 < time1:
                print(f"   🚀 緩存加速: {((time1 - time2) / time1 * 100):.1f}%")
            else:
                print(f"   ⚠️ 緩存未生效")
        else:
            print(f"   ❌ 第二次獲取失敗: {response2.status_code}")
            return False
        
        # 3. 測試經濟指標緩存
        print("   💰 獲取經濟指標數據...")
        response3 = requests.get(f"{BASE_URL}/api/market/economic")
        if response3.status_code == 200:
            print("   ✅ 經濟指標獲取成功")
        else:
            print(f"   ❌ 經濟指標獲取失敗: {response3.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ 測試市場數據緩存時出錯: {e}")
        return False

def test_report_caching():
    """測試報告緩存"""
    print("\n🧪 測試報告緩存...")
    
    try:
        # 1. 生成報告
        print(f"   📄 生成 {TEST_SYMBOL} 的分析報告...")
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}/api/stock/{TEST_SYMBOL}/report")
        time1 = time.time() - start_time
        
        if response1.status_code == 200:
            print(f"   ✅ 第一次報告生成成功，耗時: {time1:.3f}秒")
        else:
            print(f"   ❌ 第一次報告生成失敗: {response1.status_code}")
            return False
        
        # 2. 測試報告緩存
        print(f"   📄 再次生成 {TEST_SYMBOL} 的分析報告（應該使用緩存）...")
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/api/stock/{TEST_SYMBOL}/report")
        time2 = time.time() - start_time
        
        if response2.status_code == 200:
            print(f"   ✅ 第二次報告生成成功，耗時: {time2:.3f}秒")
            if time2 < time1:
                print(f"   🚀 緩存加速: {((time1 - time2) / time1 * 100):.1f}%")
            else:
                print(f"   ⚠️ 緩存未生效")
        else:
            print(f"   ❌ 第二次報告生成失敗: {response2.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ 測試報告緩存時出錯: {e}")
        return False

def test_watchlist_cache_invalidation():
    """測試監控列表緩存失效"""
    print("\n🧪 測試監控列表緩存失效...")
    
    try:
        # 1. 添加到監控列表
        print(f"   📝 添加 {TEST_SYMBOL} 到監控列表...")
        add_response = requests.post(f"{BASE_URL}/api/watchlist", 
                                   json={'symbol': TEST_SYMBOL})
        if add_response.status_code == 200:
            print("   ✅ 添加到監控列表成功")
        else:
            print(f"   ❌ 添加到監控列表失敗: {add_response.status_code}")
        
        # 2. 獲取監控列表
        print("   📋 獲取監控列表...")
        watchlist_response = requests.get(f"{BASE_URL}/api/watchlist")
        if watchlist_response.status_code == 200:
            watchlist = watchlist_response.json()
            print(f"   ✅ 監控列表: {watchlist}")
        else:
            print(f"   ❌ 獲取監控列表失敗: {watchlist_response.status_code}")
        
        # 3. 從監控列表移除
        print(f"   🗑️ 從監控列表移除 {TEST_SYMBOL}...")
        remove_response = requests.delete(f"{BASE_URL}/api/watchlist/{TEST_SYMBOL}")
        if remove_response.status_code == 200:
            print("   ✅ 從監控列表移除成功")
        else:
            print(f"   ❌ 從監控列表移除失敗: {remove_response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ 測試監控列表緩存失效時出錯: {e}")
        return False

def run_performance_test():
    """運行性能測試"""
    print("\n🚀 運行性能測試...")
    
    try:
        # 測試多個股票代碼
        test_symbols = ["0005.HK", "0700.HK", "9988.HK", "1299.HK"]
        total_time_without_cache = 0
        total_time_with_cache = 0
        
        for symbol in test_symbols:
            print(f"   📊 測試 {symbol}...")
            
            # 第一次請求（無緩存）
            start_time = time.time()
            response1 = requests.get(f"{BASE_URL}/api/stock/{symbol}")
            time1 = time.time() - start_time
            total_time_without_cache += time1
            
            if response1.status_code == 200:
                print(f"     第一次請求: {time1:.3f}秒")
            else:
                print(f"     第一次請求失敗: {response1.status_code}")
                continue
            
            # 第二次請求（有緩存）
            start_time = time.time()
            response2 = requests.get(f"{BASE_URL}/api/stock/{symbol}")
            time2 = time.time() - start_time
            total_time_with_cache += time2
            
            if response2.status_code == 200:
                print(f"     第二次請求: {time2:.3f}秒")
                if time2 < time1:
                    improvement = ((time1 - time2) / time1 * 100)
                    print(f"     緩存加速: {improvement:.1f}%")
                else:
                    print("     緩存未生效")
            else:
                print(f"     第二次請求失敗: {response2.status_code}")
        
        # 計算總體性能
        if total_time_without_cache > 0 and total_time_with_cache > 0:
            overall_improvement = ((total_time_without_cache - total_time_with_cache) / total_time_without_cache * 100)
            print(f"\n   📈 總體性能提升: {overall_improvement:.1f}%")
            print(f"      無緩存總時間: {total_time_without_cache:.3f}秒")
            print(f"      有緩存總時間: {total_time_with_cache:.3f}秒")
            print(f"      節省時間: {total_time_without_cache - total_time_with_cache:.3f}秒")
        
        return True
    except Exception as e:
        print(f"   ❌ 性能測試時出錯: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 開始緩存系統測試...")
    print("=" * 50)
    
    # 檢查服務是否運行
    try:
        health_check = requests.get(f"{BASE_URL}/api/cache/stats")
        if health_check.status_code != 200:
            print("❌ 服務未運行或無法訪問")
            print("請先啟動 Flask 應用: python backend/app.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務")
        print("請先啟動 Flask 應用: python backend/app.py")
        return
    
    # 運行測試
    tests = [
        ("基本緩存操作", test_cache_basic_operations),
        ("緩存統計功能", test_cache_statistics),
        ("緩存信息功能", test_cache_info),
        ("緩存管理功能", test_cache_management),
        ("市場數據緩存", test_market_data_caching),
        ("報告緩存", test_report_caching),
        ("監控列表緩存失效", test_watchlist_cache_invalidation),
        ("性能測試", run_performance_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試出錯: {e}")
        
        print("-" * 30)
    
    # 測試結果
    print("=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！緩存系統運行正常")
    else:
        print("⚠️ 部分測試失敗，請檢查緩存系統配置")
    
    # 最終緩存統計
    try:
        final_stats = requests.get(f"{BASE_URL}/api/cache/stats")
        if final_stats.status_code == 200:
            stats = final_stats.json()
            print(f"\n📊 最終緩存統計:")
            print(f"   總緩存條目: {stats.get('total_entries', 0)}")
            print(f"   緩存命中: {stats.get('hits', 0)}")
            print(f"   緩存未命中: {stats.get('misses', 0)}")
            print(f"   命中率: {stats.get('hit_rate', '0%')}")
    except Exception as e:
        print(f"無法獲取最終緩存統計: {e}")

if __name__ == "__main__":
    main()
