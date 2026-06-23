// State Variables
let currentEtfIdx = "6";
let currentYear = 2026;
let currentMonth = 6; // 1-indexed (1 to 12)
let selectedDate = "";
let etfHistorySummary = {}; // date_str -> {new, deleted, increased, decreased}
let chartInstance = null;
let pollInterval = null;
let weightThreshold = 0.5;

// DOM Elements
const calendarDaysEl = document.getElementById("calendar-days");
const calendarMonthYearEl = document.getElementById("calendar-month-year");
const prevMonthBtn = document.getElementById("cal-prev-month");
const nextMonthBtn = document.getElementById("cal-next-month");
const selectedDateTitleEl = document.getElementById("selected-date-title");
const liveBadgeEl = document.getElementById("live-badge");
const statTotalCountEl = document.getElementById("stat-total-count");
const thresholdSelectEl = document.getElementById("threshold-select");

// Tab Count Badges
const countNewEl = document.getElementById("tab-count-new");
const countDelEl = document.getElementById("tab-count-deleted");
const countUpEl = document.getElementById("tab-count-increased");
const countDownEl = document.getElementById("tab-count-decreased");

// Tables
const tableAllBody = document.querySelector("#table-all tbody");
const tableNewBody = document.querySelector("#table-new tbody");
const tableDelBody = document.querySelector("#table-deleted tbody");
const tableUpBody = document.querySelector("#table-increased tbody");
const tableDownBody = document.querySelector("#table-decreased tbody");
const tableStockHistoryBody = document.querySelector("#table-stock-history tbody");

// Search
const stockSearchInput = document.getElementById("stock-search-input");
const searchStockBtn = document.getElementById("btn-search-stock");
const chartPlaceholder = document.getElementById("chart-placeholder");
const stockTrendChartEl = document.getElementById("stock-trend-chart");

// Crawl Tools
const crawlStartDateInput = document.getElementById("crawl-start-date");
const crawlEndDateInput = document.getElementById("crawl-end-date");
const startCrawlBtn = document.getElementById("btn-start-crawl");

// Banners
const updateBanner = document.getElementById("update-banner");
const confirmUpdateBtn = document.getElementById("btn-confirm-update");
const cancelUpdateBtn = document.getElementById("btn-cancel-update");
const crawlProgressBanner = document.getElementById("crawl-progress-banner");
const progressBarFill = document.getElementById("progress-bar-fill");
const progressText = document.getElementById("progress-text");

// Get YYYY-MM-DD local date string
function getLocalDateString() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
    // Set default dates
    const today = new Date();
    currentYear = today.getFullYear();
    currentMonth = today.getMonth() + 1;
    
    // Set crawl range inputs default
    crawlEndDateInput.value = getLocalDateString();
    updateCrawlStartDateDefault();
    
    // Setup Event Listeners
    setupEventListeners();
    
    // Load initial data
    loadEtfData();
    checkPendingUpdates();
    checkActiveCrawl();
});

// Setup Default Start Dates for Crawling based on ETF
function updateCrawlStartDateDefault() {
    const todayStr = getLocalDateString();
    const hasHistory = etfHistorySummary && Object.keys(etfHistorySummary).length > 0;
    
    if (hasHistory) {
        crawlStartDateInput.value = todayStr;
    } else {
        if (currentEtfIdx === "2") {
            crawlStartDateInput.value = "2022-05-11";
        } else {
            crawlStartDateInput.value = "2023-05-16";
        }
    }
}

