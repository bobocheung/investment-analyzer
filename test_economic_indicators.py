#!/usr/bin/env python3
"""
測試經濟指標的完整性和顯示
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_economic_indicators():
    """測試經濟指標"""
    print("🧪 Testing Economic Indicators...")
    
    try:
        # 1. 測試數據收集器
        print("\n1️⃣ Testing Data Collector Economic Indicators...")
        from data_collector import DataCollector
        
        collector = DataCollector()
        indicators = collector.get_economic_indicators()
        
        print(f"📊 Retrieved {len(indicators)} indicators:")
        for key, data in indicators.items():
            print(f"   {key}: {data.get('value', 'No value')} (Change: {data.get('change', 'N/A')}%)")
            print(f"      Source: {data.get('source', 'Unknown')}")
            print(f"      Date: {data.get('date', 'No date')}")
            print()
        
        # 2. 檢查數據完整性
        print("\n2️⃣ Checking Data Completeness...")
        required_fields = ['value', 'date', 'source']
        missing_data = []
        
        for key, data in indicators.items():
            for field in required_fields:
                if not data.get(field):
                    missing_data.append(f"{key}.{field}")
        
        if missing_data:
            print(f"   ⚠️ Missing data: {', '.join(missing_data)}")
        else:
            print("   ✅ All required fields present")
        
        # 3. 檢查指標數量
        print(f"\n3️⃣ Indicator Count: {len(indicators)}")
        if len(indicators) >= 8:
            print("   ✅ Sufficient indicators")
        else:
            print(f"   ⚠️ Only {len(indicators)} indicators, expected at least 8")
        
        # 4. 檢查指標類型
        print("\n4️⃣ Checking Indicator Types...")
        expected_indicators = [
            '恆生指數', '上證指數', '深證成指', '恆生科技指數', 
            '恆生國企指數', '美元兌港元', '人民幣匯率', '原油價格', 
            '黃金價格', '港股通資金'
        ]
        
        missing_indicators = []
        for indicator in expected_indicators:
            if indicator not in indicators:
                missing_indicators.append(indicator)
        
        if missing_indicators:
            print(f"   ⚠️ Missing indicators: {', '.join(missing_indicators)}")
        else:
            print("   ✅ All expected indicators present")
        
        # 5. 模擬前端顯示
        print("\n5️⃣ Simulating Frontend Display...")
        print("經濟指標面板應該顯示:")
        for key, data in indicators.items():
            value = data.get('value', 'N/A')
            change = data.get('change')
            if change is not None:
                if change > 0:
                    display_value = f"{value} (+{change}%)"
                elif change < 0:
                    display_value = f"{value} ({change}%)"
                else:
                    display_value = f"{value} (0.00%)"
            else:
                display_value = value
            
            print(f"   {key}: {display_value}")
        
        print("\n🎉 Economic indicators test finished!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_economic_indicators()
