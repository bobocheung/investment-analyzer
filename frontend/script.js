// 全局變量
let currentAnalysis = null;
let watchlist = [];

// API 基礎URL
const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:8080' : '';

// DOM 元素
const elements = {
    // 導航
    navItems: document.querySelectorAll('.nav-item'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // 股票分析
    stockSearch: document.getElementById('stock-search'),
    analyzeBtn: document.getElementById('analyze-btn'),
    analysisResults: document.getElementById('analysis-results'),
    analysisLoading: document.getElementById('analysis-loading'),
    
    // 分析結果元素
    stockName: document.getElementById('stock-name'),
    currentPrice: document.getElementById('current-price'),
    priceChange: document.getElementById('price-change'),
    stockSector: document.getElementById('stock-sector'),
    marketCap: document.getElementById('market-cap'),
    
    // 評分元素
    overallScore: document.getElementById('overall-score'),
    fundamentalScore: document.getElementById('fundamental-score'),
    technicalScore: document.getElementById('technical-score'),
    overallScoreBar: document.getElementById('overall-score-bar'),
    fundamentalScoreBar: document.getElementById('fundamental-score-bar'),
    technicalScoreBar: document.getElementById('technical-score-bar'),
    
    // 建議元素
    recommendationBadge: document.getElementById('recommendation-badge'),
    recommendationText: document.getElementById('recommendation-text'),
    targetPrice: document.getElementById('target-price'),
    upsidePotential: document.getElementById('upside-potential'),
    riskLevel: document.getElementById('risk-level'),
    confidenceLevel: document.getElementById('confidence-level'),
    
    // 詳細分析
    fundamentalDetails: document.getElementById('fundamental-details'),
    technicalDetails: document.getElementById('technical-details'),
    
    // 操作按鈕
    addToWatchlistBtn: document.getElementById('add-to-watchlist'),
    generateReportBtn: document.getElementById('generate-report'),
    downloadPdfBtn: document.getElementById('download-pdf'),
    
    // 觀察清單
    watchlistContainer: document.getElementById('watchlist-container'),
    emptyWatchlist: document.getElementById('empty-watchlist'),
    batchAnalyzeBtn: document.getElementById('batch-analyze'),
    
    // 儀表板
    economicIndicators: document.getElementById('economic-indicators'),
    sectorPerformance: document.getElementById('sector-performance'),
    watchlistPreview: document.getElementById('watchlist-preview'),
    lastUpdateTime: document.getElementById('last-update-time'),
    
    // 報告
    reportType: document.getElementById('report-type'),
    reportSymbol: document.getElementById('report-symbol'),
    generateReportBtnPage: document.getElementById('generate-report-btn'),
    reportContent: document.getElementById('report-content'),
    
    // 通知和模態框
    notification: document.getElementById('notification'),
    notificationMessage: document.getElementById('notification-message'),
    notificationClose: document.getElementById('notification-close'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close'),
    modalCancel: document.getElementById('modal-cancel'),
    modalConfirm: document.getElementById('modal-confirm')
};

// 初始化應用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    loadWatchlist();
    loadDashboardData();
    updateLastUpdateTime();
    
    // 檢查是否支持 Service Worker (PWA)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    }
}

function setupEventListeners() {
    // 導航事件
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => switchTab(item.dataset.tab));
    });
    
    // 股票分析事件
    elements.analyzeBtn.addEventListener('click', analyzeStock);
    elements.stockSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeStock();
    });
    
    // 操作按鈕事件
    elements.addToWatchlistBtn.addEventListener('click', addToWatchlist);
    elements.generateReportBtn.addEventListener('click', generateReport);
    elements.downloadPdfBtn.addEventListener('click', downloadPdf);
    
    // 觀察清單事件
    elements.batchAnalyzeBtn.addEventListener('click', batchAnalyze);
    
    // 報告頁面事件
    elements.generateReportBtnPage.addEventListener('click', generateReportFromPage);
    
    // 通知事件
    elements.notificationClose.addEventListener('click', hideNotification);
    
    // 模態框事件
    elements.modalClose.addEventListener('click', hideModal);
    elements.modalCancel.addEventListener('click', hideModal);
    
    // 點擊模態框外部關閉
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) hideModal();
    });
}