// Setup all DOM event listeners
function setupEventListeners() {
    // ETF Tab Toggle
    document.querySelectorAll(".etf-tab").forEach(tab => {
        tab.addEventListener("click", (e) => {
            const targetTab = e.currentTarget;
            document.querySelectorAll(".etf-tab").forEach(t => t.classList.remove("active"));
            targetTab.classList.add("active");
            currentEtfIdx = targetTab.dataset.idx;
            
            updateCrawlStartDateDefault();
            loadEtfData();
        });
    });

    // Calendar Navigation
    prevMonthBtn.addEventListener("click", () => {
        currentMonth--;
        if (currentMonth < 1) {
            currentMonth = 12;
            currentYear--;
        }
        renderCalendar();
    });

    nextMonthBtn.addEventListener("click", () => {
        currentMonth++;
        if (currentMonth > 12) {
            currentMonth = 1;
            currentYear++;
        }
        renderCalendar();
    });

    // Details Tab Toggle
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            
            e.target.classList.add("active");
            const targetPane = document.getElementById(`tab-content-${e.target.dataset.tab}`);
            if (targetPane) targetPane.classList.add("active");
        });
    });

    // Stock Search
    searchStockBtn.addEventListener("click", () => {
        performStockAnalysis(stockSearchInput.value.strip ? stockSearchInput.value.strip() : stockSearchInput.value.trim());
    });
    stockSearchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            performStockAnalysis(stockSearchInput.value.strip ? stockSearchInput.value.strip() : stockSearchInput.value.trim());
        }
    });

    // Start Crawl Tool
    startCrawlBtn.addEventListener("click", startCrawlJob);

    // Pending Update Actions
    confirmUpdateBtn.addEventListener("click", confirmPendingUpdate);
    cancelUpdateBtn.addEventListener("click", cancelPendingUpdate);

    // Threshold Selector Change
    thresholdSelectEl.addEventListener("change", (e) => {
        weightThreshold = parseFloat(e.target.value);
        loadEtfData();
    });
}

// Show Alert Toast Message
function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    const toastMessage = document.getElementById("toast-message");
    toastMessage.textContent = message;
    
    // Style adjustments if needed
    if (type === "error") {
        toast.style.borderColor = "var(--color-del)";
        toastMessage.style.color = "var(--color-del)";
    } else if (type === "success") {
        toast.style.borderColor = "var(--color-new)";
        toastMessage.style.color = "var(--color-new)";
    } else {
        toast.style.borderColor = "var(--primary)";
        toastMessage.style.color = "var(--text-primary)";
    }

    toast.classList.remove("hidden");
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}

// Load ETF Summary History for Calendar Markers
async function loadEtfData() {
    try {
        const response = await fetch(`/api/etf/${currentEtfIdx}/history?threshold=${weightThreshold}`);
        if (!response.ok) throw new Error("데이터를 가져오는 중 오류가 발생했습니다.");
        const data = await response.json();
        
        etfHistorySummary = data.events;
        
        // Find latest date in data to select it automatically
        const dates = Object.keys(etfHistorySummary).sort();
        if (dates.length > 0) {
            const latestDate = dates[dates.length - 1];
            selectedDate = latestDate;
            
            // Adjust calendar view to show the selected date
            const parts = latestDate.split("-");
            currentYear = parseInt(parts[0]);
            currentMonth = parseInt(parts[1]);
            
            loadDateDetails(latestDate);
        } else {
            // No historical data, select today
            const todayStr = getLocalDateString();
            selectedDate = todayStr;
            loadDateDetails(todayStr);
        }
        
        updateCrawlStartDateDefault();
        renderCalendar();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Render Calendar Grid
function renderCalendar() {
    calendarMonthYearEl.textContent = `${currentYear}년 ${String(currentMonth).padStart(2, '0')}월`;
    calendarDaysEl.innerHTML = "";
    
    const firstDayIndex = new Date(currentYear, currentMonth - 1, 1).getDay();
    const lastDay = new Date(currentYear, currentMonth, 0).getDate();
    
    // Pad previous month days
    for (let i = 0; i < firstDayIndex; i++) {
        const emptyCell = document.createElement("div");
        emptyCell.classList.add("calendar-day", "empty");
        calendarDaysEl.appendChild(emptyCell);
    }
    
    // Generate active month days
    for (let day = 1; day <= lastDay; day++) {
        const dayCell = document.createElement("div");
        dayCell.classList.add("calendar-day");
        
        const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        
        // Day number
        const dayNum = document.createElement("span");
        dayNum.classList.add("calendar-day-num");
        dayNum.textContent = day;
        dayCell.appendChild(dayNum);
        
        // Check for events
        const dotsContainer = document.createElement("div");
        dotsContainer.classList.add("day-event-dots");
        
        if (etfHistorySummary[dateStr]) {
            const events = etfHistorySummary[dateStr];
            if (events.new > 0) dotsContainer.appendChild(createDot("new"));
            if (events.deleted > 0) dotsContainer.appendChild(createDot("del"));
            if (events.increased > 0) dotsContainer.appendChild(createDot("up"));
            if (events.decreased > 0) dotsContainer.appendChild(createDot("down"));
        }
        dayCell.appendChild(dotsContainer);
        
        // Selected style
        if (dateStr === selectedDate) {
            dayCell.classList.add("active");
        }
        
        // Click listener
        dayCell.addEventListener("click", () => {
            selectedDate = dateStr;
            document.querySelectorAll(".calendar-day").forEach(c => c.classList.remove("active"));
            dayCell.classList.add("active");
            loadDateDetails(dateStr);
        });
        
        calendarDaysEl.appendChild(dayCell);
    }
}

function createDot(type) {
    const dot = document.createElement("span");
    dot.classList.add("dot", `dot-${type}`);
    return dot;
}

// Fetch details for a specific date
async function loadDateDetails(dateStr) {
    try {
        selectedDateTitleEl.textContent = `${dateStr} 구성 세부 내역`;
        
        // Loading skeleton or empty screen
        setTableLoadingStates();
        
        const response = await fetch(`/api/etf/${currentEtfIdx}/date/${dateStr}?threshold=${weightThreshold}`);
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "해당 날짜의 데이터를 불러올 수 없습니다.");
        }
        const data = await response.json();
        
        // Update Live Badge
        if (data.is_live) {
            liveBadgeEl.classList.remove("hidden");
        } else {
            liveBadgeEl.classList.add("hidden");
        }
        
        // Update total stocks count
        statTotalCountEl.textContent = data.constituents.length;
        
        // Populate tab counts
        countNewEl.textContent = data.events.new.length;
        countDelEl.textContent = data.events.deleted.length;
        countUpEl.textContent = data.events.increased.length;
        countDownEl.textContent = data.events.decreased.length;
        
        // Render Tables
        renderAllTable(data.constituents, data.events);
        renderNewTable(data.events.new);
        renderDeletedTable(data.events.deleted);
        renderIncreasedTable(data.events.increased);
        renderDecreasedTable(data.events.decreased);
        
    } catch (err) {
        showToast(err.message, "error");
        setTableEmptyStates(err.message);
    }
}

