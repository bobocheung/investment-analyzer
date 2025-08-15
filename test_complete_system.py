#!/usr/bin/env python3
"""
完整系統測試腳本
測試所有功能是否正常工作並顯示真實數據
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from multi_source_collector import multi_source_collector
from data_collector import DataCollector
from analyzer import InvestmentAnalyzer
from simple_report_generator import SimpleReportGenerator
import time

def test_complete_system():
    """測試完整系統"""
    print("🧪 開始完整系統測試...")
    print("=" * 60)
    
    # 初始化組件
    collector = DataCollector()
    analyzer = InvestmentAnalyzer()
    report_generator = SimpleReportGenerator()
    
    # 測試股票
    test_symbol = '0700.HK'
    
    print(f"\n📊 測試股票: {test_symbol}")
    print("-" * 40)
    
    try:
        # 1. 數據收集測試
        print("1️⃣ 數據收集測試...")
        start_time = time.time()
        
        stock_info = collector.get_stock_info_async(test_symbol)
        price_data = collector.get_stock_prices(test_symbol, "5d")
        
        end_time = time.time()
        print(f"⏱️  數據收集時間: {end_time - start_time:.2f}秒")
        
        # 檢查數據質量
        print(f"📦 數據源: {stock_info.get('data_source', 'unknown')}")
        print(f"🏢 公司名稱: {stock_info.get('name', 'N/A')}")
        print(f"💰 當前價格: {stock_info.get('current_price', 'N/A')}")
        print(f"📈 市值: {stock_info.get('market_cap', 'N/A')}")
        print(f"📊 PE比率: {stock_info.get('pe_ratio', 'N/A')}")
        print(f"🏭 行業: {stock_info.get('sector', 'N/A')}")
        print(f"📉 價格數據點: {len(price_data)}")
        
        # 2. 分析測試
        print("\n2️⃣ 分析測試...")
        start_time = time.time()
        
        # 構建完整數據結構
        data = {
            'symbol': test_symbol,
            'stock_info': stock_info,
            'price_data': price_data,
            'financial_data': {}
        }
        
        analysis_result = analyzer.analyze_stock(data)
        
        end_time = time.time()
        print(f"⏱️  分析時間: {end_time - start_time:.2f}秒")
        
        # 檢查分析結果
        recommendation = analysis_result.get('recommendation', {})
        print(f"🎯 綜合評分: {recommendation.get('overall_score', 'N/A')}")
        print(f"📊 基本面評分: {recommendation.get('fundamental_score', 'N/A')}")
        print(f"📈 技術面評分: {recommendation.get('technical_score', 'N/A')}")
        print(f"💡 投資建議: {recommendation.get('recommendation', 'N/A')}")
        print(f"⚠️  風險等級: {recommendation.get('risk_level', 'N/A')}")
        print(f"🎯 目標價格: {recommendation.get('target_price', 'N/A')}")
        print(f"📈 上漲空間: {recommendation.get('upside_potential', 'N/A')}%")
        
        # 3. 報告生成測試
        print("\n3️⃣ 報告生成測試...")
        start_time = time.time()
        
        report_html = report_generator.generate_simple_html_report(analysis_result)
        
        end_time = time.time()
        print(f"⏱️  報告生成時間: {end_time - start_time:.2f}秒")
        print(f"📄 報告長度: {len(report_html)} 字符")
        
        # 4. 數據質量評估
        print("\n4️⃣ 數據質量評估...")
        
        # 檢查關鍵數據是否存在
        data_quality_score = 0
        total_checks = 0
        
        # 股票基本信息
        if stock_info.get('name') and stock_info.get('name') != test_symbol:
            data_quality_score += 1
        total_checks += 1
        
        if stock_info.get('current_price') and stock_info.get('current_price') > 0:
            data_quality_score += 1
        total_checks += 1
        
        if stock_info.get('sector') and stock_info.get('sector') != '未分類':
            data_quality_score += 1
        total_checks += 1
        
        # 分析結果
        if recommendation.get('overall_score', 0) > 0:
            data_quality_score += 1
        total_checks += 1
        
        if recommendation.get('recommendation') and recommendation.get('recommendation') != '數據不足，無法分析':
            data_quality_score += 1
        total_checks += 1
        
        if recommendation.get('target_price', 0) > 0:
            data_quality_score += 1
        total_checks += 1
        
        # 價格數據
        if len(price_data) > 0:
            data_quality_score += 1
        total_checks += 1
        
        quality_percentage = (data_quality_score / total_checks) * 100
        print(f"📊 數據質量評分: {data_quality_score}/{total_checks} ({quality_percentage:.1f}%)")
        
        # 5. 功能完整性檢查
        print("\n5️⃣ 功能完整性檢查...")
        
        functions_working = []
        functions_failed = []
        
        # 檢查數據收集
        if stock_info.get('data_source') != 'fallback':
            functions_working.append("✅ 數據收集")
        else:
            functions_failed.append("❌ 數據收集 (使用回退數據)")
        
        # 檢查分析功能
        if recommendation.get('overall_score', 0) > 0:
            functions_working.append("✅ 股票分析")
        else:
            functions_failed.append("❌ 股票分析")
        
        # 檢查報告生成
        if len(report_html) > 1000:
            functions_working.append("✅ 報告生成")
        else:
            functions_failed.append("❌ 報告生成")
        
        # 檢查價格數據
        if len(price_data) > 0:
            functions_working.append("✅ 價格數據")
        else:
            functions_failed.append("❌ 價格數據")
        
        print("正常功能:")
        for func in functions_working:
            print(f"  {func}")
        
        if functions_failed:
            print("需要改進的功能:")
            for func in functions_failed:
                print(f"  {func}")
        
        # 6. 總結
        print("\n" + "=" * 60)
        print("📋 測試總結:")
        print(f"  🎯 測試股票: {test_symbol}")
        print(f"  📊 數據質量: {quality_percentage:.1f}%")
        print(f"  ⚡ 響應時間: {end_time - start_time:.2f}秒")
        print(f"  🔧 功能正常: {len(functions_working)}/{len(functions_working) + len(functions_failed)}")
        
        if quality_percentage >= 80:
            print("  🎉 系統狀態: 優秀")
        elif quality_percentage >= 60:
            print("  ✅ 系統狀態: 良好")
        elif quality_percentage >= 40:
            print("  ⚠️  系統狀態: 需要改進")
        else:
            print("  ❌ 系統狀態: 需要修復")
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_stocks():
    """測試多個股票"""
    print("\n🧪 多股票測試...")
    print("=" * 60)
    
    test_symbols = ['0700.HK', '0005.HK', '0941.HK']
    results = {}
    
    for symbol in test_symbols:
        print(f"\n📊 測試 {symbol}...")
        try:
            # 快速測試
            collector = DataCollector()
            analyzer = InvestmentAnalyzer()
            
            stock_info = collector.get_stock_info_async(symbol)
            data = {'symbol': symbol, 'stock_info': stock_info, 'price_data': [], 'financial_data': {}}
            analysis = analyzer.analyze_stock(data)
            
            recommendation = analysis.get('recommendation', {})
            score = recommendation.get('overall_score', 0)
            rec = recommendation.get('recommendation', 'N/A')
            
            print(f"  🎯 評分: {score:.1f}")
            print(f"  💡 建議: {rec}")
            
            results[symbol] = {
                'score': score,
                'recommendation': rec,
                'data_source': stock_info.get('data_source', 'unknown')
            }
            
        except Exception as e:
            print(f"  ❌ 失敗: {e}")
            results[symbol] = {'error': str(e)}
    
    print("\n📊 多股票測試結果:")
    for symbol, result in results.items():
        if 'error' in result:
            print(f"  {symbol}: ❌ {result['error']}")
        else:
            print(f"  {symbol}: {result['score']:.1f}分 - {result['recommendation']} ({result['data_source']})")

if __name__ == "__main__":
    print("🚀 港股投資分析器 - 完整系統測試")
    print("=" * 60)
    
    # 完整系統測試
    result = test_complete_system()
    
    # 多股票測試
    test_multiple_stocks()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    print("\n💡 建議:")
    print("1. 如果數據質量低於80%，建議配置API密鑰")
    print("2. 如果功能失敗，檢查網絡連接和依賴")
    print("3. 如果響應時間過長，考慮優化緩存策略")
    print("4. 定期運行此測試以監控系統健康狀態")