// 標籤頁切換
function switchTab(tabName) {
    // 更新導航狀態
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.tab === tabName);
    });
    
    // 更新內容顯示
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === tabName);
    });
    
    // 根據標籤頁載入相應數據
    switch(tabName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'watchlist':
            loadWatchlistDisplay();
            break;
        case 'reports':
            // 報告頁面不需要自動載入
            break;
    }
}

// 股票分析功能
async function analyzeStock() {
    const symbol = elements.stockSearch.value.trim().toUpperCase();
    
    if (!symbol) {
        showNotification('請輸入股票代碼', 'warning');
        return;
    }
    
    // 顯示載入狀態
    elements.analysisLoading.style.display = 'block';
    elements.analysisResults.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze/${symbol}`);
        const data = await response.json();
        
        if (response.ok) {
            currentAnalysis = data;
            displayAnalysisResults(data);
            showNotification(`${symbol} 分析完成`, 'success');
        } else {
            throw new Error(data.error || '分析失敗');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification(`分析失敗: ${error.message}`, 'error');
    } finally {
        elements.analysisLoading.style.display = 'none';
    }
}

function displayAnalysisResults(data) {
    const stockInfo = data.stock_info || {};
    const recommendation = data.recommendation || {};
    const fundamentalAnalysis = recommendation.details?.fundamental_analysis || {};
    const technicalAnalysis = recommendation.details?.technical_analysis || {};
    
    // 顯示股票基本信息
    elements.stockName.textContent = `${data.symbol} - ${stockInfo.name || data.symbol}`;
    // 優先使用 stockInfo 中的當前價格，然後是 recommendation 中的
    const currentPrice = stockInfo.current_price || recommendation.current_price || 0;
    elements.currentPrice.textContent = currentPrice > 0 ? `$${currentPrice.toFixed(2)}` : '價格獲取中';
    elements.stockSector.textContent = stockInfo.sector || '未分類';
    elements.marketCap.textContent = formatMarketCap(stockInfo.market_cap);
    
    // 顯示評分
    updateScore(elements.overallScore, elements.overallScoreBar, recommendation.overall_score || 0);
    updateScore(elements.fundamentalScore, elements.fundamentalScoreBar, recommendation.fundamental_score || 0);
    updateScore(elements.technicalScore, elements.technicalScoreBar, recommendation.technical_score || 0);
    
    // 顯示投資建議
    const recText = recommendation.recommendation || '分析中';
    elements.recommendationText.textContent = recText;
    elements.recommendationBadge.className = `recommendation-badge ${getRecommendationClass(recText)}`;
    
    // 優先使用 stockInfo 中的目標價格
    const targetPrice = stockInfo.target_price || recommendation.target_price;
    elements.targetPrice.textContent = targetPrice && targetPrice > 0 ? `$${targetPrice.toFixed(2)}` : '計算中';
    elements.upsidePotential.textContent = recommendation.upside_potential ? `${recommendation.upside_potential.toFixed(1)}%` : '計算中';
    elements.riskLevel.textContent = recommendation.risk_level || '評估中';
    elements.confidenceLevel.textContent = recommendation.confidence || '評估中';
    
    // 顯示詳細分析
    displayFundamentalDetails(fundamentalAnalysis);
    displayTechnicalDetails(technicalAnalysis);
    
    // 顯示結果容器
    elements.analysisResults.style.display = 'block';
}

function updateScore(scoreElement, barElement, score) {
    scoreElement.textContent = score.toFixed(1);
    barElement.style.width = `${Math.min(score, 100)}%`;
}

function getRecommendationClass(recommendation) {
    const rec = recommendation.toLowerCase();
    if (rec.includes('買入') || rec.includes('buy')) return 'buy';
    if (rec.includes('賣出') || rec.includes('sell')) return 'sell';
    return 'hold';
}

function formatMarketCap(marketCap) {
    if (!marketCap || marketCap === 0) return '數據不可用';
    
    if (marketCap >= 1e12) {
        return `$${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
        return `$${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e6) {
        return `$${(marketCap / 1e6).toFixed(2)}M`;
    }
    return `$${marketCap.toLocaleString()}`;
}

function displayFundamentalDetails(analysis) {
    elements.fundamentalDetails.innerHTML = '';
    
    // 從全局的 currentAnalysis 中獲取 stockInfo
    const stockInfo = currentAnalysis?.stock_info || {};
    
    const metrics = [
        { 
            label: 'PE比率', 
            value: analysis.pe_analysis?.ratio || stockInfo.pe_ratio, 
            format: 'ratio' 
        },
        { 
            label: 'ROE', 
            value: analysis.roe_analysis?.ratio || stockInfo.roe, 
            format: 'percentage' 
        },
        { 
            label: '債務股權比', 
            value: analysis.debt_analysis?.ratio || stockInfo.debt_to_equity, 
            format: 'ratio' 
        },
        { 
            label: '利潤率', 
            value: analysis.margin_analysis?.ratio || stockInfo.profit_margin, 
            format: 'percentage' 
        },
        { 
            label: 'PB比率', 
            value: analysis.pb_analysis?.ratio || stockInfo.price_to_book, 
            format: 'ratio' 
        }
    ];
    
    metrics.forEach(metric => {
        if (metric.value !== undefined && metric.value !== null && metric.value !== 0) {
            const item = createMetricItem(metric.label, metric.value, metric.format);
            elements.fundamentalDetails.appendChild(item);
        }
    });
    
    // 如果沒有任何指標，顯示提示信息
    if (elements.fundamentalDetails.children.length === 0) {
        const noDataDiv = document.createElement('div');
        noDataDiv.className = 'no-data-message';
        noDataDiv.textContent = '基本面數據獲取中...';
        elements.fundamentalDetails.appendChild(noDataDiv);
    }
}

function displayTechnicalDetails(analysis) {
    elements.technicalDetails.innerHTML = '';
    
    // 從全局的 currentAnalysis 中獲取技術指標
    const technicalIndicators = currentAnalysis?.technical_indicators || {};
    
    const metrics = [
        { 
            label: 'RSI', 
            value: analysis.rsi_analysis?.value || technicalIndicators.rsi, 
            format: 'decimal' 
        },
        { 
            label: 'MACD', 
            value: analysis.macd_analysis?.macd || technicalIndicators.macd, 
            format: 'decimal' 
        },
        { 
            label: 'SMA 20', 
            value: analysis.ma_analysis?.sma_20 || technicalIndicators.sma_20, 
            format: 'price' 
        },
        { 
            label: 'SMA 50', 
            value: analysis.ma_analysis?.sma_50 || technicalIndicators.sma_50, 
            format: 'price' 
        },
        { 
            label: 'SMA 200', 
            value: analysis.ma_analysis?.sma_200 || technicalIndicators.sma_200, 
            format: 'price' 
        },
        { 
            label: '成交量比率', 
            value: analysis.volume_analysis?.ratio || 1.0, 
            format: 'ratio' 
        }
    ];
    
    metrics.forEach(metric => {
        if (metric.value !== undefined && metric.value !== null && metric.value !== 0) {
            const item = createMetricItem(metric.label, metric.value, metric.format);
            elements.technicalDetails.appendChild(item);
        }
    });
    
    // 如果沒有任何指標，顯示提示信息
    if (elements.technicalDetails.children.length === 0) {
        const noDataDiv = document.createElement('div');
        noDataDiv.className = 'no-data-message';
        noDataDiv.textContent = '技術面數據計算中...';
        elements.technicalDetails.appendChild(noDataDiv);
    }
}

function createMetricItem(label, value, format) {
    const item = document.createElement('div');
    item.className = 'metric-item';
    
    const labelSpan = document.createElement('span');
    labelSpan.className = 'metric-label';
    labelSpan.textContent = label;
    
    const valueSpan = document.createElement('span');
    valueSpan.className = 'metric-value';
    valueSpan.textContent = formatValue(value, format);
    
    item.appendChild(labelSpan);
    item.appendChild(valueSpan);
    
    return item;
}

function formatValue(value, format) {
    if (value === null || value === undefined || isNaN(value)) return '計算中';
    
    switch (format) {
        case 'percentage':
            return `${(value * 100).toFixed(2)}%`;
        case 'ratio':
            return value.toFixed(2);
        case 'price':
            return `$${value.toFixed(2)}`;
        case 'decimal':
            return value.toFixed(2);
        default:
            return value.toString();
    }
}

// 觀察清單功能
async function loadWatchlist() {
    try {
        const response = await fetch(`${API_BASE}/api/watchlist`);
        const data = await response.json();
        watchlist = data || [];
    } catch (error) {
        console.error('Error loading watchlist:', error);
        watchlist = [];
    }
}

async function addToWatchlist() {
    if (!currentAnalysis) {
        showNotification('請先分析股票', 'warning');
        return;
    }
    
    const symbol = currentAnalysis.symbol;
    
    if (watchlist.includes(symbol)) {
        showNotification(`${symbol} 已在觀察清單中`, 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/watchlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbol })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            watchlist.push(symbol);
            showNotification(data.message, 'success');
            loadWatchlistDisplay();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error adding to watchlist:', error);
        showNotification(`添加失敗: ${error.message}`, 'error');
    }
}

async function removeFromWatchlist(symbol) {
    try {
        const response = await fetch(`${API_BASE}/api/watchlist/${symbol}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            watchlist = watchlist.filter(s => s !== symbol);
            showNotification(data.message, 'success');
            loadWatchlistDisplay();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error removing from watchlist:', error);
        showNotification(`移除失敗: ${error.message}`, 'error');
    }
}

