import os
from jinja2 import Template
from datetime import datetime
from typing import Dict
import json

class ReportGenerator:
    def __init__(self):
        self.template_dir = "templates"
        os.makedirs(self.template_dir, exist_ok=True)
        self.create_templates()
    
    def create_templates(self):
        """創建報告模板"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ symbol }} 投資分析報告</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.2em;
            margin-top: 10px;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .card.recommendation {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .card.risk {
            background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
        }
        .card.score {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .card h3 {
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }
        .card .value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #2c3e50;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-bottom: 20px;
        }
        .analysis-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .analysis-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .analysis-item h4 {
            color: #2c3e50;
            margin: 0 0 15px 0;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            font-weight: 500;
            color: #34495e;
        }
        .metric-value {
            font-weight: bold;
            color: #2c3e50;
        }
        .score-bar {
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
            transition: width 0.3s ease;
        }
        .disclaimer {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }
        .disclaimer h3 {
            color: #856404;
            margin: 0 0 10px 0;
        }
        .disclaimer p {
            color: #856404;
            margin: 0;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .analysis-grid {
                grid-template-columns: 1fr;
            }
            .summary-cards {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ symbol }} 投資分析報告</h1>
            <div class="subtitle">{{ stock_name }} | 生成時間: {{ analysis_date }}</div>
        </div>

        <div class="summary-cards">
            <div class="card recommendation">
                <h3>投資建議</h3>
                <div class="value">{{ recommendation }}</div>
                <div>信心度: {{ confidence }}</div>
            </div>
            <div class="card score">
                <h3>綜合評分</h3>
                <div class="value">{{ "%.1f"|format(overall_score) }}</div>
                <div>滿分 100</div>
            </div>
            <div class="card risk">
                <h3>風險等級</h3>
                <div class="value">{{ risk_level }}</div>
                <div>波動率: {{ "%.1f%"|format(volatility * 100) if volatility else "計算中" }}</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 核心指標</h2>
            <div class="analysis-grid">
                <div class="analysis-item">
                    <h4>價格信息</h4>
                                    <div class="metric">
                    <span class="metric-label">當前價格</span>
                    <span class="metric-value">${{ current_price|round(2) if current_price else "數據不可用" }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">目標價格</span>
                    <span class="metric-value">${{ target_price|round(2) if target_price else "計算中" }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">上漲空間</span>
                    <span class="metric-value">{{ upside_potential|round(1) if upside_potential else "計算中" }}%</span>
                </div>
                </div>
                
                <div class="analysis-item">
                    <h4>評分詳情</h4>
                    <div class="metric">
                        <span class="metric-label">基本面評分</span>
                        <span class="metric-value">{{ "%.1f"|format(fundamental_score) }}</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {{ fundamental_score }}%"></div>
                    </div>
                    <div class="metric">
                        <span class="metric-label">技術面評分</span>
                        <span class="metric-value">{{ "%.1f"|format(technical_score) }}</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {{ technical_score }}%"></div>
                    </div>
                </div>
            </div>
        </div>

        {% if fundamental_analysis %}
        <div class="section">
            <h2>📈 基本面分析</h2>
            <div class="analysis-grid">
                {% if fundamental_analysis.pe_analysis %}
                <div class="analysis-item">
                    <h4>估值指標</h4>
                    <div class="metric">
                        <span class="metric-label">PE比率</span>
                        <span class="metric-value">{{ "%.2f"|format(fundamental_analysis.pe_analysis.ratio) }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">PB比率</span>
                        <span class="metric-value">{{ "%.2f"|format(fundamental_analysis.pb_analysis.ratio) if fundamental_analysis.pb_analysis else "數據不可用" }}</span>
                    </div>
                </div>
                {% endif %}
                
                {% if fundamental_analysis.roe_analysis %}
                <div class="analysis-item">
                    <h4>盈利能力</h4>
                    <div class="metric">
                        <span class="metric-label">ROE</span>
                        <span class="metric-value">{{ "%.1f%"|format(fundamental_analysis.roe_analysis.ratio * 100) }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">利潤率</span>
                        <span class="metric-value">{{ "%.1f%"|format(fundamental_analysis.margin_analysis.ratio * 100) if fundamental_analysis.margin_analysis else "N/A" }}</span>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        {% if technical_analysis %}
        <div class="section">
            <h2>📉 技術面分析</h2>
            <div class="analysis-grid">
                {% if technical_analysis.rsi_analysis %}
                <div class="analysis-item">
                    <h4>動量指標</h4>
                    <div class="metric">
                        <span class="metric-label">RSI</span>
                        <span class="metric-value">{{ "%.1f"|format(technical_analysis.rsi_analysis.value) }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">MACD</span>
                        <span class="metric-value">{{ "%.3f"|format(technical_analysis.macd_analysis.macd) if technical_analysis.macd_analysis else "N/A" }}</span>
                    </div>
                </div>
                {% endif %}
                
                {% if technical_analysis.ma_analysis %}
                <div class="analysis-item">
                    <h4>趨勢指標</h4>
                    <div class="metric">
                        <span class="metric-label">SMA 20</span>
                        <span class="metric-value">${{ "%.2f"|format(technical_analysis.ma_analysis.sma_20) }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">SMA 50</span>
                        <span class="metric-value">${{ "%.2f"|format(technical_analysis.ma_analysis.sma_50) }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">SMA 200</span>
                        <span class="metric-value">${{ "%.2f"|format(technical_analysis.ma_analysis.sma_200) }}</span>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        {% if risk_metrics %}
        <div class="section">
            <h2>⚠️ 風險分析</h2>
            <div class="analysis-grid">
                <div class="analysis-item">
                    <h4>風險指標</h4>
                    <div class="metric">
                        <span class="metric-label">年化波動率</span>
                        <span class="metric-value">{{ "%.1f%"|format(risk_metrics.volatility * 100) if risk_metrics.volatility else "N/A" }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">最大回撤</span>
                        <span class="metric-value">{{ "%.1f%"|format(risk_metrics.max_drawdown * 100) if risk_metrics.max_drawdown else "N/A" }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">VaR (95%)</span>
                        <span class="metric-value">{{ "%.1f%"|format(risk_metrics.var_95 * 100) if risk_metrics.var_95 else "N/A" }}</span>
                    </div>
                </div>
                
                <div class="analysis-item">
                    <h4>風險調整收益</h4>
                    <div class="metric">
                        <span class="metric-label">夏普比率</span>
                        <span class="metric-value">{{ "%.2f"|format(risk_metrics.sharpe_ratio) if risk_metrics.sharpe_ratio else "N/A" }}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Beta係數</span>
                        <span class="metric-value">{{ "%.2f"|format(risk_metrics.beta) if risk_metrics.beta else "N/A" }}</span>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

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
        
        template_path = os.path.join(self.template_dir, "report_template.html")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
    
    def generate_html_report(self, analysis_data: Dict) -> str:
        """生成HTML報告"""
        try:
            template_path = os.path.join(self.template_dir, "report_template.html")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            # 準備模板數據
            recommendation_data = analysis_data.get('recommendation', {})
            fundamental_analysis = recommendation_data.get('details', {}).get('fundamental_analysis', {})
            technical_analysis = recommendation_data.get('details', {}).get('technical_analysis', {})
            risk_metrics = recommendation_data.get('details', {}).get('risk_metrics', {})
            
            template_data = {
                'symbol': analysis_data.get('symbol', 'N/A'),
                'stock_name': analysis_data.get('stock_info', {}).get('name', 'N/A'),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'recommendation': recommendation_data.get('recommendation', 'N/A'),
                'confidence': recommendation_data.get('confidence', 'N/A'),
                'overall_score': recommendation_data.get('overall_score', 0),
                'fundamental_score': recommendation_data.get('fundamental_score', 0),
                'technical_score': recommendation_data.get('technical_score', 0),
                'risk_level': recommendation_data.get('risk_level', 'N/A'),
                'current_price': recommendation_data.get('current_price', 0),
                'target_price': recommendation_data.get('target_price', 0),
                'upside_potential': recommendation_data.get('upside_potential', 0),
                'volatility': risk_metrics.get('volatility', 0),
                'fundamental_analysis': fundamental_analysis,
                'technical_analysis': technical_analysis,
                'risk_metrics': risk_metrics
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return f"<html><body><h1>報告生成錯誤</h1><p>{str(e)}</p></body></html>"
    
    def generate_pdf_report(self, analysis_data: Dict) -> str:
        """生成PDF報告（使用HTML替代方案）"""
        try:
            # 生成HTML內容
            html_content = self.generate_html_report(analysis_data)
            
            # 確保輸出目錄存在
            output_dir = "../data/reports"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            symbol = analysis_data.get('symbol', 'UNKNOWN')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 嘗試多種PDF生成方法
            pdf_methods = [
                self._try_weasyprint,
                self._try_pdfkit,
                self._fallback_html
            ]
            
            for method in pdf_methods:
                try:
                    result = method(html_content, symbol, timestamp, output_dir)
                    if result:
                        return result
                except Exception as e:
                    print(f"PDF method failed: {e}")
                    continue
            
            # 如果所有方法都失敗，返回None
            return None
                
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return None
    
    def _try_weasyprint(self, html_content, symbol, timestamp, output_dir):
        """嘗試使用WeasyPrint生成PDF"""
        try:
            # WeasyPrint is optional - fallback to HTML if not available
            try:
                from weasyprint import HTML
                pdf_filename = f"{symbol}_report_{timestamp}.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                HTML(string=html_content).write_pdf(pdf_path)
                return pdf_path
            except ImportError:
                raise Exception("WeasyPrint not available")
        except ImportError:
            raise Exception("WeasyPrint not available")
    
    def _try_pdfkit(self, html_content, symbol, timestamp, output_dir):
        """嘗試使用pdfkit生成PDF"""
        try:
            # pdfkit is optional - fallback to HTML if not available
            try:
                import pdfkit
                pdf_filename = f"{symbol}_report_{timestamp}.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                pdfkit.from_string(html_content, pdf_path)
                return pdf_path
            except ImportError:
                raise Exception("pdfkit not available")
        except ImportError:
            raise Exception("pdfkit not available")
    
    def _fallback_html(self, html_content, symbol, timestamp, output_dir):
        """備用方案：生成HTML文件"""
        html_filename = f"{symbol}_report_{timestamp}.html"
        html_path = os.path.join(output_dir, html_filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"PDF generation failed, saved as HTML: {html_path}")
        return html_path
    
    def generate_summary_report(self, multiple_analysis: Dict) -> str:
        """生成多股票摘要報告"""
        try:
            summary_template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投資組合分析摘要</title>
    <style>
        body { font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .stock-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .stock-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #f9f9f9; }
        .stock-header { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .recommendation { padding: 5px 10px; border-radius: 5px; color: white; display: inline-block; }
        .buy { background: #27ae60; }
        .hold { background: #f39c12; }
        .sell { background: #e74c3c; }
        .metric { display: flex; justify-content: space-between; margin: 5px 0; }
        .score { font-size: 1.5em; font-weight: bold; text-align: center; margin: 10px 0; }
            </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>投資組合分析摘要</h1>
            <p>生成時間: {{ analysis_date }}</p>
        </div>
        
        <div class="stock-grid">
            {% for symbol, data in stocks.items() %}
            <div class="stock-card">
                <div class="stock-header">{{ symbol }}</div>
                <div class="recommendation {{ data.recommendation.lower() }}">
                    {{ data.recommendation }}
                </div>
                <div class="score">{{ "%.1f"|format(data.overall_score) }}</div>
                <div class="metric">
                    <span>當前價格:</span>
                    <span>${{ "%.2f"|format(data.current_price) if data.current_price else "N/A" }}</span>
                </div>
                <div class="metric">
                    <span>目標價格:</span>
                    <span>${{ "%.2f"|format(data.target_price) if data.target_price else "N/A" }}</span>
                </div>
                <div class="metric">
                    <span>風險等級:</span>
                    <span>{{ data.risk_level }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
            """
            
            template = Template(summary_template)
            
            # 準備數據
            stocks_data = {}
            for symbol, analysis in multiple_analysis.items():
                if 'recommendation' in analysis:
                    rec = analysis['recommendation']
                    stocks_data[symbol] = {
                        'recommendation': rec.get('recommendation', 'N/A'),
                        'overall_score': rec.get('overall_score', 0),
                        'current_price': rec.get('current_price', 0),
                        'target_price': rec.get('target_price', 0),
                        'risk_level': rec.get('risk_level', 'N/A')
                    }
            
            template_data = {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'stocks': stocks_data
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            print(f"Error generating summary report: {e}")
            return f"<html><body><h1>摘要報告生成錯誤</h1><p>{str(e)}</p></body></html>"

# 使用示例
if __name__ == "__main__":
    # 測試報告生成
    sample_data = {
        'symbol': 'AAPL',
        'recommendation': {
            'overall_score': 75.5,
            'fundamental_score': 80.0,
            'technical_score': 70.0,
            'recommendation': '買入',
            'confidence': '高',
            'risk_level': '中等風險',
            'current_price': 150.25,
            'target_price': 165.00,
            'upside_potential': 9.8
        }
    }
    
    generator = ReportGenerator()
    html_report = generator.generate_html_report(sample_data)
    print("HTML report generated successfully")