function setTableLoadingStates() {
    const loadingHtml = `<tr><td colspan="7" class="text-center"><i class="fa-solid fa-spinner fa-spin"></i> 로딩 중...</td></tr>`;
    tableAllBody.innerHTML = loadingHtml;
    tableNewBody.innerHTML = loadingHtml;
    tableDelBody.innerHTML = loadingHtml;
    tableUpBody.innerHTML = loadingHtml;
    tableDownBody.innerHTML = loadingHtml;
}

function setTableEmptyStates(msg) {
    const emptyHtml = `<tr><td colspan="7" class="text-center text-muted">${msg}</td></tr>`;
    tableAllBody.innerHTML = emptyHtml;
    tableNewBody.innerHTML = emptyHtml;
    tableDelBody.innerHTML = emptyHtml;
    tableUpBody.innerHTML = emptyHtml;
    tableDownBody.innerHTML = emptyHtml;
}

// Table Render: All Constituents
function renderAllTable(constituents, events) {
    tableAllBody.innerHTML = "";
    if (constituents.length === 0) {
        tableAllBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">구성종목 내역이 없습니다.</td></tr>`;
        return;
    }
    
    // Create fast lookup maps for highlights
    const newCodes = new Set(events.new.map(x => x.code));
    const delCodes = new Set(events.deleted.map(x => x.code));
    const upCodes = new Set(events.increased.map(x => x.code));
    const downCodes = new Set(events.decreased.map(x => x.code));
    
    const sorted = [...constituents].sort((a, b) => b.weight - a.weight);
    
    sorted.forEach(item => {
        const tr = document.createElement("tr");
        
        // Row Highlight based on events
        if (newCodes.has(item.code)) {
            tr.classList.add("highlight-new");
        } else if (upCodes.has(item.code)) {
            tr.style.background = "rgba(59, 130, 246, 0.03)";
        } else if (downCodes.has(item.code)) {
            tr.style.background = "rgba(249, 115, 22, 0.03)";
        }
        
        const qBadge = upCodes.has(item.code) ? ' <span class="badge badge-up">+증가</span>' :
                       downCodes.has(item.code) ? ' <span class="badge badge-down">-감소</span>' : '';
                       
        const evalPrice = item.quantity > 0 ? Math.round(item.amount / item.quantity) : 0;
                       
        tr.innerHTML = `
            <td><strong>${item.name}</strong>${qBadge}</td>
            <td><code>${item.code}</code></td>
            <td>${item.quantity.toLocaleString()}</td>
            <td>${evalPrice > 0 ? evalPrice.toLocaleString() + '원' : '-'}</td>
            <td>${item.amount.toLocaleString()}</td>
            <td>${item.weight.toFixed(2)}%</td>
        `;
        
        // Click to analyze
        tr.addEventListener("click", () => {
            stockSearchInput.value = item.code === "CASH" ? "현금" : item.code;
            performStockAnalysis(item.code === "CASH" ? "현금" : item.code);
        });
        
        tableAllBody.appendChild(tr);
    });
}

