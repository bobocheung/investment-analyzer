#!/usr/bin/env python3
from data_collector import DataCollector
from simple_report_generator import SimpleReportGenerator

def test_and_fix_report():
    """測試並修復報告生成問題"""
    
    # 初始化組件
    data_collector = DataCollector()
    report_generator = SimpleReportGenerator()
    
    # 測試股票信息獲取
    symbol = "0700.HK"
    print(f"Testing stock info for {symbol}...")
    
    stock_info = data_collector.get_stock_info(symbol)
    print("Stock info:", stock_info)
    
    # 創建完整的測試數據
    analysis_data = {
        'symbol': symbol,
        'stock_info': stock_info,
        'recommendation': {
            'recommendation': '買入',
            'confidence': '高',
            'risk_level': '中等',
            'current_price': stock_info.get('current_price', 590.0),
            'target_price': 650.0,
            'upside_potential': 10.2,
            'overall_score': 75.5,
            'fundamental_score': 80.0,
            'technical_score': 71.0
        }
    }
    
    print("\nGenerating report...")
    try:
        html_report = report_generator.generate_simple_html_report(analysis_data)
        
        # 保存報告到文件
        with open('test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print("✅ Report generated successfully!")
        print("📄 Report saved as 'test_report.html'")
        
        # 檢查關鍵信息是否包含在報告中
        if stock_info.get('name', 'N/A') != 'N/A':
            print(f"✅ Company name: {stock_info.get('name')}")
        else:
            print("❌ Company name missing")
            
        if stock_info.get('sector', 'N/A') != 'N/A':
            print(f"✅ Sector: {stock_info.get('sector')}")
        else:
            print("❌ Sector missing")
            
        if stock_info.get('market_cap', 0) > 0:
            market_cap = stock_info.get('market_cap')
            print(f"✅ Market cap: {market_cap:,}")
        else:
            print("❌ Market cap missing")
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_and_fix_report()