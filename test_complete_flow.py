#!/usr/bin/env python3
"""
測試完整的數據流程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_complete_flow():
    """測試完整的數據流程"""
    print("🧪 Testing complete data flow...")
    
    try:
        # 1. 測試智能數據獲取器
        print("\n1️⃣ Testing Smart Data Fetcher...")
        from smart_data_fetcher import smart_fetcher
        
        test_symbols = ['0700.HK', '0005.HK', '0003.HK']
        
        for symbol in test_symbols:
            print(f"\n   Testing {symbol}...")
            success, data = smart_fetcher.fetch_stock_data(symbol)
            if success:
                name = data.get('longName') or data.get('shortName') or 'Unknown'
                price = data.get('currentPrice') or data.get('regularMarketPrice') or 'No price'
                sector = data.get('sector', 'Unknown')
                print(f"   ✅ Success: {name} at ${price} ({sector})")
            else:
                print(f"   ❌ Failed to fetch data")
        
        # 2. 測試數據收集器
        print("\n2️⃣ Testing Data Collector...")
        from data_collector import DataCollector
        
        collector = DataCollector()
        
        for symbol in test_symbols:
            print(f"\n   Testing {symbol}...")
            try:
                stock_info = collector.get_stock_info_async(symbol)
                name = stock_info.get('name', 'Unknown')
                price = stock_info.get('current_price', 'No price')
                sector = stock_info.get('sector', 'Unknown')
                source = stock_info.get('data_source', 'Unknown')
                print(f"   ✅ Success: {name} at ${price} ({sector}) from {source}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # 3. 測試分析器
        print("\n3️⃣ Testing Analyzer...")
        from analyzer import InvestmentAnalyzer
        
        analyzer = InvestmentAnalyzer()
        
        for symbol in test_symbols:
            print(f"\n   Testing {symbol}...")
            try:
                # 構建測試數據
                test_data = {
                    'symbol': symbol,
                    'stock_info': collector.get_stock_info_async(symbol),
                    'price_data': [],
                    'financial_data': {}
                }
                
                analysis = analyzer.analyze_stock(test_data)
                
                if analysis and 'recommendation' in analysis:
                    rec = analysis['recommendation']
                    score = rec.get('overall_score', 0)
                    recommendation = rec.get('recommendation', 'Unknown')
                    print(f"   ✅ Analysis: Score {score:.1f}, Recommendation: {recommendation}")
                else:
                    print(f"   ❌ No analysis result")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # 4. 測試報告生成器
        print("\n4️⃣ Testing Report Generator...")
        from simple_report_generator import SimpleReportGenerator
        
        report_gen = SimpleReportGenerator()
        
        for symbol in test_symbols:
            print(f"\n   Testing {symbol}...")
            try:
                # 構建測試數據
                test_data = {
                    'symbol': symbol,
                    'stock_info': collector.get_stock_info_async(symbol),
                    'recommendation': {
                        'overall_score': 75.0,
                        'fundamental_score': 80.0,
                        'technical_score': 70.0,
                        'recommendation': '買入',
                        'current_price': 100.0,
                        'target_price': 120.0,
                        'upside_potential': 20.0,
                        'risk_level': '中等風險',
                        'confidence': '高'
                    }
                }
                
                report_html = report_gen.generate_simple_html_report(test_data)
                
                if report_html and len(report_html) > 100:
                    print(f"   ✅ Report generated: {len(report_html)} characters")
                    # 檢查是否包含中文公司名稱
                    if '騰訊' in report_html or '匯豐' in report_html or '煤氣' in report_html:
                        print(f"   ✅ Chinese company names found")
                    else:
                        print(f"   ⚠️ No Chinese company names found")
                else:
                    print(f"   ❌ Report generation failed")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎉 Complete flow test finished!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_flow()
