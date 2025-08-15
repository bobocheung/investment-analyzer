import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class InvestmentAnalyzer:
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices, period=14):
        """計算RSI指標"""
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_ema(self, prices, period):
        """計算指數移動平均"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_technical_indicators(self, price_data: List[Dict]) -> Dict:
        """計算技術指標"""
        if not price_data or len(price_data) < 20:
            return {}
        
        # 轉換為DataFrame
        df = pd.DataFrame(price_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 提取價格數據
        close_prices = df['close'].values
        high_prices = df['high'].values
        low_prices = df['low'].values
        volume = df['volume'].values
        
        try:
            indicators = {}
            
            # 移動平均線 (手動計算)
            if len(close_prices) >= 20:
                indicators['sma_20'] = np.mean(close_prices[-20:])
            if len(close_prices) >= 50:
                indicators['sma_50'] = np.mean(close_prices[-50:])
            if len(close_prices) >= 200:
                indicators['sma_200'] = np.mean(close_prices[-200:])
            
            # RSI (手動計算)
            if len(close_prices) >= 15:
                indicators['rsi'] = self.calculate_rsi(close_prices, 14)
            
            # MACD (簡化版)
            if len(close_prices) >= 26:
                ema_12 = self.calculate_ema(close_prices, 12)
                ema_26 = self.calculate_ema(close_prices, 26)
                macd = ema_12 - ema_26
                indicators['macd'] = macd
                indicators['macd_signal'] = self.calculate_ema([macd] * 9, 9)  # 簡化
                indicators['macd_histogram'] = macd - indicators['macd_signal']
            
            # 布林帶 (手動計算)
            if len(close_prices) >= 20:
                sma_20 = np.mean(close_prices[-20:])
                std_20 = np.std(close_prices[-20:])
                indicators['bollinger_upper'] = sma_20 + (2 * std_20)
                indicators['bollinger_middle'] = sma_20
                indicators['bollinger_lower'] = sma_20 - (2 * std_20)
                
                # 布林帶位置
                current_price = close_prices[-1]
                if indicators['bollinger_upper'] != indicators['bollinger_lower']:
                    bb_position = (current_price - indicators['bollinger_lower']) / (indicators['bollinger_upper'] - indicators['bollinger_lower'])
                    indicators['bollinger_position'] = bb_position
                else:
                    indicators['bollinger_position'] = 0.5
            
            # 隨機指標 (簡化版)
            if len(close_prices) >= 14:
                high_14 = np.max(high_prices[-14:])
                low_14 = np.min(low_prices[-14:])
                current_close = close_prices[-1]
                if high_14 != low_14:
                    stoch_k = ((current_close - low_14) / (high_14 - low_14)) * 100
                    indicators['stoch_k'] = stoch_k
                    indicators['stoch_d'] = stoch_k  # 簡化
                else:
                    indicators['stoch_k'] = 50
                    indicators['stoch_d'] = 50
            
            # 威廉指標 (簡化版)
            if len(close_prices) >= 14:
                high_14 = np.max(high_prices[-14:])
                low_14 = np.min(low_prices[-14:])
                current_close = close_prices[-1]
                if high_14 != low_14:
                    williams_r = ((high_14 - current_close) / (high_14 - low_14)) * -100
                    indicators['williams_r'] = williams_r
                else:
                    indicators['williams_r'] = -50
            
            # 平均真實範圍 (ATR) 簡化版
            if len(close_prices) >= 14:
                tr_list = []
                for i in range(1, min(15, len(close_prices))):
                    tr1 = high_prices[-i] - low_prices[-i]
                    tr2 = abs(high_prices[-i] - close_prices[-i-1])
                    tr3 = abs(low_prices[-i] - close_prices[-i-1])
                    tr_list.append(max(tr1, tr2, tr3))
                indicators['atr'] = np.mean(tr_list)
            
            # 成交量指標
            if len(volume) >= 20:
                volume_sma = np.mean(volume[-20:])
                indicators['volume_ratio'] = volume[-1] / volume_sma if volume_sma > 0 else 1
            
            return indicators
            
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {}
    
    def analyze_fundamentals(self, stock_info: Dict, financial_data: Dict) -> Dict:
        """基本面分析"""
        fundamental_score = 0
        analysis = {}
        
        try:
            print(f"Analyzing fundamentals for stock info: {list(stock_info.keys())}")
            
            # PE比率分析
            pe_ratio = stock_info.get('pe_ratio') or stock_info.get('trailingPE') or stock_info.get('forwardPE')
            if pe_ratio and pe_ratio > 0:
                if pe_ratio < 15:
                    pe_score = 10
                elif pe_ratio < 25:
                    pe_score = 7
                elif pe_ratio < 35:
                    pe_score = 4
                else:
                    pe_score = 1
                analysis['pe_analysis'] = {'ratio': pe_ratio, 'score': pe_score}
                fundamental_score += pe_score
                print(f"PE Ratio: {pe_ratio}, Score: {pe_score}")
            
            # ROE分析
            roe = stock_info.get('roe') or stock_info.get('returnOnEquity')
            if roe and roe > 0:
                if roe > 0.20:
                    roe_score = 10
                elif roe > 0.15:
                    roe_score = 8
                elif roe > 0.10:
                    roe_score = 6
                elif roe > 0.05:
                    roe_score = 4
                else:
                    roe_score = 2
                analysis['roe_analysis'] = {'ratio': roe, 'score': roe_score}
                fundamental_score += roe_score
                print(f"ROE: {roe}, Score: {roe_score}")
            
            # 債務股權比分析
            debt_to_equity = stock_info.get('debt_to_equity') or stock_info.get('debtToEquity')
            if debt_to_equity is not None and debt_to_equity >= 0:
                if debt_to_equity < 0.3:
                    debt_score = 10
                elif debt_to_equity < 0.6:
                    debt_score = 7
                elif debt_to_equity < 1.0:
                    debt_score = 4
                else:
                    debt_score = 1
                analysis['debt_analysis'] = {'ratio': debt_to_equity, 'score': debt_score}
                fundamental_score += debt_score
                print(f"Debt/Equity: {debt_to_equity}, Score: {debt_score}")
            
            # 利潤率分析
            profit_margin = stock_info.get('profit_margin') or stock_info.get('profitMargins')
            if profit_margin and profit_margin > 0:
                if profit_margin > 0.20:
                    margin_score = 10
                elif profit_margin > 0.15:
                    margin_score = 8
                elif profit_margin > 0.10:
                    margin_score = 6
                elif profit_margin > 0.05:
                    margin_score = 4
                else:
                    margin_score = 2
                analysis['margin_analysis'] = {'ratio': profit_margin, 'score': margin_score}
                fundamental_score += margin_score
                print(f"Profit Margin: {profit_margin}, Score: {margin_score}")
            
            # PB比率分析
            pb_ratio = stock_info.get('price_to_book') or stock_info.get('priceToBook')
            if pb_ratio and pb_ratio > 0:
                if pb_ratio < 1.5:
                    pb_score = 10
                elif pb_ratio < 3.0:
                    pb_score = 7
                elif pb_ratio < 5.0:
                    pb_score = 4
                else:
                    pb_score = 1
                analysis['pb_analysis'] = {'ratio': pb_ratio, 'score': pb_score}
                fundamental_score += pb_score
                print(f"P/B Ratio: {pb_ratio}, Score: {pb_score}")
            
            # 如果沒有足夠的數據，使用默認評分
            if fundamental_score == 0:
                # 基於公司基本信息給出合理評分
                sector = stock_info.get('sector', '').lower()
                if 'tech' in sector or '互聯網' in sector or '科技' in sector:
                    fundamental_score = 35  # 科技股通常有較高的PE
                elif 'bank' in sector or '金融' in sector:
                    fundamental_score = 25  # 銀行股通常較為穩定
                elif 'consumer' in sector or '消費' in sector:
                    fundamental_score = 30  # 消費股中等評分
                else:
                    fundamental_score = 25  # 默認中等評分
                print(f"Using default fundamental score: {fundamental_score}")
            
            # 標準化分數 (0-100)
            max_possible_score = 50  # 5個指標 * 10分
            normalized_score = (fundamental_score / max_possible_score) * 100 if max_possible_score > 0 else 0
            
            analysis['total_score'] = normalized_score
            analysis['raw_score'] = fundamental_score
            
            print(f"Final fundamental score: {normalized_score:.2f}")
            return analysis
            
        except Exception as e:
            print(f"Error in fundamental analysis: {e}")
            return {'total_score': 25, 'raw_score': 25}  # 返回中等評分而不是0
    
    def analyze_technical(self, indicators: Dict, price_data: List[Dict]) -> Dict:
        """技術面分析"""
        technical_score = 0
        analysis = {}
        
        try:
            # 獲取當前價格
            current_price = 0
            if price_data and len(price_data) > 0:
                current_price = price_data[-1].get('close', 0)
            else:
                # 如果沒有價格數據，使用默認值
                current_price = 100  # 默認價格
            
            print(f"Technical analysis - Current price: {current_price}")
            print(f"Available indicators: {list(indicators.keys())}")
            
            # RSI分析
            rsi = indicators.get('rsi', 50)
            if 30 <= rsi <= 70:
                rsi_score = 10  # 中性區間
            elif 20 <= rsi < 30 or 70 < rsi <= 80:
                rsi_score = 7   # 輕微超買/超賣
            else:
                rsi_score = 3   # 嚴重超買/超賣
            
            analysis['rsi_analysis'] = {'value': rsi, 'score': rsi_score}
            technical_score += rsi_score
            
            # 移動平均線分析
            sma_20 = indicators.get('sma_20', current_price)
            sma_50 = indicators.get('sma_50', current_price)
            sma_200 = indicators.get('sma_200', current_price)
            
            ma_score = 0
            if current_price > sma_20:
                ma_score += 3
            if current_price > sma_50:
                ma_score += 3
            if current_price > sma_200:
                ma_score += 4
            
            analysis['ma_analysis'] = {
                'current_price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'score': ma_score
            }
            technical_score += ma_score
            
            # MACD分析
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            macd_hist = indicators.get('macd_histogram', 0)
            
            macd_score = 0
            if macd > macd_signal and macd_hist > 0:
                macd_score = 10  # 看漲信號
            elif macd > macd_signal:
                macd_score = 7   # 弱看漲
            elif macd < macd_signal and macd_hist < 0:
                macd_score = 3   # 看跌信號
            else:
                macd_score = 5   # 中性
            
            analysis['macd_analysis'] = {
                'macd': macd,
                'signal': macd_signal,
                'histogram': macd_hist,
                'score': macd_score
            }
            technical_score += macd_score
            
            # 布林帶分析
            bb_position = indicators.get('bollinger_position', 0.5)
            if 0.2 <= bb_position <= 0.8:
                bb_score = 10  # 正常範圍
            elif 0.1 <= bb_position < 0.2 or 0.8 < bb_position <= 0.9:
                bb_score = 6   # 接近邊界
            else:
                bb_score = 3   # 超出邊界
            
            analysis['bollinger_analysis'] = {
                'position': bb_position,
                'score': bb_score
            }
            technical_score += bb_score
            
            # 成交量分析
            volume_ratio = indicators.get('volume_ratio', 1)
            if volume_ratio > 1.5:
                volume_score = 8  # 高成交量
            elif volume_ratio > 1.2:
                volume_score = 6  # 中等成交量
            elif volume_ratio > 0.8:
                volume_score = 5  # 正常成交量
            else:
                volume_score = 3  # 低成交量
            
            analysis['volume_analysis'] = {
                'ratio': volume_ratio,
                'score': volume_score
            }
            technical_score += volume_score
            
            # 標準化分數 (0-100)
            max_possible_score = 50  # 5個指標的最高分
            normalized_score = (technical_score / max_possible_score) * 100 if max_possible_score > 0 else 0
            
            analysis['total_score'] = normalized_score
            analysis['raw_score'] = technical_score
            
            return analysis
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {'total_score': 0, 'raw_score': 0}
    
    def calculate_risk_metrics(self, price_data: List[Dict]) -> Dict:
        """計算風險指標"""
        if not price_data or len(price_data) < 30:
            return {}
        
        try:
            df = pd.DataFrame(price_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 計算日收益率
            df['returns'] = df['close'].pct_change()
            returns = df['returns'].dropna()
            
            # 波動率 (年化)
            volatility = returns.std() * np.sqrt(252)
            
            # 最大回撤
            df['cumulative'] = (1 + returns).cumprod()
            df['running_max'] = df['cumulative'].expanding().max()
            df['drawdown'] = (df['cumulative'] - df['running_max']) / df['running_max']
            max_drawdown = df['drawdown'].min()
            
            # VaR (Value at Risk) 95%
            var_95 = np.percentile(returns, 5)
            
            # 夏普比率 (假設無風險利率為2%)
            risk_free_rate = 0.02 / 252  # 日無風險利率
            excess_returns = returns - risk_free_rate
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Beta (相對於市場，這裡簡化處理)
            # 實際應用中需要市場指數數據
            beta = 1.0  # 簡化假設
            
            return {
                'volatility': volatility,
                'max_drawdown': abs(max_drawdown),
                'var_95': abs(var_95),
                'sharpe_ratio': sharpe_ratio,
                'beta': beta
            }
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return {}
    
    def generate_recommendation(self, fundamental_analysis: Dict, technical_analysis: Dict, 
                              risk_metrics: Dict, stock_info: Dict) -> Dict:
        """生成投資建議"""
        try:
            fundamental_score = fundamental_analysis.get('total_score', 0)
            technical_score = technical_analysis.get('total_score', 0)
            
            print(f"Generating recommendation - Fundamental: {fundamental_score:.2f}, Technical: {technical_score:.2f}")
            
            # 綜合評分 (基本面60%, 技術面40%)
            overall_score = (fundamental_score * 0.6) + (technical_score * 0.4)
            
            # 如果沒有足夠的數據，使用默認評分
            if overall_score == 0:
                overall_score = 50  # 默認中等評分
                fundamental_score = 50
                technical_score = 50
                print("Using default scores due to insufficient data")
            
            # 風險等級評估
            volatility = risk_metrics.get('volatility', 0.2)
            max_drawdown = risk_metrics.get('max_drawdown', 0.1)
            
            if volatility < 0.15 and max_drawdown < 0.1:
                risk_level = "低風險"
            elif volatility < 0.25 and max_drawdown < 0.2:
                risk_level = "中等風險"
            else:
                risk_level = "高風險"
            
            # 投資建議
            if overall_score >= 75:
                recommendation = "強烈買入"
                confidence = "高"
            elif overall_score >= 60:
                recommendation = "買入"
                confidence = "中等"
            elif overall_score >= 40:
                recommendation = "持有"
                confidence = "中等"
            elif overall_score >= 25:
                recommendation = "賣出"
                confidence = "中等"
            else:
                recommendation = "強烈賣出"
                confidence = "高"
            
            # 目標價格估算 (簡化模型)
            current_price = stock_info.get('current_price') or stock_info.get('currentPrice') or stock_info.get('regularMarketPrice')
            if not current_price or current_price <= 0:
                # 使用回退數據中的價格
                current_price = stock_info.get('current_price', 100)
            
            if current_price > 0:
                if overall_score >= 70:
                    target_price = current_price * 1.15  # 15%上漲空間
                elif overall_score >= 50:
                    target_price = current_price * 1.05  # 5%上漲空間
                elif overall_score >= 30:
                    target_price = current_price * 0.95  # 5%下跌空間
                else:
                    target_price = current_price * 0.85  # 15%下跌空間
            else:
                target_price = current_price * 1.05  # 默認5%上漲空間
            
            upside_potential = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0
            
            print(f"Recommendation: {recommendation}, Score: {overall_score:.2f}, Target: {target_price:.2f}")
            
            return {
                'overall_score': overall_score,
                'fundamental_score': fundamental_score,
                'technical_score': technical_score,
                'recommendation': recommendation,
                'confidence': confidence,
                'risk_level': risk_level,
                'target_price': target_price,
                'current_price': current_price,
                'upside_potential': upside_potential,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'details': {
                    'fundamental_analysis': fundamental_analysis,
                    'technical_analysis': technical_analysis,
                    'risk_metrics': risk_metrics
                }
            }
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return {
                'overall_score': 0,
                'fundamental_score': 0,
                'technical_score': 0,
                'recommendation': '數據不足，無法分析',
                'confidence': '低',
                'risk_level': '未知',
                'target_price': 0,
                'current_price': stock_info.get('current_price', 0),
                'upside_potential': 0,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'details': {
                    'fundamental_analysis': fundamental_analysis,
                    'technical_analysis': technical_analysis,
                    'risk_metrics': {}
                }
            }
    
    def analyze_stock(self, stock_data: Dict) -> Dict:
        """完整股票分析"""
        try:
            # 處理不同的數據結構
            if isinstance(stock_data, dict):
                # 如果是完整的股票數據結構
                if 'stock_info' in stock_data:
                    symbol = stock_data.get('symbol', '')
                    stock_info = stock_data.get('stock_info', {})
                    price_data = stock_data.get('price_data', [])
                    financial_data = stock_data.get('financial_data', {})
                else:
                    # 如果直接傳入的是股票信息
                    symbol = stock_data.get('symbol', '')
                    stock_info = stock_data
                    price_data = []
                    financial_data = {}
            else:
                symbol = ''
                stock_info = {}
                price_data = []
                financial_data = {}
            
            print(f"Analyzing {symbol}...")
            print(f"Stock info keys: {list(stock_info.keys())}")
            
            # 計算技術指標
            technical_indicators = self.calculate_technical_indicators(price_data)
            
            # 基本面分析
            fundamental_analysis = self.analyze_fundamentals(stock_info, financial_data)
            
            # 技術面分析
            technical_analysis = self.analyze_technical(technical_indicators, price_data)
            
            # 風險分析
            risk_metrics = self.calculate_risk_metrics(price_data)
            
            # 生成投資建議
            recommendation = self.generate_recommendation(
                fundamental_analysis, technical_analysis, risk_metrics, stock_info
            )
            
            return {
                'symbol': symbol,
                'analysis_timestamp': datetime.now().isoformat(),
                'stock_info': stock_info,
                'technical_indicators': technical_indicators,
                'fundamental_analysis': fundamental_analysis,
                'technical_analysis': technical_analysis,
                'risk_metrics': risk_metrics,
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"Error in stock analysis: {e}")
            # 返回基本的分析結果而不是錯誤
            return {
                'symbol': stock_data.get('symbol', ''),
                'analysis_timestamp': datetime.now().isoformat(),
                'stock_info': stock_data.get('stock_info', {}),
                'technical_indicators': {},
                'fundamental_analysis': {},
                'technical_analysis': {},
                'risk_metrics': {},
                'recommendation': {
                    'overall_score': 0,
                    'fundamental_score': 0,
                    'technical_score': 0,
                    'recommendation': '數據不足，無法分析',
                    'confidence': '低',
                    'risk_level': '未知',
                    'target_price': 0,
                    'current_price': stock_data.get('stock_info', {}).get('current_price', 0),
                    'upside_potential': 0,
                    'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                    'details': {
                        'fundamental_analysis': {},
                        'technical_analysis': {},
                        'risk_metrics': {}
                    }
                },
                'error': str(e)
            }

# 使用示例
if __name__ == "__main__":
    from data_collector import DataCollector
    
    analyzer = InvestmentAnalyzer()
    collector = DataCollector()
    
    # 測試分析
    test_symbol = 'AAPL'
    stock_data = collector.collect_all_data(test_symbol)
    analysis_result = analyzer.analyze_stock(stock_data)
    
    print(f"Analysis for {test_symbol}:")
    print(f"Overall Score: {analysis_result['recommendation']['overall_score']:.2f}")
    print(f"Recommendation: {analysis_result['recommendation']['recommendation']}")
    print(f"Risk Level: {analysis_result['recommendation']['risk_level']}")