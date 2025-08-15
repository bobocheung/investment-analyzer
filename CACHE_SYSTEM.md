# 緩存系統文檔

## 概述

香港股票投資分析器的緩存系統是一個高性能、智能化的數據緩存解決方案，旨在減少外部API調用、提升響應速度、優化系統性能。

## 核心特性

### 🚀 性能優化
- **智能緩存策略**: 根據數據類型設置不同的TTL（生存時間）
- **內存緩存**: 快速訪問，減少I/O操作
- **自動清理**: 定期清理過期緩存，釋放內存

### 🛡️ 可靠性保障
- **線程安全**: 使用鎖機制確保多線程環境下的數據一致性
- **錯誤處理**: 優雅的錯誤處理和回退機制
- **統計監控**: 實時監控緩存命中率和性能指標

### 🔧 靈活配置
- **可配置TTL**: 支持動態調整不同緩存類型的生存時間
- **緩存分類**: 支持多種數據類型的獨立緩存管理
- **手動控制**: 支持手動清空、失效特定緩存

## 緩存類型

| 緩存類型 | TTL | 說明 | 數據示例 |
|---------|-----|------|----------|
| `stock_info` | 1小時 | 股票基本信息 | 公司名稱、行業、市值等 |
| `price_data` | 4小時 | 股票價格數據 | 開盤價、收盤價、成交量等 |
| `financial_data` | 1天 | 財務數據 | 收入、利潤、資產等 |
| `news` | 30分鐘 | 市場新聞 | 新聞標題、摘要、來源等 |
| `economic_indicators` | 12小時 | 經濟指標 | 恆生指數、匯率等 |
| `sector_performance` | 12小時 | 行業表現 | 各行業漲跌幅等 |
| `analysis_result` | 1小時 | 分析結果 | 技術分析、基本面分析等 |

## API端點

### 緩存統計
```http
GET /api/cache/stats
```
獲取緩存系統的統計信息，包括命中率、緩存條目數量等。

**響應示例:**
```json
{
  "total_entries": 25,
  "cache_types": {
    "stock_info": 8,
    "price_data": 5,
    "analysis_result": 12
  },
  "hits": 45,
  "misses": 12,
  "sets": 25,
  "deletes": 3,
  "expirations": 2,
  "hit_rate": "78.9%"
}
```

### 緩存信息
```http
GET /api/cache/info?type=stock_info
```
獲取特定緩存類型的詳細信息。

**響應示例:**
```json
{
  "type": "stock_info",
  "entries": 8,
  "ttl": "1:00:00",
  "keys": ["0005.HK", "0700.HK", "9988.HK"]
}
```

### 清空緩存
```http
POST /api/cache/clear
Content-Type: application/json

{
  "type": "stock_info"  // 可選，不指定則清空所有緩存
}
```

### 失效特定股票緩存
```http
POST /api/cache/invalidate/0005.HK
```
失效指定股票的所有相關緩存。

### 設置TTL
```http
POST /api/cache/ttl
Content-Type: application/json

{
  "type": "stock_info",
  "hours": 2
}
```

## 使用方法

### 1. 基本緩存操作

```python
from cache_manager import cache_manager

# 設置緩存
cache_manager.set('stock_info', '0005.HK', stock_data)

# 獲取緩存
cached_data = cache_manager.get('stock_info', '0005.HK')

# 刪除緩存
cache_manager.delete('stock_info', '0005.HK')
```

### 2. 使用緩存裝飾器

```python
from cache_manager import cached
from datetime import timedelta

@cached('stock_info', ttl_override=timedelta(hours=2))
def get_stock_info(symbol):
    # 這個函數的結果會被自動緩存
    return fetch_stock_data(symbol)
```

### 3. 批量緩存管理

```python
# 清空特定類型緩存
cache_manager.clear_type('stock_info')

# 清空所有緩存
cache_manager.clear_all()

# 失效特定股票的所有相關緩存
cache_manager.invalidate_stock_data('0005.HK')
```

