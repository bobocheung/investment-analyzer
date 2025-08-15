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
        
        # 請求限制配置
        self.request_delay = 0.5  # 基礎請求間隔
        self.max_retries = 2      # 每個源的最大重試次數
        self.max_concurrent = 3   # 最大並發請求數
        
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
        """從Yahoo Finance獲取數據"""
        try:
            if not self._can_make_request('yahoo_finance'):
                return False, {}
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info and len(info) > 1:
                self._update_source_stats('yahoo_finance', True)
                return True, info
            else:
                self._update_source_stats('yahoo_finance', False)
                return False, {}
                
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
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
    
    def _get_fallback_data(self, symbol: str) -> Dict:
        """獲取回退數據"""
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
            'sector': '未分類',
            'industry': '未分類',
            'market_cap': 0,
            'pe_ratio': None,
            'price_to_book': None,
            'debt_to_equity': None,
            'roe': None,
            'profit_margin': None,
            'current_price': 0,
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
