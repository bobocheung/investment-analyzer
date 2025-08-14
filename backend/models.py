import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "../data/database.db"):
        self.db_path = db_path
        # 確保目錄存在
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """初始化數據庫表結構"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 股票基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                sector TEXT,
                industry TEXT,
                market_cap REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 股價數據表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date DATE,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                adj_close REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol),
                UNIQUE(symbol, date)
            )
        ''')
        
        # 財務數據表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                period TEXT,
                revenue REAL,
                net_income REAL,
                total_assets REAL,
                total_debt REAL,
                shareholders_equity REAL,
                pe_ratio REAL,
                roe REAL,
                debt_to_equity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol),
                UNIQUE(symbol, period)
            )
        ''')
        
        # 技術指標表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date DATE,
                sma_20 REAL,
                sma_50 REAL,
                sma_200 REAL,
                rsi REAL,
                macd REAL,
                macd_signal REAL,
                bollinger_upper REAL,
                bollinger_lower REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol),
                UNIQUE(symbol, date)
            )
        ''')
        
        # 分析結果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                analysis_date DATE,
                fundamental_score REAL,
                technical_score REAL,
                overall_score REAL,
                recommendation TEXT,
                risk_level TEXT,
                target_price REAL,
                analysis_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks (symbol)
            )
        ''')
        
        # 宏觀經濟數據表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economic_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator TEXT,
                date DATE,
                value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(indicator, date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """獲取數據庫連接"""
        return sqlite3.connect(self.db_path)
    
    def insert_stock_data(self, symbol: str, data: Dict):
        """插入股票數據"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 插入股票基本信息
            cursor.execute('''
                INSERT OR REPLACE INTO stocks (symbol, name, sector, industry, market_cap, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, data.get('name'), data.get('sector'), 
                  data.get('industry'), data.get('market_cap'), datetime.now()))
            
            conn.commit()
        except Exception as e:
            print(f"Error inserting stock data: {e}")
        finally:
            conn.close()
    
    def insert_price_data(self, symbol: str, price_data: List[Dict]):
        """插入股價數據"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for data in price_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_prices 
                    (symbol, date, open, high, low, close, volume, adj_close)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, data['date'], data['open'], data['high'], 
                      data['low'], data['close'], data['volume'], data['adj_close']))
            
            conn.commit()
        except Exception as e:
            print(f"Error inserting price data: {e}")
        finally:
            conn.close()
    
    def get_stock_prices(self, symbol: str, limit: int = 100) -> List[Dict]:
        """獲取股價數據"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, open, high, low, close, volume, adj_close
            FROM stock_prices
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (symbol, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'date': row[0],
                'open': row[1],
                'high': row[2],
                'low': row[3],
                'close': row[4],
                'volume': row[5],
                'adj_close': row[6]
            }
            for row in results
        ]
    
    def insert_analysis_result(self, symbol: str, result: Dict):
        """插入分析結果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO analysis_results 
                (symbol, analysis_date, fundamental_score, technical_score, 
                 overall_score, recommendation, risk_level, target_price, analysis_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, datetime.now().date(), result.get('fundamental_score'),
                  result.get('technical_score'), result.get('overall_score'),
                  result.get('recommendation'), result.get('risk_level'),
                  result.get('target_price'), json.dumps(result.get('details', {}))))
            
            conn.commit()
        except Exception as e:
            print(f"Error inserting analysis result: {e}")
        finally:
            conn.close()
    
    def get_latest_analysis(self, symbol: str) -> Optional[Dict]:
        """獲取最新分析結果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fundamental_score, technical_score, overall_score, 
                   recommendation, risk_level, target_price, analysis_details
            FROM analysis_results
            WHERE symbol = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (symbol,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'fundamental_score': result[0],
                'technical_score': result[1],
                'overall_score': result[2],
                'recommendation': result[3],
                'risk_level': result[4],
                'target_price': result[5],
                'details': json.loads(result[6]) if result[6] else {}
            }
        return None