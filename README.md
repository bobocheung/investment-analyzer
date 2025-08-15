# 香港股票投資分析器 (Hong Kong Stock Investment Analyzer)

## 🚀 項目概述

香港股票投資分析器是一個專業的港股投資分析工具，提供全面的股票數據分析、技術指標計算、基本面分析和投資建議。該系統集成了高性能緩存系統，確保快速響應和優異的用戶體驗。

## ✨ 核心功能

### 📊 股票分析
- **基本信息分析**: 公司名稱、行業、市值、PE比率等
- **技術指標**: RSI、MACD、布林帶、移動平均線等
- **基本面分析**: 財務比率、盈利能力、風險評估
- **投資建議**: 綜合評分、風險等級、目標價格

### 🎯 市場數據
- **實時價格**: 股票價格、成交量、漲跌幅
- **市場指標**: 恆生指數、行業表現、經濟指標
- **新聞資訊**: 相關市場新聞和分析

### 📈 報告生成
- **HTML報告**: 美觀的投資分析報告
- **數據可視化**: 圖表和指標展示
- **投資建議**: 詳細的投資決策支持

### 🚀 高性能緩存系統
- **智能緩存策略**: 根據數據類型設置不同TTL
- **內存緩存**: 快速訪問，減少I/O操作
- **自動清理**: 定期清理過期緩存，釋放內存
- **線程安全**: 多線程環境下的數據一致性
- **統計監控**: 實時監控緩存命中率和性能指標

## 🏗️ 技術架構

### 後端技術棧
- **Flask**: Web框架
- **Python 3.9+**: 核心編程語言
- **yfinance**: Yahoo Finance數據API
- **pandas & numpy**: 數據處理和分析
- **自定義緩存系統**: 高性能緩存管理

### 前端技術棧
- **HTML5 & CSS3**: 響應式設計
- **JavaScript**: 動態交互
- **Chart.js**: 數據可視化

### 部署配置
- **Render.com**: 雲端部署
- **Python 3.9.16**: 運行環境
- **自動化部署**: CI/CD流程

## 📁 項目結構

```
investment-analyzer/
├── backend/                    # 後端核心代碼
│   ├── app.py                 # Flask應用主文件
│   ├── cache_manager.py       # 高性能緩存管理器
│   ├── data_collector.py      # 數據收集器
│   ├── analyzer.py            # 股票分析引擎
│   └── simple_report_generator.py  # 報告生成器
├── frontend/                   # 前端界面
│   ├── index.html             # 主頁面
│   ├── style.css              # 樣式文件
│   └── script.js              # 交互邏輯
├── templates/                  # 報告模板
│   └── report_template.html   # HTML報告模板
├── data/                      # 數據存儲
├── tests/                     # 測試文件
├── requirements.txt            # Python依賴
├── render.yaml                # Render部署配置
├── Procfile                   # 部署命令
└── README.md                  # 項目文檔
```

## 🚀 快速開始

### 環境要求
- Python 3.9+
- pip 包管理器

### 安裝步驟

1. **克隆項目**
```bash
git clone https://github.com/bobocheung/investment-analyzer.git
cd investment-analyzer
```

2. **安裝依賴**
```bash
pip install -r requirements.txt
```

3. **啟動應用**
```bash
python run.py
```

4. **訪問應用**
打開瀏覽器訪問 `http://localhost:8080`

### 部署到雲端

#### Render.com 部署
1. Fork 本項目到你的GitHub賬戶
2. 在Render.com創建新的Web Service
3. 連接GitHub倉庫
4. 設置環境變量（如需要）
5. 部署完成！

## 📊 緩存系統特性

### 緩存類型
| 類型 | TTL | 說明 |
|------|-----|------|
| `stock_info` | 1小時 | 股票基本信息 |
| `price_data` | 4小時 | 股票價格數據 |
| `financial_data` | 1天 | 財務數據 |
| `news` | 30分鐘 | 市場新聞 |
| `economic_indicators` | 12小時 | 經濟指標 |
| `sector_performance` | 12小時 | 行業表現 |
| `analysis_result` | 1小時 | 分析結果 |

