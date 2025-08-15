import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import time
import random
from dotenv import load_dotenv
from cache_manager import cache_manager, cached

load_dotenv()

class DataCollector:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.fred_api_key = os.getenv('FRED_API_KEY', 'demo')
        self.request_delay = 1.0  # 請求間隔（秒）
        self.max_retries = 3  # 最大重試次數
    
    def safe_yfinance_request(self, symbol, max_retries=3, delay=1.0):
        """安全的yfinance請求，帶重試機制"""
        for attempt in range(max_retries):
            try:
                # 添加隨機延遲避免被限制
                if attempt > 0:
                    time.sleep(delay * (attempt + 1) + random.uniform(0.5, 1.5))
                
                ticker = yf.Ticker(symbol)
                
                # 嘗試獲取基本信息來驗證ticker是否有效
                try:
                    info = ticker.info
                    # 即使info為空，也返回ticker讓其他方法處理
                    return ticker
                except Exception as info_error:
                    print(f"Info fetch failed for {symbol}: {str(info_error)}")
                    # 繼續嘗試其他方法
                    return ticker
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt == max_retries - 1:
                    print(f"All attempts failed for {symbol}")
                    return None
                continue
        
        return None
    
    def _get_fallback_price_data(self, symbol: str, period: str = "1y") -> List[Dict]:
        """當Yahoo Finance失敗時的回退價格數據"""
        print(f"Generating fallback price data for {symbol}")
        
        # 生成模擬的價格數據
        base_price = 100.0  # 基礎價格
        price_data = []
        end_date = datetime.now()
        
        # 根據period生成不同數量的數據點
        if period == "5d":
            days = 5
        elif period == "1mo":
            days = 30
        elif period == "3mo":
            days = 90
        elif period == "6mo":
            days = 180
        else:  # 1y
            days = 365
        
        for i in range(days):
            date = end_date - timedelta(days=days-i-1)
            # 添加一些隨機波動
            variation = random.uniform(-0.05, 0.05)
            price = base_price * (1 + variation)
            
            price_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(price, 2),
                'high': round(price * 1.02, 2),
                'low': round(price * 0.98, 2),
                'close': round(price, 2),
                'volume': random.randint(1000000, 10000000)
            })
        
        return price_data

    def _get_fallback_stock_info(self, symbol: str) -> Dict:
        """當Yahoo Finance失敗時的回退股票信息"""
        print(f"Using fallback data for {symbol}")
        
        # 基於股票代碼提供一些基本信息
        company_names = {
            '0700.HK': 'Tencent Holdings Ltd',
            '0005.HK': 'HSBC Holdings plc',
            '0941.HK': 'China Mobile Limited',
            '1398.HK': 'Industrial and Commercial Bank of China Limited',
            '3988.HK': 'Bank of China Limited',
            '0939.HK': 'China Construction Bank Corporation',
            '2318.HK': 'Ping An Insurance (Group) Company of China, Ltd.',
            '1299.HK': 'AIA Group Limited',
            '0388.HK': 'Hong Kong Exchanges and Clearing Limited',
            '0007.HK': 'WISDOM WEALTH'
        }
        
        return {
            'symbol': symbol,
            'name': company_names.get(symbol, symbol.replace('.HK', '')),
            'current_price': 0.0,
            'market_cap': 0,
            'pe_ratio': None,
            'pb_ratio': None,
            'dividend_yield': None,
            'beta': None,
            'eps': None,
            'book_value': None,
            'debt_to_equity': None,
            'roe': None,
            'sector': '未分類',
            'industry': '未分類',
            'currency': 'HKD',
            'exchange': 'HKG',
            'data_source': 'fallback',
            'last_updated': datetime.now().isoformat()
        }
    
    def get_stock_info(self, symbol: str) -> Dict:
        """獲取股票基本信息（帶緩存）"""
        # 先檢查緩存
        cached_data = cache_manager.get('stock_info', symbol)
        if cached_data:
            print(f"📦 Using cached stock info for {symbol}")
            return cached_data
        
        try:
            print(f"🌐 Fetching fresh stock info for {symbol}...")
            ticker = self.safe_yfinance_request(symbol)
            if not ticker:
                print(f"Failed to get ticker for {symbol}")
                fallback_data = self._get_fallback_stock_info(symbol)
                # 緩存回退數據（較短時間）
                cache_manager.set('stock_info', symbol, fallback_data)
                return fallback_data
            
            # 嘗試獲取info，如果失敗則使用回退數據
            try:
                info = ticker.info
                if not info or len(info) <= 1:
                    print(f"Empty info for {symbol}, using fallback data")
                    fallback_data = self._get_fallback_stock_info(symbol)
                    cache_manager.set('stock_info', symbol, fallback_data)
                    return fallback_data
            except Exception as e:
                print(f"Error getting info for {symbol}: {e}, using fallback data")
                fallback_data = self._get_fallback_stock_info(symbol)
                cache_manager.set('stock_info', symbol, fallback_data)
                return fallback_data
            
            # 處理缺失數據，提供更有意義的默認值
            def safe_get(key, default=None, data_type=None):
                value = info.get(key, default)
                if value is None or value == 'N/A' or (isinstance(value, (int, float)) and np.isnan(value)):
                    return default
                if data_type == 'float' and isinstance(value, (int, float)):
                    return float(value) if not np.isnan(value) else default
                return value
            
            # 獲取當前價格，嘗試多個字段
            current_price = (safe_get('currentPrice', 0, 'float') or 
                           safe_get('regularMarketPrice', 0, 'float') or 
                           safe_get('previousClose', 0, 'float'))
            
            # 獲取公司名稱，嘗試多個字段
            company_name = (safe_get('longName') or 
                          safe_get('shortName') or 
                          symbol)
            
            # 獲取行業信息
            sector = safe_get('sector') or '未分類'
            industry = safe_get('industry') or '未分類'
            
            stock_info = {
                'symbol': symbol,
                'name': company_name,
                'sector': sector,
                'industry': industry,
                'market_cap': safe_get('marketCap', 0, 'float'),
                'pe_ratio': safe_get('trailingPE', None, 'float'),
                'forward_pe': safe_get('forwardPE', None, 'float'),
                'price_to_book': safe_get('priceToBook', None, 'float'),
                'debt_to_equity': safe_get('debtToEquity', None, 'float'),
                'roe': safe_get('returnOnEquity', None, 'float'),
                'profit_margin': safe_get('profitMargins', None, 'float'),
                'current_price': current_price,
                'target_price': safe_get('targetMeanPrice', None, 'float'),
                'recommendation': safe_get('recommendationMean', None, 'float'),
                'data_source': 'yahoo_finance',
                'last_updated': datetime.now().isoformat()
            }
            
            # 緩存成功獲取的數據
            cache_manager.set('stock_info', symbol, stock_info)
            print(f"💾 Cached stock info for {symbol}")
            return stock_info
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            # 返回基本信息而不是空字典
            return {
                'symbol': symbol,
                'name': symbol,
                'sector': '數據不可用',
                'industry': '數據不可用',
                'market_cap': 0,
                'pe_ratio': None,
                'forward_pe': None,
                'price_to_book': None,
                'debt_to_equity': None,
                'roe': None,
                'profit_margin': None,
                'current_price': 0,
                'target_price': None,
                'recommendation': None
            }
    
    def get_stock_prices(self, symbol: str, period: str = "1y") -> List[Dict]:
        """獲取股價歷史數據（帶緩存）"""
        # 檢查緩存
        cache_key = f"{symbol}_{period}"
        cached_data = cache_manager.get('price_data', cache_key)
        if cached_data:
            print(f"📦 Using cached price data for {symbol} ({period})")
            return cached_data
        
        try:
            print(f"🌐 Fetching fresh price data for {symbol} ({period})...")
            ticker = self.safe_yfinance_request(symbol)
            if not ticker:
                print(f"Failed to get ticker for {symbol}")
                return []
            
            # 添加延遲避免請求過快
            time.sleep(self.request_delay)
            
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"No price data found for {symbol}, using fallback data")
                # 提供回退價格數據
                fallback_prices = self._get_fallback_price_data(symbol, period)
                cache_manager.set('price_data', cache_key, fallback_prices)
                return fallback_prices
            
            price_data = []
            for date, row in hist.iterrows():
                price_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'adj_close': float(row['Close'])  # Yahoo Finance已調整
                })
            
            # 緩存價格數據
            cache_manager.set('price_data', cache_key, price_data)
            print(f"💾 Cached {len(price_data)} price records for {symbol}")
            return price_data
            
        except Exception as e:
            print(f"Error fetching price data for {symbol}: {e}")
            return []
    
    def get_financial_statements(self, symbol: str) -> Dict:
        """獲取財務報表數據"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 獲取財務數據
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            if financials.empty or balance_sheet.empty:
                return {}
            
            # 獲取最新年度數據
            latest_year = financials.columns[0]
            
            financial_data = {
                'revenue': financials.loc['Total Revenue', latest_year] if 'Total Revenue' in financials.index else 0,
                'net_income': financials.loc['Net Income', latest_year] if 'Net Income' in financials.index else 0,
                'total_assets': balance_sheet.loc['Total Assets', latest_year] if 'Total Assets' in balance_sheet.index else 0,
                'total_debt': balance_sheet.loc['Total Debt', latest_year] if 'Total Debt' in balance_sheet.index else 0,
                'shareholders_equity': balance_sheet.loc['Stockholders Equity', latest_year] if 'Stockholders Equity' in balance_sheet.index else 0,
                'period': str(latest_year.year)
            }
            
            return financial_data
        except Exception as e:
            print(f"Error fetching financial data for {symbol}: {e}")
            return {}
    
    def get_economic_indicators(self) -> Dict:
        """獲取宏觀經濟指標（港股相關）"""
        # 檢查緩存
        cached_data = cache_manager.get('economic_indicators', 'hk_market')
        if cached_data:
            print("📦 Using cached economic indicators data")
            return cached_data
        
        indicators = {}
        
        try:
            # 獲取港股相關經濟指標
            # 使用Yahoo Finance獲取一些基本指標
            
            # 恆生指數
            hsi = yf.Ticker("^HSI")
            hsi_info = hsi.info
            hsi_hist = hsi.history(period="5d")
            
            if not hsi_hist.empty:
                current_hsi = hsi_hist['Close'][-1]
                prev_hsi = hsi_hist['Close'][0]
                hsi_change = ((current_hsi - prev_hsi) / prev_hsi) * 100
                
                indicators['恆生指數'] = {
                    'value': f"{current_hsi:.0f} ({hsi_change:+.2f}%)",
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # 港元匯率 (USD/HKD)
            usd_hkd = yf.Ticker("USDHKD=X")
            usd_hkd_hist = usd_hkd.history(period="5d")
            
            if not usd_hkd_hist.empty:
                current_rate = usd_hkd_hist['Close'][-1]
                indicators['美元兌港元'] = {
                    'value': f"{current_rate:.4f}",
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            
            # 中國A50指數 (代表內地經濟)
            try:
                a50 = yf.Ticker("000001.SS")  # 上證指數
                a50_hist = a50.history(period="5d")
                if not a50_hist.empty:
                    current_a50 = a50_hist['Close'][-1]
                    prev_a50 = a50_hist['Close'][0]
                    a50_change = ((current_a50 - prev_a50) / prev_a50) * 100
                    
                    indicators['上證指數'] = {
                        'value': f"{current_a50:.0f} ({a50_change:+.2f}%)",
                        'date': datetime.now().strftime('%Y-%m-%d')
                    }
            except:
                pass
            
            # 如果無法獲取數據，提供模擬數據
            if not indicators:
                indicators = {
                    '恆生指數': {'value': '17,500 (+0.5%)', 'date': datetime.now().strftime('%Y-%m-%d')},
                    '美元兌港元': {'value': '7.8200', 'date': datetime.now().strftime('%Y-%m-%d')},
                    '上證指數': {'value': '3,100 (-0.2%)', 'date': datetime.now().strftime('%Y-%m-%d')},
                    '港股通資金': {'value': '淨流入 15億', 'date': datetime.now().strftime('%Y-%m-%d')}
                }
        
        except Exception as e:
            print(f"Error fetching economic indicators: {e}")
            # 提供港股相關的默認數據
            indicators = {
                '恆生指數': {'value': '17,500 (+0.5%)', 'date': datetime.now().strftime('%Y-%m-%d')},
                '美元兌港元': {'value': '7.8200', 'date': datetime.now().strftime('%Y-%m-%d')},
                '上證指數': {'value': '3,100 (-0.2%)', 'date': datetime.now().strftime('%Y-%m-%d')},
                '港股通資金': {'value': '淨流入 15億', 'date': datetime.now().strftime('%Y-%m-%d')}
            }
        
        # 緩存數據
        cache_manager.set('economic_indicators', 'hk_market', indicators)
        print("💾 Cached economic indicators data")
        return indicators
    
    def get_market_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """獲取市場新聞（使用免費新聞源）"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            news_data = []
            for item in news[:limit]:
                news_data.append({
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'url': item.get('link', ''),
                    'published': item.get('providerPublishTime', 0),
                    'source': item.get('publisher', '')
                })
            
            return news_data
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return []
    
    def get_sector_performance(self) -> Dict:
        """獲取港股行業表現數據"""
        # 檢查緩存
        cached_data = cache_manager.get('sector_performance', 'hk_sectors')
        if cached_data:
            print("📦 Using cached sector performance data")
            return cached_data
        
        try:
            # 港股主要行業代表股票
            hk_sectors = {
                '科技股': ['0700.HK', '9988.HK', '1024.HK'],  # 騰訊、阿里、快手
                '金融股': ['0005.HK', '1398.HK', '3988.HK'],  # 匯豐、工商銀行、中銀
                '地產股': ['1109.HK', '0016.HK', '1997.HK'],  # 華潤置地、新鴻基、九龍倉置業
                '能源股': ['0857.HK', '0883.HK', '2628.HK'],  # 中石油、中海油、中國人壽
                '消費股': ['1299.HK', '0288.HK', '6862.HK'],  # 友邦、萬洲國際、海底撈
                '醫藥股': ['1177.HK', '6160.HK', '2269.HK'],  # 中生製藥、百濟神州、藥明生物
                '汽車股': ['2238.HK', '1211.HK', '0175.HK'],  # 廣汽集團、比亞迪、吉利汽車
                '電信股': ['0941.HK', '0728.HK', '0762.HK']   # 中移動、中電信、中聯通
            }
            
            sector_data = {}
            for sector, stocks in hk_sectors.items():
                try:
                    # 計算該行業的平均表現
                    sector_changes = []
                    for stock in stocks:
                        try:
                            ticker = yf.Ticker(stock)
                            hist = ticker.history(period="5d")
                            if not hist.empty:
                                current_price = hist['Close'][-1]
                                prev_price = hist['Close'][0]
                                change_pct = ((current_price - prev_price) / prev_price) * 100
                                sector_changes.append(change_pct)
                        except:
                            continue
                    
                    if sector_changes:
                        avg_change = sum(sector_changes) / len(sector_changes)
                        sector_data[sector] = {
                            'symbol': f"{len(sector_changes)}隻股票",
                            'current_price': 0,
                            'change_percent': float(avg_change)
                        }
                except Exception as e:
                    print(f"Error fetching data for {sector}: {e}")
            
            # 如果無法獲取數據，提供港股行業模擬數據
            if not sector_data:
                sector_data = {
                    '科技股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': -1.2},
                    '金融股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': 0.8},
                    '地產股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': -0.5},
                    '能源股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': 1.5},
                    '消費股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': 0.3},
                    '醫藥股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': -0.8},
                    '汽車股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': 2.1},
                    '電信股': {'symbol': '3隻股票', 'current_price': 0, 'change_percent': 0.1}
                }
            
            # 緩存數據
            cache_manager.set('sector_performance', 'hk_sectors', sector_data)
            print("💾 Cached sector performance data")
            return sector_data
        except Exception as e:
            print(f"Error fetching sector performance: {e}")
            return {}
    
    def collect_all_data(self, symbol: str) -> Dict:
        """收集指定股票的所有數據"""
        print(f"Collecting data for {symbol}...")
        
        data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'stock_info': self.get_stock_info(symbol),
            'price_data': self.get_stock_prices(symbol),
            'financial_data': self.get_financial_statements(symbol),
            'news': self.get_market_news(symbol),
            'economic_indicators': self.get_economic_indicators(),
            'sector_performance': self.get_sector_performance()
        }
        
        return data

# 使用示例
if __name__ == "__main__":
    collector = DataCollector()
    
    # 測試數據收集
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_symbols:
        data = collector.collect_all_data(symbol)
        print(f"Collected data for {symbol}: {len(data['price_data'])} price points")