// Table Render: New Stocks
function renderNewTable(items) {
    tableNewBody.innerHTML = "";
    if (items.length === 0) {
        tableNewBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">신규 종목이 없습니다.</td></tr>`;
        return;
    }
    
    items.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-up"><strong>${item.name}</strong></td>
            <td><code>${item.code}</code></td>
            <td>${item.quantity.toLocaleString()}</td>
            <td>${item.weight.toFixed(2)}%</td>
        `;
        tr.addEventListener("click", () => {
            stockSearchInput.value = item.code === "CASH" ? "현금" : item.code;
            performStockAnalysis(item.code === "CASH" ? "현금" : item.code);
        });
        tableNewBody.appendChild(tr);
    });
}

// Table Render: Deleted Stocks
function renderDeletedTable(items) {
    tableDelBody.innerHTML = "";
    if (items.length === 0) {
        tableDelBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">삭제된 종목이 없습니다.</td></tr>`;
        return;
    }
    
    items.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-down"><strong>${item.name}</strong></td>
            <td><code>${item.code}</code></td>
            <td>${item.quantity.toLocaleString()}</td>
            <td>${item.weight.toFixed(2)}%</td>
        `;
        tr.addEventListener("click", () => {
            stockSearchInput.value = item.code === "CASH" ? "현금" : item.code;
            performStockAnalysis(item.code === "CASH" ? "현금" : item.code);
        });
        tableDelBody.appendChild(tr);
    });
}

// Table Render: Increased Quantity
function renderIncreasedTable(items) {
    tableUpBody.innerHTML = "";
    if (items.length === 0) {
        tableUpBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">수량이 증가한 종목이 없습니다.</td></tr>`;
        return;
    }
    
    items.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${item.name}</strong></td>
            <td><code>${item.code}</code></td>
            <td>${item.prev_quantity.toLocaleString()}</td>
            <td>${item.quantity.toLocaleString()}</td>
            <td class="text-up">+${item.change_qty.toLocaleString()} (+${item.change_rate}%)</td>
            <td>${item.prev_weight.toFixed(2)}%</td>
            <td>${item.weight.toFixed(2)}% (${item.change_weight >= 0 ? '+' : ''}${item.change_weight}%)</td>
        `;
        tr.addEventListener("click", () => {
            stockSearchInput.value = item.code === "CASH" ? "현금" : item.code;
            performStockAnalysis(item.code === "CASH" ? "현금" : item.code);
        });
        tableUpBody.appendChild(tr);
    });
}

// Table Render: Decreased Quantity
function renderDecreasedTable(items) {
    tableDownBody.innerHTML = "";
    if (items.length === 0) {
        tableDownBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">수량이 감소한 종목이 없습니다.</td></tr>`;
        return;
    }
    
    items.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${item.name}</strong></td>
            <td><code>${item.code}</code></td>
            <td>${item.prev_quantity.toLocaleString()}</td>
            <td>${item.quantity.toLocaleString()}</td>
            <td class="text-down">${item.change_qty.toLocaleString()} (${item.change_rate}%)</td>
            <td>${item.prev_weight.toFixed(2)}%</td>
            <td>${item.weight.toFixed(2)}% (${item.change_weight >= 0 ? '+' : ''}${item.change_weight}%)</td>
        `;
        tr.addEventListener("click", () => {
            stockSearchInput.value = item.code === "CASH" ? "현금" : item.code;
            performStockAnalysis(item.code === "CASH" ? "현금" : item.code);
        });
        tableDownBody.appendChild(tr);
    });
}

// Perform Single Stock Historical Trend Analysis
async function performStockAnalysis(query) {
    if (!query) {
        showToast("종목명 또는 코드를 입력해 주세요.", "error");
        return;
    }
    
    chartPlaceholder.style.display = "flex";
    stockTrendChartEl.style.opacity = "0";
    tableStockHistoryBody.innerHTML = `<tr><td colspan="5" class="text-center"><i class="fa-solid fa-spinner fa-spin"></i> 분석 중...</td></tr>`;
    
    try {
        const response = await fetch(`/api/etf/${currentEtfIdx}/stock/${encodeURIComponent(query)}`);
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "종목을 찾을 수 없거나 데이터 분석에 실패했습니다.");
        }
        const data = await response.json();
        
        // Hide placeholder and show chart
        chartPlaceholder.style.display = "none";
        stockTrendChartEl.style.opacity = "1";
        
        // Render EChart
        renderStockTrendChart(data);
        
        // Render History Table
        renderStockHistoryTable(data.history);
        
    } catch (err) {
        showToast(err.message, "error");
        tableStockHistoryBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">${err.message}</td></tr>`;
    }
}

