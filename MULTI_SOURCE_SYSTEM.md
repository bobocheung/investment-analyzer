# 🚀 多源數據收集系統

## 📋 **系統概述**

多源數據收集系統是一個智能的、負載均衡的股票數據收集解決方案，支持多個API源，確保數據的高可用性和系統的穩定性。

## 🔧 **核心特性**

### **智能負載均衡**
- **優先級排序**: 按數據源質量和成功率自動排序
- **速率限制**: 每個API源都有獨立的請求限制
- **自動降級**: 當主要源失敗時自動切換到備用源
- **並發控制**: 限制同時請求數量，避免系統超負荷

### **多數據源支持**
1. **Yahoo Finance** (主要源)
   - 免費，無API密鑰要求
   - 數據全面，更新及時
   - 速率限制：每分鐘100次請求

2. **Alpha Vantage** (備用源)
   - 免費版：每分鐘5次請求
   - 提供基本面數據
   - 需要API密鑰

3. **Finnhub** (備用源)
   - 免費版：每分鐘60次請求
   - 提供實時價格數據
   - 需要API密鑰

4. **回退數據** (最後保障)
   - 當所有API源都失敗時使用
   - 提供基本的公司信息
   - 生成模擬價格數據

## 🚀 **快速開始**

### **1. 安裝依賴**
```bash
pip install aiohttp asyncio
```

### **2. 配置API密鑰**
複製 `env.example` 為 `.env` 並填入你的API密鑰：
```bash
cp env.example .env
```

編輯 `.env` 文件：
```env
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
```

### **3. 使用多源收集器**
```python
from multi_source_collector import multi_source_collector

# 獲取股票信息
stock_data = await multi_source_collector.get_stock_info_multi_source('0700.HK')

# 查看統計信息
stats = multi_source_collector.get_stats()
print(f"成功率: {stats['success_rate']:.2%}")
```

## 📊 **API端點**

### **數據源管理**
- `GET /api/data/sources` - 獲取所有數據源統計信息
- `GET /api/data/sources/<source_name>/toggle?enabled=true` - 啟用/禁用數據源

### **緩存管理**
- `GET /api/cache/stats` - 獲取緩存統計
- `GET /api/cache/info` - 獲取緩存詳細信息
- `POST /api/cache/clear` - 清理緩存
- `DELETE /api/cache/invalidate/<symbol>` - 失效特定股票緩存

## ⚙️ **配置選項**

### **數據源配置**
```python
# 啟用/禁用數據源
multi_source_collector.enable_source('yahoo_finance', True)
multi_source_collector.enable_source('alpha_vantage', False)

# 設置優先級
multi_source_collector.set_source_priority('yahoo_finance', 1)
multi_source_collector.set_source_priority('alpha_vantage', 2)
```

### **速率限制配置**
```python
# 修改請求間隔
collector.request_delay = 0.5  # 秒

# 修改最大重試次數
collector.max_retries = 2
```

## 📈 **性能優化**

### **緩存策略**
- **股票信息**: 1小時TTL
- **價格數據**: 4小時TTL
- **分析結果**: 1小時TTL
- **回退數據**: 30分鐘TTL

### **請求優化**
- **並發請求**: 最多3個同時進行
- **智能重試**: 失敗後自動重試，指數退避
- **負載分散**: 自動分散請求到不同時間

## 🔍 **監控和調試**

### **統計信息**
```python
stats = multi_source_collector.get_stats()
print(f"總請求數: {stats['total_requests']}")
print(f"成功率: {stats['success_rate']:.2%}")
print(f"各源使用情況: {stats['source_usage']}")
```

### **日誌輸出**
系統會輸出詳細的日誌信息：
```
🚀 MultiSourceDataCollector initialized
🌐 Fetching stock info for 0700.HK from multiple sources...
✅ Got data from yahoo_finance
💾 Cached stock info for 0700.HK from yahoo_finance
```

## 🚨 **故障排除**

### **常見問題**

#### **1. API密鑰錯誤**
```
Error: Invalid API key
```
**解決方案**: 檢查 `.env` 文件中的API密鑰是否正確

#### **2. 速率限制**
```
Error: Rate limit exceeded
```
**解決方案**: 增加請求間隔或升級API計劃

#### **3. 網絡超時**
```
Error: Connection timeout
```
**解決方案**: 檢查網絡連接，增加超時時間

### **降級策略**
當遇到問題時，系統會自動：
1. 嘗試其他可用的數據源
2. 使用緩存的數據
3. 生成回退數據
4. 記錄錯誤信息

## 🔮 **未來擴展**

### **計劃中的功能**
- **更多數據源**: 添加Bloomberg、Reuters等
- **數據質量評分**: 自動評估數據準確性
- **智能路由**: 根據數據類型選擇最佳源
- **實時監控**: WebSocket實時數據推送

### **自定義擴展**
```python
class CustomDataSource:
    def __init__(self):
        self.name = 'custom_source'
        self.priority = 4
    
    async def fetch_data(self, symbol):
        # 實現你的數據獲取邏輯
        pass

# 註冊自定義源
multi_source_collector.data_sources.append(CustomDataSource())
```

## 📞 **支持**

如果你遇到問題或需要幫助：
1. 檢查日誌輸出
2. 查看緩存統計
3. 測試各個數據源
4. 聯繫開發團隊

---

**注意**: 請遵守各API服務商的使用條款和速率限制。