async function loadWatchlistDisplay() {
    if (watchlist.length === 0) {
        elements.watchlistContainer.style.display = 'none';
        elements.emptyWatchlist.style.display = 'block';
        return;
    }
    
    elements.watchlistContainer.style.display = 'grid';
    elements.emptyWatchlist.style.display = 'none';
    elements.watchlistContainer.innerHTML = '';
    
    // 為每個觀察清單項目創建卡片
    for (const symbol of watchlist) {
        const card = createWatchlistCard(symbol);
        elements.watchlistContainer.appendChild(card);
        
        // 載入股票信息
        loadStockInfoForWatchlist(symbol, card);
    }
}

function createWatchlistCard(symbol) {
    const card = document.createElement('div');
    card.className = 'watchlist-item';
    card.innerHTML = `
        <div class="watchlist-item-header">
            <span class="watchlist-symbol">${symbol}</span>
            <button class="remove-btn" onclick="removeFromWatchlist('${symbol}')">&times;</button>
        </div>
        <div class="watchlist-info">
            <div class="loading">載入中...</div>
        </div>
    `;
    return card;
}

async function loadStockInfoForWatchlist(symbol, card) {
    try {
        const response = await fetch(`${API_BASE}/api/stocks/${symbol}/info`);
        const data = await response.json();
        
        if (response.ok) {
            const infoDiv = card.querySelector('.watchlist-info');
            infoDiv.innerHTML = `
                <div class="detail-item">
                    <span>當前價格:</span>
                    <span>$${(data.current_price || 0).toFixed(2)}</span>
                </div>
                <div class="detail-item">
                    <span>PE比率:</span>
                    <span>${(data.pe_ratio || 0).toFixed(2)}</span>
                </div>
                <div class="detail-item">
                    <span>行業:</span>
                    <span>${data.sector || 'N/A'}</span>
                </div>
            `;
        }
    } catch (error) {
        console.error(`Error loading info for ${symbol}:`, error);
    }
}