// Render ECharts dual-axis plot with actual prices on third axis
function renderStockTrendChart(data) {
    if (chartInstance) {
        chartInstance.dispose();
    }
    
    chartInstance = echarts.init(stockTrendChartEl);
    
    const dates = data.history.map(x => x.date);
    const quantities = data.history.map(x => x.quantity);
    const weights = data.history.map(x => x.weight);
    const prices = data.history.map(x => x.real_price);
    const currencySymbol = data.currency === "KRW" ? "₩" : data.currency === "JPY" ? "¥" : "$";
    
    // Create map for O(1) date present lookup
    const historyMap = new Map(data.history.map(x => [x.date, x]));
    
    const option = {
        title: {
            text: `${data.stock_name} (${data.stock_code}) 추이 분석`,
            textStyle: {
                color: '#ffffff',
                fontFamily: 'Outfit',
                fontSize: 16
            },
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'line' },
            formatter: function (params) {
                if (!params || params.length === 0) return '';
                const dateStr = params[0].axisValue;
                const item = historyMap.get(dateStr);
                
                let html = `<div style="font-family: var(--font-ui); font-size: 13px; padding: 4px; line-height: 1.6;">`;
                html += `<div style="font-weight: 700; margin-bottom: 6px; color: #fff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px;">${dateStr}</div>`;
                
                if (item && !item.present) {
                    html += `<div style="color: var(--color-del); font-weight: 600; display: flex; align-items: center; gap: 6px;">`;
                    html += `<i class="fa-solid fa-circle-minus"></i> 미보유 (포트폴리오 제외 상태)</div>`;
                } else {
                    params.forEach(p => {
                        let valStr = p.value !== undefined ? p.value.toLocaleString() : '-';
                        if (p.seriesName === '비중') {
                            valStr = p.value !== undefined ? `${Number(p.value).toFixed(2)}%` : '-';
                        } else if (p.seriesName === '실제 주가') {
                            valStr = p.value !== undefined ? `${currencySymbol}${Number(p.value).toLocaleString()}` : '-';
                        }
                        html += `<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">`;
                        html += `<span><span style="display:inline-block;margin-right:6px;border-radius:50%;width:8px;height:8px;background-color:${p.color};"></span>${p.seriesName}</span>`;
                        html += `<strong style="color: #fff;">${valStr}</strong>`;
                        html += `</div>`;
                    });
                    
                    // 평가 주가 (원화 환산)
                    if (item && item.eval_price > 0) {
                        html += `<div style="display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-top: 4px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 4px;">`;
                        html += `<span><span style="display:inline-block;margin-right:6px;border-radius:50%;width:8px;height:8px;background-color:#fbbf24;"></span>평가 주가 (원화)</span>`;
                        html += `<strong style="color: #fff;">₩${item.eval_price.toLocaleString()}</strong>`;
                        html += `</div>`;
                    }
                }
                html += `</div>`;
                return html;
            }
        },
        legend: {
            data: ['수량', '비중', '실제 주가'],
            textStyle: { color: '#9ca3af' },
            bottom: 0
        },
        grid: {
            top: '15%',
            left: '5%',
            right: '12%',
            bottom: '12%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: dates,
                axisPointer: { type: 'shadow' },
                axisLabel: { color: '#9ca3af' },
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
            }
        ],
        yAxis: [
            {
                type: 'value',
                name: '수량',
                position: 'left',
                nameTextStyle: { color: '#9ca3af' },
                axisLabel: {
                    color: '#9ca3af',
                    formatter: function(value) {
                        return value.toLocaleString();
                    }
                },
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
            },
            {
                type: 'value',
                name: '비중 (%)',
                position: 'right',
                nameTextStyle: { color: '#9ca3af' },
                axisLabel: {
                    color: '#9ca3af',
                    formatter: '{value}%'
                },
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                splitLine: { show: false }
            },
            {
                type: 'value',
                name: `실제 주가 (${data.currency})`,
                position: 'right',
                offset: 65,
                nameTextStyle: { color: '#9ca3af' },
                axisLabel: {
                    color: '#9ca3af',
                    formatter: function(value) {
                        return currencySymbol + value.toLocaleString();
                    }
                },
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                splitLine: { show: false }
            }
        ],
        series: [
            {
                name: '수량',
                type: 'line',
                data: quantities,
                smooth: true,
                itemStyle: { color: '#06b6d4' },
                lineStyle: { width: 3 }
            },
            {
                name: '비중',
                type: 'line',
                yAxisIndex: 1,
                data: weights,
                smooth: true,
                itemStyle: { color: '#a855f7' }, // purple
                lineStyle: { width: 3 }
            },
            {
                name: '실제 주가',
                type: 'line',
                yAxisIndex: 2,
                data: prices,
                smooth: true,
                itemStyle: { color: '#10b981' }, // emerald green
                lineStyle: { width: 3 }
            }
        ]
    };
    
    chartInstance.setOption(option);
    
    window.addEventListener('resize', () => {
        chartInstance.resize();
    });
}

