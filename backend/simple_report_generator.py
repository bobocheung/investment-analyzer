import os
from datetime import datetime
from typing import Dict

class SimpleReportGenerator:
    def __init__(self):
        pass
    
    def generate_simple_html_report(self, analysis_data: Dict) -> str:
        """生成簡化的HTML報告"""
        try:
            # 提取數據
            symbol = analysis_data.get('symbol', '未知股票')
            stock_info = analysis_data.get('stock_info', {})
            recommendation = analysis_data.get('recommendation', {})
            
            # 如果recommendation是空的，嘗試從analysis_data中獲取
            if not recommendation:
                recommendation = analysis_data.get('recommendation', {})
            
            print(f"Generating report for {symbol}")
            print(f"Stock info keys: {list(stock_info.keys())}")
            print(f"Recommendation keys: {list(recommendation.keys())}")
            
            # 安全地獲取數值
            def safe_format(value, format_str="%.2f", default="數據不可用"):
                try:
                    if value is not None:
                        return format_str % value
                    return default
                except:
                    return default
            
            # 格式化市值
            def format_market_cap(value):
                try:
                    if value and value > 0:
                        if value >= 1e12:
                            return f"{value/1e12:.2f}兆"
                        elif value >= 1e9:
                            return f"{value/1e9:.2f}十億"
                        elif value >= 1e8:
                            return f"{value/1e8:.2f}億"
                        elif value >= 1e6:
                            return f"{value/1e6:.2f}百萬"
                        else:
                            return f"{value:,.0f}"
                    return "數據不可用"
                except:
                    return "數據不可用"
            
            current_price = safe_format(recommendation.get('current_price'))
            target_price = safe_format(recommendation.get('target_price'))
            overall_score = safe_format(recommendation.get('overall_score', 0), "%.1f")
            fundamental_score = safe_format(recommendation.get('fundamental_score', 0), "%.1f")
            technical_score = safe_format(recommendation.get('technical_score', 0), "%.1f")
            upside_potential = safe_format(recommendation.get('upside_potential', 0), "%.1f")
            
            # 生成HTML
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 港股投資分析報告</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 50%, #ffd3a5 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 8px 8px 0px rgba(78, 205, 196, 0.2);
            border: 3px solid #4ecdc4;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #ff6b6b;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
            transform: rotate(-0.5deg);
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
            margin-top: 10px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #fff;
            border: 3px solid #4ecdc4;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            transform: rotate(-0.5deg);
            box-shadow: 5px 5px 0px rgba(78, 205, 196, 0.2);
        }}
        .card:nth-child(even) {{
            transform: rotate(0.5deg);
            border-color: #ff6b6b;
            box-shadow: 5px 5px 0px rgba(255, 107, 107, 0.2);
        }}
        .card:nth-child(3n) {{
            border-color: #feca57;
            box-shadow: 5px 5px 0px rgba(254, 202, 87, 0.2);
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
            color: #2c3e50;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .metric-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-label {{
            font-weight: 500;
            color: #34495e;
        }}
        .metric-value {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .disclaimer {{
            background: #fff3cd;
            border: 2px solid #ffeaa7;
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
            transform: rotate(-0.2deg);
        }}
        .disclaimer h3 {{
            color: #856404;
            margin: 0 0 10px 0;
        }}
        .disclaimer p {{
            color: #856404;
            margin: 0;
        }}
        @media (max-width: 768px) {{
            .summary-cards {{
                grid-template-columns: 1fr;
            }}
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏮 {symbol} 港股投資分析報告</h1>
            <div class="subtitle">{stock_info.get('name', symbol)} | 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <div class="summary-cards">
            <div class="card">
                <h3>💡 投資建議</h3>
                <div class="value">{recommendation.get('recommendation', '分析中')}</div>
                <div>信心度: {recommendation.get('confidence', '評估中')}</div>
            </div>
            <div class="card">
                <h3>📊 綜合評分</h3>
                <div class="value">{overall_score}</div>
                <div>滿分 100</div>
            </div>
            <div class="card">
                <h3>⚠️ 風險等級</h3>
                <div class="value">{recommendation.get('risk_level', '評估中')}</div>
                <div>投資風險評估</div>
            </div>
        </div>

        <div class="section">
            <h2>📈 核心指標</h2>
            <div class="metric-grid">
                <div class="metric-item">
                    <h4>💰 價格信息</h4>
                    <div class="metric">
                        <span class="metric-label">當前價格</span>
                        <span class="metric-value">HK$ {current_price}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">目標價格</span>
                        <span class="metric-value">HK$ {target_price}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">上漲空間</span>
                        <span class="metric-value">{upside_potential}%</span>
                    </div>
                </div>
                
                <div class="metric-item">
                    <h4>📊 評分詳情</h4>
                    <div class="metric">
                        <span class="metric-label">基本面評分</span>
                        <span class="metric-value">{fundamental_score}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">技術面評分</span>
                        <span class="metric-value">{technical_score}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">綜合評分</span>
                        <span class="metric-value">{overall_score}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🏢 公司基本信息</h2>
            <div class="metric-grid">
                <div class="metric-item">
                    <h4>📋 基本資料</h4>
                    <div class="metric">
                        <span class="metric-label">股票代碼</span>
                        <span class="metric-value">{symbol}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">公司名稱</span>
                        <span class="metric-value">{stock_info.get('name', symbol)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">所屬行業</span>
                        <span class="metric-value">{stock_info.get('sector', '未分類')}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">市值</span>
                        <span class="metric-value">{format_market_cap(stock_info.get('market_cap', 0))}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">PE比率</span>
                        <span class="metric-value">{safe_format(stock_info.get('pe_ratio', 0))}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="disclaimer">
            <h3>⚠️ 重要聲明</h3>
            <p>
                本報告僅供參考，不構成投資建議。投資有風險，入市需謹慎。
                所有分析基於公開數據，可能存在延遲或不準確性。
                投資決策應基於個人風險承受能力和投資目標，建議諮詢專業投資顧問。
            </p>
        </div>
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            print(f"Error generating simple HTML report: {e}")
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1>報告生成錯誤</h1>
                <p>錯誤信息: {str(e)}</p>
                <p>請稍後重試或聯繫技術支持。</p>
            </body>
            </html>
            """
    
    def generate_pdf_report(self, analysis_data: Dict) -> str:
        """生成報告文件（HTML格式）"""
        try:
            # 確保輸出目錄存在
            output_dir = "../data/reports"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成HTML內容
            html_content = self.generate_simple_html_report(analysis_data)
            
            # 生成文件名
            symbol = analysis_data.get('symbol', 'UNKNOWN')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_filename = f"{symbol}_report_{timestamp}.html"
            html_path = os.path.join(output_dir, html_filename)
            
            # 保存HTML文件
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Report saved as HTML: {html_path}")
            return html_path
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None