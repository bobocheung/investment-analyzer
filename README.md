# 🏮 港股投資分析系統 (Hong Kong Stock Investment Analyzer)

一個專為港股市場設計的智能投資分析系統，提供全面的股票分析、技術指標計算和投資建議生成功能。

## ✨ 主要功能

### 📊 股票分析
- **實時股價數據**：通過 Yahoo Finance API 獲取最新港股數據
- **基本面分析**：PE比率、PB比率、ROE、債務比率等關鍵指標
- **技術面分析**：移動平均線、RSI、MACD、布林帶等技術指標
- **市場情緒分析**：基於多項指標的綜合評分系統

### 📈 投資建議
- **智能評分**：基於基本面和技術面的綜合評分（0-100分）
- **投資建議**：買入/持有/賣出建議，附帶信心度評估
- **風險評級**：低/中/高風險等級分類
- **目標價格**：基於分析模型的目標價格預測

### 📋 投資組合管理
- **觀察清單**：添加/移除關注股票
- **批量分析**：一次性分析多隻股票
- **歷史追蹤**：股價走勢和分析結果歷史記錄

### 📄 報告生成
- **美觀的HTML報告**：包含完整分析結果的可視化報告
- **一鍵下載**：支持HTML格式報告下載
- **中文界面**：完全中文化的用戶界面

## 🚀 快速開始

### 環境要求
- Python 3.8+
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
cd backend
python app.py
```

4. **訪問應用**
打開瀏覽器訪問：http://localhost:8080

## 📁 項目結構

```
investment-analyzer/
├── backend/                    # 後端代碼
│   ├── app.py                 # Flask 主應用
│   ├── data_collector.py      # 數據收集模組
│   ├── analyzer.py            # 分析引擎
│   ├── models.py              # 數據模型
│   ├── simple_report_generator.py  # 報告生成器
│   └── report_generator.py    # 高級報告生成器
├── frontend/                   # 前端代碼
│   ├── index.html             # 主頁面
│   ├── script.js              # JavaScript 邏輯
│   └── style.css              # 樣式文件
├── data/                      # 數據存儲目錄
│   ├── reports/               # 生成的報告
│   └── watchlist.json         # 觀察清單
├── requirements.txt           # Python 依賴
└── README.md                  # 項目說明
```

## 🔧 API 接口

### 股票信息
- `GET /api/stocks/{symbol}/info` - 獲取股票基本信息
- `GET /api/stocks/{symbol}/prices` - 獲取股價歷史數據

### 分析功能
- `GET /api/analyze/{symbol}` - 分析指定股票
- `POST /api/batch-analyze` - 批量分析股票

### 報告生成
- `GET /api/reports/{symbol}` - 生成HTML報告
- `GET /api/reports/{symbol}/pdf` - 生成PDF報告（需要額外依賴）

### 觀察清單
- `GET /api/watchlist` - 獲取觀察清單
- `POST /api/watchlist/{symbol}` - 添加到觀察清單
- `DELETE /api/watchlist/{symbol}` - 從觀察清單移除

### 市場數據
- `GET /api/market/economic` - 獲取經濟指標
- `GET /api/market/sectors` - 獲取行業表現

## 📊 分析指標說明

### 基本面指標
- **PE比率**：市盈率，股價與每股收益的比值
- **PB比率**：市淨率，股價與每股淨資產的比值
- **ROE**：股東權益報酬率，衡量公司盈利能力
- **債務比率**：負債與股東權益的比值

### 技術面指標
- **移動平均線**：5日、20日、50日移動平均
- **RSI**：相對強弱指標，衡量超買超賣
- **MACD**：指數平滑移動平均線，趨勢指標
- **布林帶**：價格通道指標

### 評分系統
- **基本面評分**：基於財務指標的評分（0-100）
- **技術面評分**：基於技術指標的評分（0-100）
- **綜合評分**：基本面和技術面的加權平均

## 🎨 界面特色

- **響應式設計**：支持桌面和移動設備
- **中文界面**：完全中文化的用戶體驗
- **美觀報告**：採用現代化設計的分析報告
- **實時更新**：股價和分析數據實時刷新

## ⚙️ 配置選項

### 數據更新頻率
系統會自動定期更新股價數據，默認配置：
- 股價數據：每小時更新
- 分析結果：每日更新
- 市場指標：每日更新

### 可選依賴
如需PDF報告生成功能，請安裝額外依賴：
```bash
pip install weasyprint pdfkit
```

## 🔍 使用示例

### 分析單隻股票
1. 在搜索框輸入股票代碼（如：0700.HK）
2. 點擊"分析"按鈕
3. 查看詳細的分析結果
4. 可選擇生成報告或添加到觀察清單

### 批量分析
1. 點擊"批量分析"
2. 輸入多個股票代碼（用逗號分隔）
3. 系統會並行分析所有股票
4. 查看對比結果

### 生成報告
1. 完成股票分析後
2. 點擊"生成報告"按鈕
3. 系統會生成包含完整分析的HTML報告
4. 可直接在瀏覽器查看或下載

## 🛠️ 開發指南

### 添加新的分析指標
1. 在 `analyzer.py` 中添加計算邏輯
2. 更新 `simple_report_generator.py` 中的報告模板
3. 在前端 `script.js` 中添加顯示邏輯

### 自定義報告樣式
1. 修改 `simple_report_generator.py` 中的CSS樣式
2. 調整HTML模板結構
3. 測試不同瀏覽器的兼容性

## 📝 注意事項

### 數據來源
- 股價數據來自 Yahoo Finance
- 數據可能存在15-20分鐘延遲
- 建議僅用於參考，不構成投資建議

### 免責聲明
- 本系統僅供學習和研究使用
- 所有分析結果僅供參考，不構成投資建議
- 投資有風險，入市需謹慎
- 請根據個人風險承受能力做出投資決策

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本項目
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情

## 📞 聯繫方式

- 項目地址：https://github.com/bobocheung/investment-analyzer
- 問題反饋：https://github.com/bobocheung/investment-analyzer/issues

## 🙏 致謝

- [Yahoo Finance](https://finance.yahoo.com/) - 提供股價數據
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [pandas](https://pandas.pydata.org/) - 數據處理
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API

---

**⚠️ 投資風險提示**：本系統提供的所有信息和分析僅供參考，不構成投資建議。投資者應該根據自己的風險承受能力和投資目標做出決策。股市有風險，投資需謹慎。