// Render stock details table in chart tab
function renderStockHistoryTable(history) {
    tableStockHistoryBody.innerHTML = "";
    
    // Filter to only display present days and first deletion event
    const filtered = history.filter(item => item.present || item.is_deleted);
    
    if (filtered.length === 0) {
        tableStockHistoryBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">데이터가 없습니다.</td></tr>`;
        return;
    }
    
    const reversed = [...filtered].reverse(); // Show latest dates first
    reversed.forEach(item => {
        const tr = document.createElement("tr");
        
        let changeClass = "";
        let changeText = "-";
        
        if (item.is_readded) {
            tr.classList.add("highlight-new");
            changeClass = "text-up";
            changeText = "신규 진입";
        } else if (item.is_deleted) {
            tr.classList.add("highlight-del");
            changeClass = "text-down";
            changeText = "삭제됨";
        } else if (item.change_rate > 0) {
            changeClass = "text-up";
            changeText = `+${item.change_rate}%`;
        } else if (item.change_rate < 0) {
            changeClass = "text-down";
            changeText = `${item.change_rate}%`;
        }
        
        const qtyDisplay = item.quantity === 0 && item.is_deleted ? "0" : item.quantity.toLocaleString();
        const weightDisplay = item.weight === 0.0 && item.is_deleted ? "0.00%" : `${item.weight.toFixed(2)}%`;
        const amountDisplay = item.amount === 0 && item.is_deleted ? "0" : item.amount.toLocaleString();
        
        const currencySymbol = item.currency === "KRW" ? "₩" : item.currency === "JPY" ? "¥" : "$";
        const realPriceDisplay = item.real_price > 0 ? `${currencySymbol}${item.real_price.toLocaleString()}` : "-";
        const evalPriceDisplay = item.eval_price > 0 ? `₩${item.eval_price.toLocaleString()}` : "-";
        
        tr.innerHTML = `
            <td><code>${item.date}</code></td>
            <td><strong>${qtyDisplay}</strong></td>
            <td class="${changeClass}">${changeText}</td>
            <td>${weightDisplay}</td>
            <td>${realPriceDisplay}</td>
            <td>${evalPriceDisplay}</td>
            <td>${amountDisplay}</td>
        `;
        tableStockHistoryBody.appendChild(tr);
    });
}