async function batchAnalyze() {
    if (watchlist.length === 0) {
        showNotification('觀察清單為空', 'warning');
        return;
    }
    
    showNotification('開始批量分析...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/api/batch-analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbols: watchlist })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('批量分析完成', 'success');
            // 可以在這裡顯示批量分析結果
            console.log('Batch analysis results:', data);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Batch analysis error:', error);
        showNotification(`批量分析失敗: ${error.message}`, 'error');
    }
}

// 儀表板功能
async function loadDashboardData() {
    loadEconomicIndicators();
    loadSectorPerformance();
    loadWatchlistPreview();
}

async function loadEconomicIndicators() {
    try {
        const response = await fetch(`${API_BASE}/api/market/economic`);
        const data = await response.json();
        
        if (response.ok) {
            displayEconomicIndicators(data);
        }
    } catch (error) {
        console.error('Error loading economic indicators:', error);
        elements.economicIndicators.innerHTML = '<div class="error">載入失敗</div>';
    }
}

function displayEconomicIndicators(data) {
    elements.economicIndicators.innerHTML = '';
    
    Object.entries(data).forEach(([key, indicator]) => {
        const item = document.createElement('div');
        item.className = 'indicator-item';
        item.innerHTML = `
            <span class="indicator-label">${getIndicatorName(key)}</span>
            <span class="indicator-value">${indicator.value || 'N/A'}</span>
        `;
        elements.economicIndicators.appendChild(item);
    });
}

