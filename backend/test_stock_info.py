#!/usr/bin/env python3
import yfinance as yf

def test_stock_info():
    """測試股票信息獲取"""
    symbol = "0700.HK"
    print(f"Testing stock info for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        print(f"Symbol: {symbol}")
        print(f"Name: {info.get('longName', 'N/A')}")
        print(f"Sector: {info.get('sector', 'N/A')}")
        print(f"Industry: {info.get('industry', 'N/A')}")
        print(f"Market Cap: {info.get('marketCap', 'N/A')}")
        print(f"PE Ratio: {info.get('trailingPE', 'N/A')}")
        print(f"Current Price: {info.get('currentPrice', 'N/A')}")
        
        # 檢查是否有基本信息
        if info.get('longName'):
            print("✅ Stock info retrieved successfully")
        else:
            print("❌ No stock info found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_stock_info()