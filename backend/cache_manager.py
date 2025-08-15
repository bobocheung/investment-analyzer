"""
智能緩存管理系統
支持多層緩存、自動失效、性能監控
"""
import time
from datetime import datetime, timedelta
import json
import threading
import gc

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.ttl = {
            'stock_info': timedelta(hours=1),
            'price_data': timedelta(hours=4),
            'financial_data': timedelta(days=1),
            'news': timedelta(minutes=30),
            'economic_indicators': timedelta(hours=12),
            'sector_performance': timedelta(hours=12),
            'analysis_result': timedelta(hours=1)
        }
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'expirations': 0
        }
        self.lock = threading.Lock()
        
        # 啟動自動清理線程
        self.cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self.cleanup_thread.start()
        
        print("📦 CacheManager initialized with auto-cleanup.")

    def get(self, cache_type: str, key: str):
        """獲取緩存數據"""
        with self.lock:
            if cache_type not in self.cache:
                self.stats['misses'] += 1
                return None
            
            if key in self.cache[cache_type]:
                data, timestamp = self.cache[cache_type][key]
                if datetime.now() - timestamp < self.ttl.get(cache_type, timedelta(minutes=5)):
                    self.stats['hits'] += 1
                    return data
                else:
                    # 緩存過期，自動清理
                    self.delete(cache_type, key)
                    self.stats['expirations'] += 1
            
            self.stats['misses'] += 1
            return None

    def set(self, cache_type: str, key: str, data):
        """設置緩存數據"""
        with self.lock:
            if cache_type not in self.cache:
                self.cache[cache_type] = {}
            self.cache[cache_type][key] = (data, datetime.now())
            self.stats['sets'] += 1

    def delete(self, cache_type: str, key: str):
        """刪除特定緩存"""
        with self.lock:
            if cache_type in self.cache and key in self.cache[cache_type]:
                del self.cache[cache_type][key]
                self.stats['deletes'] += 1

    def clear_type(self, cache_type: str):
        """清空特定類型的緩存"""
        with self.lock:
            if cache_type in self.cache:
                deleted_count = len(self.cache[cache_type])
                self.cache[cache_type] = {}
                self.stats['deletes'] += deleted_count
                print(f"🗑️ Cleared {deleted_count} {cache_type} cache entries")

    def clear_all(self):
        """清空所有緩存"""
        with self.lock:
            total_entries = sum(len(cache) for cache in self.cache.values())
            self.cache = {}
            self.stats['deletes'] += total_entries
            print(f"🗑️ All caches cleared ({total_entries} entries)")

    def invalidate_stock_data(self, symbol: str):
        """失效特定股票的所有相關緩存"""
        with self.lock:
            cache_types = ['stock_info', 'price_data', 'financial_data', 'news', 'analysis_result']
            deleted_count = 0
            
            for cache_type in cache_types:
                if cache_type in self.cache and symbol in self.cache[cache_type]:
                    del self.cache[cache_type][symbol]
                    deleted_count += 1
            
            if deleted_count > 0:
                self.stats['deletes'] += deleted_count
                print(f"🗑️ Invalidated {deleted_count} cache entries for {symbol}")

    def get_stats(self):
        """獲取緩存統計信息"""
        with self.lock:
            total_entries = sum(len(cache) for cache in self.cache.values())
            hit_rate = (self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])) * 100 if (self.stats['hits'] + self.stats['misses']) > 0 else 0
            
            return {
                'total_entries': total_entries,
                'cache_types': {k: len(v) for k, v in self.cache.items()},
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'expirations': self.stats['expirations'],
                'hit_rate': f"{hit_rate:.1f}%"
            }

    def _auto_cleanup(self):
        """自動清理過期緩存"""
        while True:
            try:
                time.sleep(300)  # 每5分鐘檢查一次
                self._cleanup_expired()
            except Exception as e:
                print(f"Auto-cleanup error: {e}")

    def _cleanup_expired(self):
        """清理過期緩存"""
        with self.lock:
            current_time = datetime.now()
            expired_count = 0
            
            for cache_type, cache_data in self.cache.items():
                expired_keys = []
                for key, (data, timestamp) in cache_data.items():
                    if current_time - timestamp > self.ttl.get(cache_type, timedelta(minutes=5)):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del cache_data[key]
                    expired_count += 1
            
            if expired_count > 0:
                self.stats['expirations'] += expired_count
                print(f"🧹 Auto-cleanup: removed {expired_count} expired entries")

    def set_ttl(self, cache_type: str, ttl: timedelta):
        """設置特定緩存類型的TTL"""
        self.ttl[cache_type] = ttl
        print(f"⏰ Set TTL for {cache_type}: {ttl}")

    def get_cache_info(self, cache_type: str = None):
        """獲取緩存信息"""
        with self.lock:
            if cache_type:
                if cache_type in self.cache:
                    return {
                        'type': cache_type,
                        'entries': len(self.cache[cache_type]),
                        'ttl': str(self.ttl.get(cache_type, 'default')),
                        'keys': list(self.cache[cache_type].keys())
                    }
                return None
            
            return {
                'types': {k: len(v) for k, v in self.cache.items()},
                'ttl_settings': {k: str(v) for k, v in self.ttl.items()}
            }

# 全局實例
cache_manager = CacheManager()

def cached(cache_type: str, ttl_override: timedelta = None):
    """緩存裝飾器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成緩存鍵
            cache_key_parts = [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
            cache_key = "_".join(cache_key_parts)
            
            # 檢查緩存
            cached_data = cache_manager.get(cache_type, cache_key)
            if cached_data:
                print(f"📦 Using cached data for {func.__name__} ({cache_type}, {cache_key})")
                return cached_data
            
            # 執行函數
            result = func(*args, **kwargs)
            
            # 設置TTL覆蓋
            if ttl_override:
                cache_manager.set_ttl(cache_type, ttl_override)
            
            # 緩存結果
            cache_manager.set(cache_type, cache_key, result)
            print(f"💾 Cached fresh data for {func.__name__} ({cache_type}, {cache_key})")
            return result
        return wrapper
    return decorator