function getIndicatorName(key) {
    const names = {
        'GDP': 'GDP',
        'UNEMPLOYMENT': '失業率',
        'INFLATION': '通脹率',
        'INTEREST_RATE': '利率'
    };
    return names[key] || key;
}

async function loadSectorPerformance() {
    try {
        const response = await fetch(`${API_BASE}/api/market/sectors`);
        const data = await response.json();
        
        if (response.ok) {
            displaySectorPerformance(data);
        }
    } catch (error) {
        console.error('Error loading sector performance:', error);
        elements.sectorPerformance.innerHTML = '<div class="error">載入失敗</div>';
    }
}

function displaySectorPerformance(data) {
    elements.sectorPerformance.innerHTML = '';
    
    Object.entries(data).forEach(([sector, info]) => {
        const item = document.createElement('div');
        item.className = 'sector-item';
        
        const changeClass = info.change_percent >= 0 ? 'positive' : 'negative';
        const changeSign = info.change_percent >= 0 ? '+' : '';
        
        item.innerHTML = `
            <span class="sector-name">${sector}</span>
            <span class="sector-change ${changeClass}">
                ${changeSign}${info.change_percent.toFixed(2)}%
            </span>
        `;
        elements.sectorPerformance.appendChild(item);
    });
}

async function loadWatchlistPreview() {
    elements.watchlistPreview.innerHTML = '';
    
    if (watchlist.length === 0) {
        elements.watchlistPreview.innerHTML = '<div class="empty-state">觀察清單為空</div>';
        return;
    }
    
    // 顯示前5個觀察清單項目
    const previewList = watchlist.slice(0, 5);
    
    previewList.forEach(symbol => {
        const item = document.createElement('div');
        item.className = 'watchlist-preview-item';
        item.innerHTML = `
            <span>${symbol}</span>
            <span class="loading">載入中...</span>
        `;
        elements.watchlistPreview.appendChild(item);
        
        // 載入價格信息
        loadPreviewPrice(symbol, item);
    });
    
    if (watchlist.length > 5) {
        const moreItem = document.createElement('div');
        moreItem.className = 'watchlist-preview-item';
        moreItem.innerHTML = `<span>還有 ${watchlist.length - 5} 個...</span>`;
        elements.watchlistPreview.appendChild(moreItem);
    }
}

