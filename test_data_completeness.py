#!/usr/bin/env python3
"""
測試數據完整性 - 確保沒有"數據不可用"的問題
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_data_completeness():
    """測試數據完整性"""
    print("🧪 Testing data completeness...")
    
    try:
        # 1. 測試智能數據獲取器
        print("\n1️⃣ Testing Smart Data Fetcher...")
        from smart_data_fetcher import smart_fetcher
        
        test_symbols = ['0700.HK', '0005.HK', '0003.HK', '0100.HK']
        
        for symbol in test_symbols:
            print(f"\n   Testing {symbol}...")
            success, data = smart_fetcher.fetch_stock_data(symbol)
            if success:
                name = data.get('longName') or data.get('shortName') or 'Unknown'
                price = data.get('currentPrice') or data.get('regularMarketPrice') or 'No price'
                sector = data.get('sector', 'Unknown')
                market_cap = data.get('marketCap', 'No market cap')
                pe_ratio = data.get('trailingPE', 'No PE ratio')
                
                print(f"   ✅ Success: {name}")
                print(f"      Price: ${price}")
                print(f"      Sector: {sector}")
                print(f"      Market Cap: {market_cap}")
                print(f"      PE Ratio: {pe_ratio}")
                
                # 檢查是否有缺失數據
                missing_data = []
                if not data.get('currentPrice') and not data.get('regularMarketPrice'):
                    missing_data.append('current_price')
                if not data.get('sector'):
                    missing_data.append('sector')
                if not data.get('marketCap'):
                    missing_data.append('market_cap')
                if not data.get('trailingPE'):
                    missing_data.append('pe_ratio')
                
                if missing_data:
                    print(f"      ⚠️ Missing: {', '.join(missing_data)}")
                else:
                    print(f"      ✅ All data present")
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
                market_cap = stock_info.get('market_cap', 'No market cap')
                pe_ratio = stock_info.get('pe_ratio', 'No PE ratio')
                
                print(f"   ✅ Success: {name}")
                print(f"      Price: ${price}")
                print(f"      Sector: {sector}")
                print(f"      Market Cap: {market_cap}")
                print(f"      PE Ratio: {pe_ratio}")
                
                # 檢查是否有缺失數據
                missing_data = []
                if not stock_info.get('current_price'):
                    missing_data.append('current_price')
                if not stock_info.get('sector'):
                    missing_data.append('sector')
                if not stock_info.get('market_cap'):
                    missing_data.append('market_cap')
                if not stock_info.get('pe_ratio'):
                    missing_data.append('pe_ratio')
                
                if missing_data:
                    print(f"      ⚠️ Missing: {', '.join(missing_data)}")
                else:
                    print(f"      ✅ All data present")
                    
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
                    current_price = rec.get('current_price', 0)
                    target_price = rec.get('target_price', 0)
                    upside_potential = rec.get('upside_potential', 0)
                    
                    print(f"   ✅ Analysis: Score {score:.1f}, Recommendation: {recommendation}")
                    print(f"      Current Price: ${current_price}")
                    print(f"      Target Price: ${target_price}")
                    print(f"      Upside Potential: {upside_potential:.1f}%")
                    
                    # 檢查是否有缺失數據
                    missing_data = []
                    if not rec.get('current_price'):
                        missing_data.append('current_price')
                    if not rec.get('target_price'):
                        missing_data.append('target_price')
                    if not rec.get('upside_potential'):
                        missing_data.append('upside_potential')
                    
                    if missing_data:
                        print(f"      ⚠️ Missing: {', '.join(missing_data)}")
                    else:
                        print(f"      ✅ All data present")
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
                    
                    # 檢查是否包含"數據不可用"
                    if '數據不可用' in report_html:
                        print(f"   ❌ Report contains '數據不可用'")
                    else:
                        print(f"   ✅ Report has no '數據不可用' text")
                    
                    # 檢查是否包含中文公司名稱
                    if '騰訊' in report_html or '匯豐' in report_html or '煤氣' in report_html or '白馬' in report_html:
                        print(f"   ✅ Chinese company names found")
                    else:
                        print(f"   ⚠️ No Chinese company names found")
                else:
                    print(f"   ❌ Report generation failed")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎉 Data completeness test finished!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_completeness()
