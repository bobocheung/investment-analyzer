import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import time
import random
from dotenv import load_dotenv
from cache_manager import cache_manager, cached

load_dotenv()

class MultiSourceDataCollector:
    """多源數據收集器，支持多個API源和智能負載均衡"""
    
    def __init__(self):
        # API配置
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', 'demo')
        self.polygon_key = os.getenv('POLYGON_API_KEY', 'demo')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY', 'demo')
        self.marketstack_key = os.getenv('MARKETSTACK_API_KEY', 'demo')
        self.iex_cloud_key = os.getenv('IEX_CLOUD_API_KEY', 'demo')
        self.quandl_key = os.getenv('QUANDL_API_KEY', 'demo')
        
        # 請求限制配置
        self.request_delay = 0.3  # 基礎請求間隔（減少以提高速度）
        self.max_retries = 3      # 每個源的最大重試次數（增加以提高成功率）
        self.max_concurrent = 5   # 最大並發請求數（增加以提高效率）
        self.retry_delay = 1.0    # 重試間隔
        
        # API源配置
        self.data_sources = [
            {
                'name': 'yahoo_finance',
                'priority': 1,
                'enabled': True,
                'rate_limit': 100,  # 每分鐘請求數
                'last_request': 0,
                'success_rate': 0.9,
                'fallback': False
            },
            {
                'name': 'alpha_vantage',
                'priority': 2,
                'enabled': True,
                'rate_limit': 5,   # 免費版限制
                'last_request': 0,
                'success_rate': 0.8,
                'fallback': True
            },
            {
                'name': 'finnhub',
                'priority': 3,
                'enabled': True,
                'rate_limit': 60,  # 免費版限制
                'last_request': 0,
                'success_rate': 0.7,
                'fallback': True
            },
            {
                'name': 'twelve_data',
                'priority': 4,
                'enabled': True,
                'rate_limit': 8,   # 免費版限制
                'last_request': 0,
                'success_rate': 0.6,
                'fallback': True
            },
            {
                'name': 'marketstack',
                'priority': 5,
                'enabled': True,
                'rate_limit': 5,   # 免費版限制
                'last_request': 0,
                'success_rate': 0.5,
                'fallback': True
            },
            {
                'name': 'iex_cloud',
                'priority': 6,
                'enabled': True,
                'rate_limit': 10,  # 免費版限制
                'last_request': 0,
                'success_rate': 0.4,
                'fallback': True
            },
            {
                'name': 'quandl',
                'priority': 7,
                'enabled': True,
                'rate_limit': 50,  # 免費版限制
                'last_request': 0,
                'success_rate': 0.3,
                'fallback': True
            }
        ]
        
        # 統計信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'source_usage': {}
        }
        
        print("🚀 MultiSourceDataCollector initialized")
    
    def _can_make_request(self, source_name: str) -> bool:
        """檢查是否可以發送請求（基於速率限制）"""
        source = next((s for s in self.data_sources if s['name'] == source_name), None)
        if not source or not source['enabled']:
            return False
        
        current_time = time.time()
        time_since_last = current_time - source['last_request']
        min_interval = 60.0 / source['rate_limit']  # 最小間隔
        
        return time_since_last >= min_interval
    
    def _update_source_stats(self, source_name: str, success: bool):
        """更新源統計信息"""
        source = next((s for s in self.data_sources if s['name'] == source_name), None)
        if source:
            source['last_request'] = time.time()
            if success:
                source['success_rate'] = min(1.0, source['success_rate'] + 0.01)
            else:
                source['success_rate'] = max(0.0, source['success_rate'] - 0.05)
        
        self.stats['total_requests'] += 1
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        self.stats['source_usage'][source_name] = self.stats['source_usage'].get(source_name, 0) + 1
    
    def _fetch_from_yahoo_finance(self, symbol: str) -> Tuple[bool, Dict]:
        """從Yahoo Finance獲取數據（帶重試機制）"""
        for retry in range(self.max_retries):
            try:
                if not self._can_make_request('yahoo_finance'):
                    if retry < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False, {}
                
                print(f"🔍 Fetching from Yahoo Finance: {symbol} (attempt {retry + 1})")
                
                # 嘗試不同的符號格式
                symbol_variants = [
                    symbol,  # 原始符號
                    symbol.replace('.HK', ''),  # 移除.HK
                    symbol.replace('.HK', '.HK'),  # 確保.HK格式
                    symbol.replace('.HK', '.SI') if '.HK' in symbol else symbol,  # 嘗試新加坡格式
                    symbol.replace('.HK', '.TO') if '.HK' in symbol else symbol,  # 嘗試多倫多格式
                    symbol.replace('.HK', '.L') if '.HK' in symbol else symbol,   # 嘗試倫敦格式
                    symbol.replace('.HK', '.AX') if '.HK' in symbol else symbol,  # 嘗試澳洲格式
                    symbol.replace('.HK', '.PA') if '.HK' in symbol else symbol   # 嘗試巴黎格式
                ]
                
                for variant in symbol_variants:
                    try:
                        ticker = yf.Ticker(variant)
                        
                        # 嘗試獲取基本信息
                        info = ticker.info
                        
                        # 檢查是否有有效數據
                        if info and len(info) > 1:
                            # 驗證關鍵字段
                            has_price = any([
                                info.get('currentPrice'),
                                info.get('regularMarketPrice'),
                                info.get('previousClose'),
                                info.get('close'),
                                info.get('lastPrice')
                            ])
                            
                            has_name = any([
                                info.get('longName'),
                                info.get('shortName'),
                                info.get('symbol'),
                                info.get('name')
                            ])
                            
                            # 如果沒有價格數據，嘗試從歷史數據獲取
                            if not has_price:
                                try:
                                    hist = ticker.history(period="1d")
                                    if not hist.empty:
                                        latest = hist.iloc[-1]
                                        info['currentPrice'] = float(latest['Close'])
                                        info['regularMarketPrice'] = float(latest['Close'])
                                        info['previousClose'] = float(latest['Open'])
                                        has_price = True
                                        print(f"📊 Got price from history: ${info['currentPrice']}")
                                except Exception as e:
                                    print(f"Failed to get history: {e}")
                            
                            if has_price or has_name:
                                print(f"✅ Yahoo Finance success for {variant}")
                                self._update_source_stats('yahoo_finance', True)
                                return True, info
                        
                        # 如果info為空，嘗試獲取歷史數據
                        if not info or len(info) <= 1:
                            hist = ticker.history(period="1d")
                            if not hist.empty:
                                # 從歷史數據構建基本信息
                                latest = hist.iloc[-1]
                                basic_info = {
                                    'symbol': symbol,
                                    'currentPrice': float(latest['Close']),
                                    'regularMarketPrice': float(latest['Close']),
                                    'previousClose': float(latest['Open']),
                                    'longName': symbol,
                                    'shortName': symbol,
                                    'volume': int(latest['Volume']),
                                    'marketCap': 0,
                                    'sector': '未分類',
                                    'industry': '未分類'
                                }
                                print(f"✅ Yahoo Finance success (from history) for {variant}")
                                self._update_source_stats('yahoo_finance', True)
                                return True, basic_info
                                
                    except Exception as e:
                        print(f"Yahoo Finance variant {variant} failed: {e}")
                        continue
                
                # 如果所有變體都失敗，等待後重試
                if retry < self.max_retries - 1:
                    print(f"Retrying Yahoo Finance in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
                    
            except Exception as e:
                print(f"Yahoo Finance error for {symbol}: {e}")
                if retry < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
        
        print(f"❌ All Yahoo Finance attempts failed for {symbol}")
        self._update_source_stats('yahoo_finance', False)
        return False, {}
    
    def _fetch_from_alpha_vantage(self, symbol: str) -> Tuple[bool, Dict]:
        """從Alpha Vantage獲取數據"""
        try:
            if not self._can_make_request('alpha_vantage'):
                return False, {}
            
            # 移除.HK後綴
            clean_symbol = symbol.replace('.HK', '')
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': clean_symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'Symbol' in data:
                    # 轉換為統一格式
                    converted_data = self._convert_alpha_vantage_data(data)
                    self._update_source_stats('alpha_vantage', True)
                    return True, converted_data
            
            self._update_source_stats('alpha_vantage', False)
            return False, {}
            
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            self._update_source_stats('alpha_vantage', False)
            return False, {}
    
    def _fetch_from_finnhub(self, symbol: str) -> Tuple[bool, Dict]:
        """從Finnhub獲取數據"""
        try:
            if not self._can_make_request('finnhub'):
                return False, {}
            
            # 移除.HK後綴
            clean_symbol = symbol.replace('.HK', '')
            
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': clean_symbol,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'c' in data:  # current price
                    # 轉換為統一格式
                    converted_data = self._convert_finnhub_data(data, clean_symbol)
                    self._update_source_stats('finnhub', True)
                    return True, converted_data
            
            self._update_source_stats('finnhub', False)
            return False, {}
            
        except Exception as e:
            print(f"Finnhub error for {symbol}: {e}")
            self._update_source_stats('finnhub', False)
            return False, {}
    
    def _fetch_from_twelve_data(self, symbol: str) -> Tuple[bool, Dict]:
        """從Twelve Data獲取數據"""
        try:
            if not self._can_make_request('twelve_data'):
                return False, {}
            
            # 移除.HK後綴
            clean_symbol = symbol.replace('.HK', '')
            
            url = "https://api.twelvedata.com/quote"
            params = {
                'symbol': clean_symbol,
                'apikey': self.twelve_data_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'symbol' in data:
                    # 轉換為統一格式
                    converted_data = self._convert_twelve_data_data(data)
                    self._update_source_stats('twelve_data', True)
                    return True, converted_data
            
            self._update_source_stats('twelve_data', False)
            return False, {}
            
        except Exception as e:
            print(f"Twelve Data error for {symbol}: {e}")
            self._update_source_stats('twelve_data', False)
            return False, {}
    
    def _fetch_from_marketstack(self, symbol: str) -> Tuple[bool, Dict]:
        """從MarketStack獲取數據"""
        try:
            if not self._can_make_request('marketstack'):
                return False, {}
            
            # 移除.HK後綴
            clean_symbol = symbol.replace('.HK', '')
            
            url = "http://api.marketstack.com/v1/intraday/latest"
            params = {
                'access_key': self.marketstack_key,
                'symbols': clean_symbol
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data and len(data['data']) > 0:
                    # 轉換為統一格式
                    converted_data = self._convert_marketstack_data(data['data'][0])
                    self._update_source_stats('marketstack', True)
                    return True, converted_data
            
            self._update_source_stats('marketstack', False)
            return False, {}
            
        except Exception as e:
            print(f"MarketStack error for {symbol}: {e}")
            self._update_source_stats('marketstack', False)
            return False, {}
    
    def _fetch_from_iex_cloud(self, symbol: str) -> Tuple[bool, Dict]:
        """從IEX Cloud獲取數據"""
        try:
            if not self._can_make_request('iex_cloud'):
                return False, {}
            
            # 移除.HK後綴
            clean_symbol = symbol.replace('.HK', '')
            
            url = f"https://cloud.iexapis.com/stable/stock/{clean_symbol}/quote"
            params = {
                'token': self.iex_cloud_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'symbol' in data:
                    # 轉換為統一格式
                    converted_data = self._convert_iex_cloud_data(data)
                    self._update_source_stats('iex_cloud', True)
                    return True, converted_data
            
            self._update_source_stats('iex_cloud', False)
            return False, {}
            
        except Exception as e:
            print(f"IEX Cloud error for {symbol}: {e}")
            self._update_source_stats('iex_cloud', False)
            return False, {}
    
    def _fetch_from_quandl(self, symbol: str) -> Tuple[bool, Dict]:
        """從Quandl獲取數據"""
        try:
            if not self._can_make_request('quandl'):
                return False, {}
            
            # 移除.HK後綴
            clean_symbol = symbol.replace('.HK', '')
            
            url = f"https://www.quandl.com/api/v3/datasets/WIKI/{clean_symbol}/data.json"
            params = {
                'api_key': self.quandl_key,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'dataset_data' in data and 'data' in data['dataset_data']:
                    # 轉換為統一格式
                    converted_data = self._convert_quandl_data(data['dataset_data']['data'][0], clean_symbol)
                    self._update_source_stats('quandl', True)
                    return True, converted_data
            
            self._update_source_stats('quandl', False)
            return False, {}
            
        except Exception as e:
            print(f"Quandl error for {symbol}: {e}")
            self._update_source_stats('quandl', False)
            return False, {}
    
    def _convert_alpha_vantage_data(self, data: Dict) -> Dict:
        """轉換Alpha Vantage數據為統一格式"""
        return {
            'symbol': data.get('Symbol', ''),
            'name': data.get('Name', ''),
            'sector': data.get('Sector', '未分類'),
            'industry': data.get('Industry', '未分類'),
            'market_cap': float(data.get('MarketCapitalization', 0)) if data.get('MarketCapitalization') else 0,
            'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') else None,
            'price_to_book': float(data.get('PriceToBookRatio', 0)) if data.get('PriceToBookRatio') else None,
            'debt_to_equity': float(data.get('DebtToEquityRatio', 0)) if data.get('DebtToEquityRatio') else None,
            'roe': float(data.get('ReturnOnEquityTTM', 0)) if data.get('ReturnOnEquityTTM') else None,
            'profit_margin': float(data.get('ProfitMargin', 0)) if data.get('ProfitMargin') else None,
            'current_price': float(data.get('LatestPrice', 0)) if data.get('LatestPrice') else 0,
            'data_source': 'alpha_vantage'
        }
    
    def _convert_finnhub_data(self, data: Dict, symbol: str) -> Dict:
        """轉換Finnhub數據為統一格式"""
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': '未分類',
            'industry': '未分類',
            'market_cap': 0,
            'pe_ratio': None,
            'price_to_book': None,
            'debt_to_equity': None,
            'roe': None,
            'profit_margin': None,
            'current_price': float(data.get('c', 0)) if data.get('c') else 0,
            'data_source': 'finnhub'
        }
    
    def _convert_twelve_data_data(self, data: Dict) -> Dict:
        """轉換Twelve Data數據為統一格式"""
        return {
            'symbol': data.get('symbol', ''),
            'name': data.get('name', ''),
            'sector': '未分類',
            'industry': '未分類',
            'market_cap': 0,
            'pe_ratio': None,
            'price_to_book': None,
            'debt_to_equity': None,
            'roe': None,
            'profit_margin': None,
            'current_price': float(data.get('close', 0)) if data.get('close') else 0,
            'data_source': 'twelve_data'
        }
    
    def _convert_marketstack_data(self, data: Dict) -> Dict:
        """轉換MarketStack數據為統一格式"""
        return {
            'symbol': data.get('symbol', ''),
            'name': data.get('symbol', ''),
            'sector': '未分類',
            'industry': '未分類',
            'market_cap': 0,
            'pe_ratio': None,
            'price_to_book': None,
            'debt_to_equity': None,
            'roe': None,
            'profit_margin': None,
            'current_price': float(data.get('close', 0)) if data.get('close') else 0,
            'data_source': 'marketstack'
        }
    
    def _convert_iex_cloud_data(self, data: Dict) -> Dict:
        """轉換IEX Cloud數據為統一格式"""
        return {
            'symbol': data.get('symbol', ''),
            'name': data.get('companyName', ''),
            'sector': data.get('sector', '未分類'),
            'industry': '未分類',
            'market_cap': float(data.get('marketCap', 0)) if data.get('marketCap') else 0,
            'pe_ratio': float(data.get('peRatio', 0)) if data.get('peRatio') else None,
            'price_to_book': None,
            'debt_to_equity': None,
            'roe': None,
            'profit_margin': None,
            'current_price': float(data.get('latestPrice', 0)) if data.get('latestPrice') else 0,
            'data_source': 'iex_cloud'
        }
    
    def _convert_quandl_data(self, data: List, symbol: str) -> Dict:
        """轉換Quandl數據為統一格式"""
        # Quandl數據格式: [Date, Open, High, Low, Close, Volume, Ex-Dividend, Split Ratio, Adj. Open, Adj. High, Adj. Low, Adj. Close, Adj. Volume]
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': '未分類',
            'industry': '未分類',
            'market_cap': 0,
            'pe_ratio': None,
            'price_to_book': None,
            'debt_to_equity': None,
            'roe': None,
            'profit_margin': None,
            'current_price': float(data[4]) if len(data) > 4 else 0,  # Close price
            'data_source': 'quandl'
        }
    
    def _get_fallback_data(self, symbol: str) -> Dict:
        """獲取回退數據"""
        # 真實的港股公司數據（基於公開信息）
        company_data = {
            '0700.HK': {
                'name': '騰訊控股有限公司',
                'sector': '科技',
                'industry': '互聯網服務',
                'current_price': 320.0,
                'market_cap': 3000000000000,  # 3萬億港元
                'pe_ratio': 15.2,
                'price_to_book': 3.8,
                'roe': 0.25,
                'profit_margin': 0.35
            },
            '0005.HK': {
                'name': '匯豐控股有限公司',
                'sector': '金融',
                'industry': '銀行',
                'current_price': 65.0,
                'market_cap': 1200000000000,  # 1.2萬億港元
                'pe_ratio': 8.5,
                'price_to_book': 0.9,
                'roe': 0.12,
                'profit_margin': 0.28
            },
            '0941.HK': {
                'name': '中國移動有限公司',
                'sector': '電信',
                'industry': '電信服務',
                'current_price': 52.0,
                'market_cap': 1100000000000,  # 1.1萬億港元
                'pe_ratio': 12.3,
                'price_to_book': 1.2,
                'roe': 0.10,
                'profit_margin': 0.15
            },
            '1398.HK': {
                'name': '中國工商銀行股份有限公司',
                'sector': '金融',
                'industry': '銀行',
                'current_price': 4.2,
                'market_cap': 1500000000000,  # 1.5萬億港元
                'pe_ratio': 4.8,
                'price_to_book': 0.6,
                'roe': 0.12,
                'profit_margin': 0.35
            },
            '3988.HK': {
                'name': '中國銀行股份有限公司',
                'sector': '金融',
                'industry': '銀行',
                'current_price': 3.1,
                'market_cap': 900000000000,  # 9000億港元
                'pe_ratio': 4.2,
                'price_to_book': 0.5,
                'roe': 0.10,
                'profit_margin': 0.30
            },
            '0939.HK': {
                'name': '中國建設銀行股份有限公司',
                'sector': '金融',
                'industry': '銀行',
                'current_price': 5.8,
                'market_cap': 1400000000000,  # 1.4萬億港元
                'pe_ratio': 5.1,
                'price_to_book': 0.7,
                'roe': 0.13,
                'profit_margin': 0.32
            },
            '2318.HK': {
                'name': '中國平安保險(集團)股份有限公司',
                'sector': '金融',
                'industry': '保險',
                'current_price': 42.0,
                'market_cap': 800000000000,  # 8000億港元
                'pe_ratio': 6.8,
                'price_to_book': 0.8,
                'roe': 0.12,
                'profit_margin': 0.18
            },
            '1299.HK': {
                'name': '友邦保險集團有限公司',
                'sector': '金融',
                'industry': '保險',
                'current_price': 68.0,
                'market_cap': 800000000000,  # 8000億港元
                'pe_ratio': 18.5,
                'price_to_book': 2.1,
                'roe': 0.11,
                'profit_margin': 0.22
            },
            '0388.HK': {
                'name': '香港交易及結算所有限公司',
                'sector': '金融',
                'industry': '金融服務',
                'current_price': 280.0,
                'market_cap': 350000000000,  # 3500億港元
                'pe_ratio': 22.3,
                'price_to_book': 8.5,
                'roe': 0.38,
                'profit_margin': 0.65
            },
            '0007.HK': {
                'name': '智富資源投資控股集團有限公司',
                'sector': '金融',
                'industry': '投資控股',
                'current_price': 0.15,
                'market_cap': 200000000,  # 2億港元
                'pe_ratio': None,
                'price_to_book': 0.8,
                'roe': None,
                'profit_margin': None
            }
        }
        
        # 獲取公司數據，如果沒有則使用默認值
        company_info = company_data.get(symbol, {
            'name': symbol.replace('.HK', ''),
            'sector': '未分類',
            'industry': '未分類',
            'current_price': 10.0,
            'market_cap': 1000000000,  # 10億港元
            'pe_ratio': None,
            'price_to_book': None,
            'roe': None,
            'profit_margin': None
        })
        
        return {
            'symbol': symbol,
            'name': company_info['name'],
            'sector': company_info['sector'],
            'industry': company_info['industry'],
            'market_cap': company_info['market_cap'],
            'pe_ratio': company_info['pe_ratio'],
            'price_to_book': company_info['price_to_book'],
            'debt_to_equity': None,
            'roe': company_info['roe'],
            'profit_margin': company_info['profit_margin'],
            'current_price': company_info['current_price'],
            'data_source': 'fallback'
        }
    
    def get_stock_info_multi_source(self, symbol: str) -> Dict:
        """從多個源獲取股票信息"""
        # 檢查緩存
        cached_data = cache_manager.get('stock_info', symbol)
        if cached_data:
            print(f"📦 Using cached stock info for {symbol}")
            return cached_data
        
        print(f"🌐 Fetching stock info for {symbol} from multiple sources...")
        
        # 按優先級排序啟用的源
        enabled_sources = [s for s in self.data_sources if s['enabled']]
        enabled_sources.sort(key=lambda x: x['priority'])
        
        # 順序獲取數據（避免並發導致的速率限制問題）
        best_data = None
        best_source = None
        
        for source in enabled_sources:
            try:
                if source['name'] == 'yahoo_finance':
                    success, data = self._fetch_from_yahoo_finance(symbol)
                elif source['name'] == 'alpha_vantage':
                    success, data = self._fetch_from_alpha_vantage(symbol)
                elif source['name'] == 'finnhub':
                    success, data = self._fetch_from_finnhub(symbol)
                elif source['name'] == 'twelve_data':
                    success, data = self._fetch_from_twelve_data(symbol)
                elif source['name'] == 'marketstack':
                    success, data = self._fetch_from_marketstack(symbol)
                elif source['name'] == 'iex_cloud':
                    success, data = self._fetch_from_iex_cloud(symbol)
                elif source['name'] == 'quandl':
                    success, data = self._fetch_from_quandl(symbol)
                else:
                    continue
                
                if success and data:
                    best_data = data
                    best_source = source['name']
                    print(f"✅ Got data from {best_source}")
                    break
                    
            except Exception as e:
                print(f"Error from {source['name']}: {e}")
                continue
        
        # 如果所有源都失敗，使用回退數據
        if not best_data:
            print(f"❌ All sources failed for {symbol}, using fallback data")
            best_data = self._get_fallback_data(symbol)
            best_source = 'fallback'
        
        # 添加元數據
        best_data['last_updated'] = datetime.now().isoformat()
        best_data['data_source'] = best_source
        
        # 緩存數據
        cache_manager.set('stock_info', symbol, best_data)
        print(f"💾 Cached stock info for {symbol} from {best_source}")
        
        return best_data
    
    def get_stats(self) -> Dict:
        """獲取收集器統計信息"""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': self.stats['successful_requests'] / max(self.stats['total_requests'], 1),
            'source_usage': self.stats['source_usage'],
            'sources': [
                {
                    'name': s['name'],
                    'enabled': s['enabled'],
                    'priority': s['priority'],
                    'success_rate': s['success_rate'],
                    'rate_limit': s['rate_limit']
                }
                for s in self.data_sources
            ]
        }
    
    def enable_source(self, source_name: str, enabled: bool = True):
        """啟用或禁用數據源"""
        source = next((s for s in self.data_sources if s['name'] == source_name), None)
        if source:
            source['enabled'] = enabled
            print(f"{'✅ Enabled' if enabled else '❌ Disabled'} {source_name}")
    
    def set_source_priority(self, source_name: str, priority: int):
        """設置數據源優先級"""
        source = next((s for s in self.data_sources if s['name'] == source_name), None)
        if source:
            source['priority'] = priority
            print(f"Set {source_name} priority to {priority}")

# 創建全局實例
multi_source_collector = MultiSourceDataCollector()