### 緩存管理API
- `GET /api/cache/stats` - 緩存統計信息
- `GET /api/cache/info` - 緩存詳細信息
- `POST /api/cache/clear` - 清空緩存
- `POST /api/cache/invalidate/<symbol>` - 失效特定股票緩存
- `POST /api/cache/ttl` - 設置緩存TTL

## 🔧 配置選項

### 環境變量
```bash
FLASK_ENV=production          # 環境設置
PORT=8080                     # 端口設置
```

### 緩存配置
```python
# 設置特定緩存類型的TTL
cache_manager.set_ttl('stock_info', timedelta(hours=2))
cache_manager.set_ttl('price_data', timedelta(minutes=30))
```

## 📈 性能優化

### 緩存策略
- **智能TTL**: 根據數據類型設置不同的生存時間
- **自動清理**: 每5分鐘自動清理過期緩存
- **內存管理**: 優化的內存使用和垃圾回收

### 響應時間
- **首次請求**: 正常API響應時間
- **緩存命中**: 響應時間減少80%+
- **批量請求**: 支持並發處理

## 🧪 測試

### 運行測試
```bash
python test_cache_system.py    # 緩存系統測試
python test_system.py          # 系統功能測試
```

### 測試覆蓋
- ✅ 緩存系統功能測試
- ✅ 股票分析功能測試
- ✅ API端點測試
- ✅ 報告生成測試

## 📚 API文檔

### 核心API端點

#### 股票分析
- `GET /api/stock/<symbol>` - 獲取股票分析數據
- `GET /api/stock/<symbol>/report` - 生成分析報告

#### 市場數據
- `GET /api/market/sectors` - 獲取市場板塊數據
- `GET /api/market/economic` - 獲取經濟指標

#### 監控列表
- `GET /api/watchlist` - 獲取監控列表
- `POST /api/watchlist` - 添加到監控列表
- `DELETE /api/watchlist/<symbol>` - 從監控列表移除

## 🐛 故障排除

### 常見問題

#### 1. 緩存命中率低
- 檢查TTL設置是否合理
- 確認緩存鍵設計是否正確
- 檢查是否有頻繁的緩存清空操作

#### 2. 部署失敗
- 確認Python版本為3.9+
- 檢查依賴是否完整安裝
- 查看部署日誌中的具體錯誤

#### 3. 數據獲取失敗
- 檢查網絡連接
- 確認Yahoo Finance API可用性
- 查看錯誤日誌

### 調試技巧
```python
# 檢查緩存統計
stats = cache_manager.get_stats()
print(f"Cache hit rate: {stats['hit_rate']}")

# 檢查緩存內容
info = cache_manager.get_cache_info('stock_info')
print(f"Stock info cache: {info}")
```

## 🤝 貢獻指南

### 開發環境設置
1. Fork 項目
2. 創建功能分支
3. 提交更改
4. 發起Pull Request

### 代碼規範
- 遵循PEP 8 Python代碼規範
- 添加適當的註釋和文檔
- 編寫測試用例
- 確保代碼通過所有測試

## 📄 許可證

本項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- Yahoo Finance API 提供股票數據
- Flask 框架提供Web服務支持
- 開源社區的貢獻和支持

## 📞 聯繫方式

- **項目地址**: [GitHub](https://github.com/bobocheung/investment-analyzer)
- **問題反饋**: [Issues](https://github.com/bobocheung/investment-analyzer/issues)
- **功能建議**: [Discussions](https://github.com/bobocheung/investment-analyzer/discussions)

---

**最後更新**: 2025-01-XX  
**版本**: v2.0.0  
**狀態**: 🚀 生產就緒