async function loadPreviewPrice(symbol, item) {
    try {
        const response = await fetch(`${API_BASE}/api/stocks/${symbol}/info`);
        const data = await response.json();
        
        if (response.ok) {
            const priceSpan = item.querySelector('span:last-child');
            priceSpan.textContent = `$${(data.current_price || 0).toFixed(2)}`;
            priceSpan.className = '';
        }
    } catch (error) {
        console.error(`Error loading preview for ${symbol}:`, error);
    }
}

function updateLastUpdateTime() {
    elements.lastUpdateTime.textContent = new Date().toLocaleString('zh-TW');
}

// 報告功能
async function generateReport() {
    if (!currentAnalysis) {
        showNotification('請先分析股票', 'warning');
        return;
    }
    
    const symbol = currentAnalysis.symbol;
    window.open(`${API_BASE}/api/reports/${symbol}`, '_blank');
}

async function downloadPdf() {
    if (!currentAnalysis) {
        showNotification('請先分析股票', 'warning');
        return;
    }
    
    const symbol = currentAnalysis.symbol;
    
    try {
        showNotification('正在生成報告...', 'info');
        
        // 嘗試下載PDF/HTML報告
        const response = await fetch(`${API_BASE}/api/reports/${symbol}/pdf`);
        
        if (response.ok) {
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/pdf')) {
                // 如果是PDF文件，直接下載
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${symbol}_investment_report.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showNotification('PDF報告下載成功', 'success');
            } else {
                // 如果是HTML，在新窗口打開
                const html = await response.text();
                const newWindow = window.open('', '_blank');
                newWindow.document.write(html);
                newWindow.document.close();
                showNotification('報告已在新窗口打開', 'success');
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || '報告生成失敗');
        }
    } catch (error) {
        console.error('PDF download error:', error);
        showNotification(`報告生成失敗: ${error.message}`, 'error');
        
        // 備用方案：打開HTML報告
        try {
            window.open(`${API_BASE}/api/reports/${symbol}`, '_blank');
            showNotification('已打開HTML版本報告', 'info');
        } catch (fallbackError) {
            console.error('Fallback error:', fallbackError);
        }
    }
}

async function generateReportFromPage() {
    const symbol = elements.reportSymbol.value.trim().toUpperCase();
    
    if (!symbol) {
        showNotification('請輸入股票代碼', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/reports/${symbol}`);
        
        if (response.ok) {
            const html = await response.text();
            elements.reportContent.innerHTML = html;
        } else {
            const data = await response.json();
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Report generation error:', error);
        showNotification(`報告生成失敗: ${error.message}`, 'error');
    }
}

// 通知系統
function showNotification(message, type = 'info') {
    elements.notificationMessage.textContent = message;
    elements.notification.className = `notification ${type}`;
    elements.notification.style.display = 'flex';
    
    // 自動隱藏通知
    setTimeout(hideNotification, 5000);
}

function hideNotification() {
    elements.notification.style.display = 'none';
}

// 模態框系統
function showModal(title, content, onConfirm = null) {
    elements.modalTitle.textContent = title;
    elements.modalBody.innerHTML = content;
    elements.modal.style.display = 'flex';
    
    if (onConfirm) {
        elements.modalConfirm.onclick = () => {
            onConfirm();
            hideModal();
        };
    }
}

function hideModal() {
    elements.modal.style.display = 'none';
    elements.modalConfirm.onclick = null;
}

// 工具函數
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 定期更新數據
setInterval(() => {
    if (document.querySelector('.tab-content.active').id === 'dashboard') {
        loadDashboardData();
        updateLastUpdateTime();
    }
}, 300000); // 每5分鐘更新一次

// 全局錯誤處理
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showNotification('發生未知錯誤，請重試', 'error');
});

// 網絡狀態監控
window.addEventListener('online', () => {
    showNotification('網絡連接已恢復', 'success');
});

window.addEventListener('offline', () => {
    showNotification('網絡連接已斷開', 'warning');
});