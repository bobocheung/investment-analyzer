# 🔑 API密鑰獲取指南

## 📋 **概述**

為了提高數據獲取成功率，本系統支持多個免費的股票數據API。以下是獲取免費API密鑰的詳細指南。

## 🆓 **免費API密鑰獲取**

### **1. Alpha Vantage**
- **網站**: https://www.alphavantage.co/support/#api-key
- **免費額度**: 每分鐘5次請求，每天500次請求
- **獲取步驟**:
  1. 訪問網站並點擊 "Get Your Free API Key Today"
  2. 填寫基本信息（姓名、郵箱）
  3. 選擇免費計劃
  4. 立即獲得API密鑰

### **2. Finnhub**
- **網站**: https://finnhub.io/register
- **免費額度**: 每分鐘60次請求
- **獲取步驟**:
  1. 訪問註冊頁面
  2. 填寫郵箱和密碼
  3. 驗證郵箱
  4. 在控制台查看API密鑰

### **3. Twelve Data**
- **網站**: https://twelvedata.com/
- **免費額度**: 每分鐘8次請求
- **獲取步驟**:
  1. 註冊免費賬戶
  2. 登錄後在控制台查看API密鑰
  3. 無需信用卡驗證

### **4. MarketStack**
- **網站**: https://marketstack.com/
- **免費額度**: 每分鐘5次請求
- **獲取步驟**:
  1. 註冊免費賬戶
  2. 驗證郵箱
  3. 在控制台獲取API密鑰

### **5. IEX Cloud**
- **網站**: https://iexcloud.io/cloud-login#/register
- **免費額度**: 每分鐘10次請求
- **獲取步驟**:
  1. 註冊免費賬戶
  2. 驗證郵箱
  3. 在控制台查看API密鑰

### **6. Quandl**
- **網站**: https://www.quandl.com/
- **免費額度**: 每分鐘50次請求
- **獲取步驟**:
  1. 註冊免費賬戶
  2. 驗證郵箱
  3. 在個人資料頁面查看API密鑰

## ⚙️ **配置API密鑰**

### **1. 創建環境變量文件**
```bash
cp env.example .env
```

### **2. 編輯.env文件**
```env
# 複製你的API密鑰到對應位置
ALPHA_VANTAGE_API_KEY=your_actual_key_here
FINNHUB_API_KEY=your_actual_key_here
TWELVE_DATA_API_KEY=your_actual_key_here
MARKETSTACK_API_KEY=your_actual_key_here
IEX_CLOUD_API_KEY=your_actual_key_here
QUANDL_API_KEY=your_actual_key_here
```

### **3. 在Render.com部署時設置環境變量**
1. 登錄Render.com控制台
2. 選擇你的服務
3. 進入 "Environment" 標籤
4. 添加每個API密鑰作為環境變量

## 📊 **API成功率預期**

配置所有API密鑰後，預期成功率：

| 數據源 | 成功率 | 備註 |
|--------|--------|------|
| Yahoo Finance | 85-95% | 無需API密鑰 |
| Alpha Vantage | 70-80% | 需要API密鑰 |
| Finnhub | 75-85% | 需要API密鑰 |
| Twelve Data | 65-75% | 需要API密鑰 |
| MarketStack | 60-70% | 需要API密鑰 |
| IEX Cloud | 70-80% | 需要API密鑰 |
| Quandl | 50-60% | 需要API密鑰 |
| **總體成功率** | **95-99%** | 多源備份 |

## 🔧 **測試API密鑰**

### **使用測試腳本**
```bash
python3 test_data_sources.py
```

### **檢查特定API**
```python
from backend.multi_source_collector import multi_source_collector

# 測試特定API
success, data = multi_source_collector._fetch_from_alpha_vantage('0700.HK')
print(f"Alpha Vantage: {'✅ 成功' if success else '❌ 失敗'}")
```

## 🚨 **注意事項**

### **速率限制**
- 每個API都有免費額度限制
- 系統會自動管理請求頻率
- 超過限制會自動切換到其他數據源

### **數據質量**
- 不同API的數據更新頻率不同
- 系統會優先使用更新最及時的數據源
- 回退數據確保系統始終有數據顯示

### **隱私安全**
- API密鑰僅用於數據獲取
- 不會存儲或傳輸敏感信息
- 建議定期更換API密鑰

## 🆘 **故障排除**

### **常見問題**

#### **1. API密鑰無效**
```
Error: Invalid API key
```
**解決方案**: 檢查密鑰是否正確複製，確保沒有多餘的空格

#### **2. 速率限制**
```
Error: Rate limit exceeded
```
**解決方案**: 等待一段時間後重試，或配置更多API密鑰

#### **3. 網絡超時**
```
Error: Connection timeout
```
**解決方案**: 檢查網絡連接，系統會自動重試

### **獲取幫助**
如果遇到問題：
1. 檢查API密鑰是否正確
2. 確認網絡連接正常
3. 查看系統日誌輸出
4. 運行測試腳本診斷問題

## 📈 **性能優化建議**

1. **配置多個API密鑰** - 提高數據可用性
2. **定期監控使用量** - 避免超出免費額度
3. **設置合理的緩存時間** - 減少API請求次數
4. **監控成功率** - 及時調整數據源優先級

---

**提示**: 即使沒有配置API密鑰，系統也會使用Yahoo Finance和回退數據，確保基本功能正常運行。
