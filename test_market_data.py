#!/usr/bin/env python3
"""
市場數據測試腳本
測試經濟指標是否獲取真實數據
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from data_collector import DataCollector
import time

def test_market_data():
    """測試市場數據獲取"""
    print("🧪 測試市場數據獲取...")
    print("=" * 60)
    
    collector = DataCollector()
    
    try:
        print("🌐 獲取經濟指標...")
        start_time = time.time()
        
        indicators = collector.get_economic_indicators()
        
        end_time = time.time()
        print(f"⏱️  獲取時間: {end_time - start_time:.2f}秒")
        
        print("\n📊 經濟指標結果:")
        print("-" * 40)
        
        for name, data in indicators.items():
            value = data.get('value', 'N/A')
            source = data.get('source', 'unknown')
            date = data.get('date', 'N/A')
            
            print(f"📈 {name}:")
            print(f"   數值: {value}")
            print(f"   來源: {source}")
            print(f"   時間: {date}")
            print()
        
        # 驗證數據真實性
        print("🔍 數據真實性驗證:")
        print("-" * 40)
        
        hsi_data = indicators.get('恆生指數', {})
        if hsi_data:
            hsi_value = hsi_data.get('raw_value', 0)
            if 20000 <= hsi_value <= 30000:
                print("✅ 恆生指數數值合理 (20,000-30,000)")
            else:
                print(f"⚠️  恆生指數數值異常: {hsi_value}")
        
        shanghai_data = indicators.get('上證指數', {})
        if shanghai_data:
            shanghai_value = shanghai_data.get('raw_value', 0)
            if 3000 <= shanghai_value <= 4000:
                print("✅ 上證指數數值合理 (3,000-4,000)")
            else:
                print(f"⚠️  上證指數數值異常: {shanghai_value}")
        
        usd_hkd_data = indicators.get('美元兌港元', {})
        if usd_hkd_data:
            usd_hkd_value = usd_hkd_data.get('raw_value', 0)
            if 7.5 <= usd_hkd_value <= 8.0:
                print("✅ 美元兌港元數值合理 (7.5-8.0)")
            else:
                print(f"⚠️  美元兌港元數值異常: {usd_hkd_value}")
        
        # 檢查數據源
        print("\n📡 數據源檢查:")
        print("-" * 40)
        
        real_sources = 0
        total_indicators = len(indicators)
        
        for name, data in indicators.items():
            source = data.get('source', 'unknown')
            if source not in ['fallback', 'latest_known', 'estimated']:
                print(f"✅ {name}: 真實數據源 ({source})")
                real_sources += 1
            else:
                print(f"⚠️  {name}: 回退數據源 ({source})")
        
        real_data_percentage = (real_sources / total_indicators) * 100
        print(f"\n📊 真實數據比例: {real_sources}/{total_indicators} ({real_data_percentage:.1f}%)")
        
        if real_data_percentage >= 75:
            print("🎉 數據質量: 優秀")
        elif real_data_percentage >= 50:
            print("✅ 數據質量: 良好")
        elif real_data_percentage >= 25:
            print("⚠️  數據質量: 需要改進")
        else:
            print("❌ 數據質量: 需要修復")
        
        return indicators
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_yahoo_finance_direct():
    """直接測試Yahoo Finance數據獲取"""
    print("\n🧪 直接測試Yahoo Finance...")
    print("=" * 60)
    
    import yfinance as yf
    
    test_symbols = {
        '恆生指數': ['^HSI', 'HSI=F', 'HSI.HK'],
        '上證指數': ['000001.SS', '^SSEC', 'SSEC'],
        '美元兌港元': ['USDHKD=X', 'USDHKD', 'HKD=X']
    }
    
    for name, symbols in test_symbols.items():
        print(f"\n📊 測試 {name}:")
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty and len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    print(f"  ✅ {symbol}: {current:,.2f} ({change:+.2f}%)")
                else:
                    print(f"  ❌ {symbol}: 無數據")
            except Exception as e:
                print(f"  ❌ {symbol}: {e}")

if __name__ == "__main__":
    print("🚀 市場數據測試")
    print("=" * 60)
    
    # 測試市場數據
    result = test_market_data()
    
    # 直接測試Yahoo Finance
    test_yahoo_finance_direct()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    
    if result:
        print("\n💡 建議:")
        print("1. 如果真實數據比例低於75%，檢查網絡連接")
        print("2. 如果Yahoo Finance失敗，可能需要配置代理")
        print("3. 定期運行此測試以監控數據質量")
        print("4. 考慮配置專業數據源API以提高數據準確性")