// Trigger background crawler task
async function startCrawlJob() {
    const startDate = crawlStartDateInput.value;
    const endDate = crawlEndDateInput.value;
    
    if (!startDate || !endDate) {
        showToast("수집 시작일과 종료일을 정확히 선택해 주세요.", "error");
        return;
    }
    
    startCrawlBtn.disabled = true;
    startCrawlBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 요청 중...`;
    
    try {
        const response = await fetch("/api/etf/crawl-range", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                idx: currentEtfIdx,
                startDate: startDate,
                endDate: endDate
            })
        });
        
        if (!response.ok) throw new Error("크롤링 백그라운드 태스크 기동 실패");
        const data = await response.json();
        
        showToast("크롤링이 백그라운드에서 가동되었습니다.");
        checkActiveCrawl(); // Poll for progress
        
    } catch (err) {
        showToast(err.message, "error");
        startCrawlBtn.disabled = false;
        startCrawlBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-down"></i> 데이터 수집 시작`;
    }
}

// Check if crawl is active and show progress
async function checkActiveCrawl() {
    try {
        const response = await fetch("/api/etf/crawl-progress");
        const data = await response.json();
        
        if (data.status === "running") {
            startCrawlBtn.disabled = true;
            startCrawlBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 수집 작업 실행 중`;
            
            crawlProgressBanner.classList.remove("hidden");
            
            const current = data.current_day;
            const total = data.total_days;
            const pct = total > 0 ? (current / total * 100).toFixed(1) : 0;
            
            progressBarFill.style.width = `${pct}%`;
            progressText.textContent = `데이터 수집 중: (${current}/${total} 일자) 현재 진행: [${data.current_date}] (${pct}%)`;
            
            // Set polling interval
            if (!pollInterval) {
                pollInterval = setInterval(checkActiveCrawl, 1500);
            }
        } else {
            // Stop polling
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
            
            crawlProgressBanner.classList.add("hidden");
            startCrawlBtn.disabled = false;
            startCrawlBtn.innerHTML = `<i class="fa-solid fa-cloud-arrow-down"></i> 데이터 수집 시작`;
            
            if (data.status === "completed") {
                showToast("크롤링 작업이 성공적으로 끝났습니다! 저장 전 대기 상태를 검토하세요.", "success");
                checkPendingUpdates();
                // Reset status to idle on server after reading
                // We can query again or wait
            } else if (data.status === "error") {
                showToast("크롤링 작업 중 문제가 발생했습니다: " + data.errors.join(", "), "error");
            }
        }
    } catch (err) {
        console.error("Progress check error", err);
    }
}

// Check for updates pending confirm
async function checkPendingUpdates() {
    try {
        const response = await fetch("/api/etf/update/pending");
        const data = await response.json();
        
        if (data.has_pending) {
            let pendingMsg = "수집된 과거 데이터가 대기 상태입니다: ";
            const details = [];
            for (const idx in data.pending) {
                const info = data.pending[idx];
                const etfName = idx === "2" ? "나스닥100" : "글로벌AI";
                details.push(`${etfName} ${info.count}일분`);
            }
            updateBanner.classList.remove("hidden");
            document.getElementById("banner-text").textContent = pendingMsg + details.join(", ") + ". 승인 시 백업본이 자동 생성됩니다.";
        } else {
            updateBanner.classList.add("hidden");
        }
    } catch (err) {
        console.error("Check pending update error", err);
    }
}

// Action: Confirm Pending Update
async function confirmPendingUpdate() {
    confirmUpdateBtn.disabled = true;
    confirmUpdateBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> 백업 및 저장 중...`;
    
    try {
        const response = await fetch("/api/etf/update/confirm", { method: "POST" });
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, "success");
            updateBanner.classList.add("hidden");
            
            // Reload historical data & redraw calendars
            loadEtfData();
        } else {
            throw new Error(data.error || "업데이트 승인 실패");
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        confirmUpdateBtn.disabled = false;
        confirmUpdateBtn.innerHTML = `<i class="fa-solid fa-check"></i> 승인 및 백업 저장`;
    }
}

// Action: Cancel Pending Update
async function cancelPendingUpdate() {
    if (!confirm("대기 중인 스크래핑 데이터를 취소하고 비우시겠습니까?")) return;
    
    cancelUpdateBtn.disabled = true;
    
    try {
        const response = await fetch("/api/etf/update/cancel", { method: "POST" });
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, "success");
            updateBanner.classList.add("hidden");
        } else {
            throw new Error(data.message);
        }
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        cancelUpdateBtn.disabled = false;
    }
}
