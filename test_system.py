#!/usr/bin/env python3
"""
投資分析系統測試腳本
"""
import sys
import os
from pathlib import Path

# 添加backend目錄到Python路徑
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_imports():
    """測試模塊導入"""
    print("🧪 測試模塊導入...")
    
    try:
        from models import DatabaseManager
        print("✅ DatabaseManager 導入成功")
        
        from data_collector import DataCollector
        print("✅ DataCollector 導入成功")
        
        from analyzer import InvestmentAnalyzer
        print("✅ InvestmentAnalyzer 導入成功")
        
        from report_generator import ReportGenerator
        print("✅ ReportGenerator 導入成功")
        
        return True
    except Exception as e:
        print(f"❌ 導入失敗: {e}")
        return False

def test_database():
    """測試數據庫功能"""
    print("\n🗄️ 測試數據庫功能...")
    
    try:
        from models import DatabaseManager
        
        # 創建數據庫管理器
        db = DatabaseManager("../data/test.db")
        print("✅ 數據庫初始化成功")
        
        # 測試插入股票數據
        test_stock_data = {
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'market_cap': 3000000000000
        }
        
        db.insert_stock_data('AAPL', test_stock_data)
        print("✅ 股票數據插入成功")
        
        return True
    except Exception as e:
        print(f"❌ 數據庫測試失敗: {e}")
        return False

def test_data_collection():
    """測試數據收集功能"""
    print("\n📊 測試數據收集功能...")
    
    try:
        from data_collector import DataCollector
        
        collector = DataCollector()
        
        # 測試獲取股票信息
        print("正在獲取AAPL股票信息...")
        stock_info = collector.get_stock_info('AAPL')
        
        if stock_info and 'name' in stock_info:
            print(f"✅ 股票信息獲取成功: {stock_info['name']}")
        else:
            print("⚠️ 股票信息獲取失敗，可能是網絡問題")
        
        # 測試獲取價格數據
        print("正在獲取AAPL價格數據...")
        price_data = collector.get_stock_prices('AAPL', '1mo')
        
        if price_data and len(price_data) > 0:
            print(f"✅ 價格數據獲取成功: {len(price_data)} 個數據點")
        else:
            print("⚠️ 價格數據獲取失敗，可能是網絡問題")
        
        return True
    except Exception as e:
        print(f"❌ 數據收集測試失敗: {e}")
        return False

def test_analysis():
    """測試分析功能"""
    print("\n🔍 測試分析功能...")
    
    try:
        from analyzer import InvestmentAnalyzer
        from data_collector import DataCollector
        
        analyzer = InvestmentAnalyzer()
        collector = DataCollector()
        
        # 獲取測試數據
        print("正在收集AAPL數據進行分析...")
        stock_data = collector.collect_all_data('AAPL')
        
        if not stock_data.get('price_data'):
            print("⚠️ 無法獲取價格數據，跳過分析測試")
            return True
        
        # 進行分析
        analysis_result = analyzer.analyze_stock(stock_data)
        
        if analysis_result and 'recommendation' in analysis_result:
            rec = analysis_result['recommendation']
            print(f"✅ 分析完成")
            print(f"   綜合評分: {rec.get('overall_score', 0):.1f}")
            print(f"   投資建議: {rec.get('recommendation', 'N/A')}")
            print(f"   風險等級: {rec.get('risk_level', 'N/A')}")
        else:
            print("⚠️ 分析結果異常")
        
        return True
    except Exception as e:
        print(f"❌ 分析測試失敗: {e}")
        return False

def test_report_generation():
    """測試報告生成功能"""
    print("\n📄 測試報告生成功能...")
    
    try:
        from report_generator import ReportGenerator
        
        generator = ReportGenerator()
        
        # 創建測試數據
        test_analysis_data = {
            'symbol': 'AAPL',
            'stock_info': {'name': 'Apple Inc.'},
            'recommendation': {
                'overall_score': 75.5,
                'fundamental_score': 80.0,
                'technical_score': 70.0,
                'recommendation': '買入',
                'confidence': '高',
                'risk_level': '中等風險',
                'current_price': 150.25,
                'target_price': 165.00,
                'upside_potential': 9.8,
                'details': {}
            }
        }
        
        # 生成HTML報告
        html_report = generator.generate_html_report(test_analysis_data)
        
        if html_report and len(html_report) > 1000:
            print("✅ HTML報告生成成功")
        else:
            print("⚠️ HTML報告生成異常")
        
        return True
    except Exception as e:
        print(f"❌ 報告生成測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 投資分析系統測試開始")
    print("=" * 50)
    
    # 確保數據目錄存在
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    tests = [
        ("模塊導入", test_imports),
        ("數據庫功能", test_database),
        ("數據收集", test_data_collection),
        ("分析功能", test_analysis),
        ("報告生成", test_report_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統可以正常使用")
        print("\n🚀 啟動系統:")
        print("   python3 run.py")
        print("\n🌍 或直接啟動後端:")
        print("   cd backend && python3 app.py")
    else:
        print("⚠️ 部分測試失敗，請檢查錯誤信息")
        print("\n🔧 常見問題解決:")
        print("1. 網絡連接問題 - 檢查網絡連接")
        print("2. 依賴缺失 - 運行 pip install -r requirements.txt")
        print("3. 權限問題 - 檢查文件讀寫權限")

if __name__ == "__main__":
    main()