## 配置選項

### TTL配置
```python
# 設置特定緩存類型的TTL
cache_manager.set_ttl('stock_info', timedelta(hours=2))
cache_manager.set_ttl('price_data', timedelta(minutes=30))
```

### 自動清理配置
```python
# 在 CacheManager 初始化時設置
class CacheManager:
    def __init__(self):
        # 每5分鐘檢查一次過期緩存
        self.cleanup_interval = 300  # 秒
```

## 性能監控

### 緩存統計
- **命中率**: 緩存命中次數 / 總請求次數
- **緩存條目**: 當前緩存的數據條目數量
- **操作統計**: 設置、獲取、刪除、過期等操作的次數

### 性能指標
- **響應時間**: 有緩存 vs 無緩存的響應時間對比
- **內存使用**: 緩存佔用的內存空間
- **API調用節省**: 通過緩存減少的對外API調用次數

## 最佳實踐

### 1. TTL設置策略
- **高頻數據**: 設置較短的TTL（如價格數據30分鐘）
- **穩定數據**: 設置較長的TTL（如財務數據1天）
- **實時數據**: 設置最短TTL（如新聞15分鐘）

### 2. 緩存鍵設計
- 使用有意義的鍵名
- 避免過長的鍵名
- 考慮鍵的衝突可能性

### 3. 內存管理
- 定期監控緩存大小
- 設置合理的緩存條目限制
- 及時清理過期緩存

### 4. 錯誤處理
- 緩存失敗時不影響主要業務邏輯
- 提供合理的回退機制
- 記錄緩存相關的錯誤日誌

## 故障排除

### 常見問題

#### 1. 緩存命中率低
**可能原因:**
- TTL設置過短
- 緩存鍵設計不合理
- 緩存被頻繁清空

**解決方案:**
- 檢查TTL設置
- 優化緩存鍵設計
- 檢查是否有手動清空操作

#### 2. 內存使用過高
**可能原因:**
- 緩存條目過多
- TTL設置過長
- 自動清理未正常工作

**解決方案:**
- 檢查緩存條目數量
- 調整TTL設置
- 檢查自動清理線程

#### 3. 緩存數據過期
**可能原因:**
- TTL設置過短
- 系統時間不準確
- 緩存清理過於頻繁

**解決方案:**
- 調整TTL設置
- 檢查系統時間
- 調整清理頻率

### 調試技巧

#### 1. 啟用詳細日誌
```python
# 在緩存操作中添加日誌
print(f"💾 Cached data for {key}")
print(f"📦 Using cached data for {key}")
```

#### 2. 監控緩存統計
```python
# 定期檢查緩存統計
stats = cache_manager.get_stats()
print(f"Cache hit rate: {stats['hit_rate']}")
```

#### 3. 檢查緩存內容
```python
# 檢查特定緩存類型的內容
info = cache_manager.get_cache_info('stock_info')
print(f"Stock info cache: {info}")
```

## 擴展功能

### 1. 分佈式緩存
- 支持Redis等外部緩存服務
- 多實例間的緩存同步
- 緩存負載均衡

### 2. 持久化緩存
- 將緩存數據保存到磁盤
- 應用重啟後恢復緩存
- 緩存數據的備份和恢復

### 3. 智能緩存
- 基於使用模式的TTL調整
- 預熱常用數據
- 緩存優先級管理

## 更新日誌

### v1.0.0 (2025-01-XX)
- 初始版本發布
- 基本緩存功能
- 自動清理機制
- 統計監控功能

### 計劃功能
- 分佈式緩存支持
- 緩存預熱機制
- 智能TTL調整
- 緩存性能分析工具

## 技術支持

如有問題或建議，請：
1. 檢查本文檔的故障排除部分
2. 查看系統日誌
3. 運行緩存測試腳本
4. 聯繫開發團隊

---

*緩存系統文檔 v1.0.0*
*最後更新: 2025-01-XX*
