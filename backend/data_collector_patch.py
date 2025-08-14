# 臨時修復文件 - 減少API調用
import time
import random

def patch_data_collector():
    """修復DataCollector的API調用問題"""
    
    # 添加請求延遲
    original_yfinance_ticker = None
    
    def safe_ticker_request(symbol, max_retries=2):
        """安全的ticker請求"""
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(2 + random.uniform(0.5, 1.5))
                
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                
                # 測試是否能獲取基本信息
                info = ticker.info
                if info and len(info) > 1:
                    return ticker
                    
            except Exception as e:
                print(f"Ticker request failed for {symbol} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    return safe_ticker_request

# 使用示例
safe_request = patch_data_collector()