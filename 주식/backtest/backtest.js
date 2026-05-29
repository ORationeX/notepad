// Backtest Simulator Module

// CORS proxies list for fallback reliability. Local /proxy is preferred when served by server.js.
const CORS_PROXIES = [
  url => `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`,
  url => `https://thingproxy.freeboard.io/fetch/${url}`,
  url => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`
];

function getProxyUrls(url) {
  const urls = [];
  const isLocalHttp = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  if (isLocalHttp) {
    urls.push(`${window.location.origin}/proxy?url=${encodeURIComponent(url)}`);
  }
  urls.push(...CORS_PROXIES.map(proxyFn => proxyFn(url)));
  return urls;
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 12000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function fetchWithProxy(url, encoding = 'utf-8') {
  let lastError = null;
  for (const proxyUrl of getProxyUrls(url)) {
    try {
      const res = await fetchWithTimeout(proxyUrl);
      if (res.ok) {
        const contentType = res.headers.get('content-type') || '';
        const buffer = await res.arrayBuffer();
        const decoder = new TextDecoder(encoding);
        const text = decoder.decode(buffer);
        // If the response is HTML (error page) treat as failure
        if (!contentType.includes('application/json') && text.trim().startsWith('<')) {
          throw new Error('HTML error page received');
        }
        if (contentType.includes('application/json') || ['{', '['].includes(text.trim().charAt(0))) {
          try { return JSON.parse(text); } catch (e) { console.warn('JSON parse failed, returning raw text', e); return text; }
        }
        // Non‑JSON response – return raw text for caller to handle
        return text;
      }
      lastError = new Error(`Proxy HTTP ${res.status}: ${proxyUrl}`);
    } catch (e) {
      lastError = e;
    }
  }
  throw lastError || new Error('All CORS proxies failed.');
}

async function fetchTextWithProxy(url, encoding = 'utf-8') {
  let lastError = null;
  for (const proxyUrl of getProxyUrls(url)) {
    try {
      const res = await fetchWithTimeout(proxyUrl);
      if (res.ok) {
        const buffer = await res.arrayBuffer();
        const decoder = new TextDecoder(encoding);
        return decoder.decode(buffer);
      }
      lastError = new Error(`Proxy HTTP ${res.status}: ${proxyUrl}`);
    } catch (e) {
      lastError = e;
    }
  }
  throw lastError || new Error('All CORS proxies failed (text).');
}

// Toast show helper
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMessage');
  const toastIcon = document.getElementById('toastIcon');
  
  if (!toast || !toastMsg || !toastIcon) return;
  
  toastMsg.innerText = message;
  if (type === 'success') toastIcon.innerText = '✅';
  else if (type === 'error') toastIcon.innerText = '❌';
  else if (type === 'warning') toastIcon.innerText = '⚠️';
  else toastIcon.innerText = 'ℹ️';

  toast.classList.add('active');
  setTimeout(() => {
    toast.classList.remove('active');
  }, 3500);
}

// Format money
function formatMoney(amount) {
  return new Intl.NumberFormat('ko-KR').format(Math.round(amount)) + '원';
}

function getPriceTrendSignal(history, index = null) {
  if (!history || history.length === 0) {
    return {
      current: null,
      sma20: null,
      sma50: null,
      sma100: null,
      momentum20: 0,
      drawdown63: 0,
      recoveryFrom63Low: 0,
      aboveSma50: false,
      aboveSma100: false,
      trendUp: false,
      weakTrend: false,
      deepDrawdown: false,
      recovering: false
    };
  }

  const endIdx = index === null || index === undefined ? history.length - 1 : index;
  const safeIdx = Math.max(0, Math.min(endIdx, history.length - 1));
  const getClose = (item) => item.close !== undefined ? item.close : item.value;
  const current = getClose(history[safeIdx]);

  const calcSma = (period) => {
    let sum = 0;
    let count = 0;
    for (let i = safeIdx; i >= 0 && count < period; i--) {
      const close = getClose(history[i]);
      if (typeof close === 'number') {
        sum += close;
        count++;
      }
    }
    return count > 0 ? sum / count : current;
  };

  const sma20 = calcSma(20);
  const sma50 = calcSma(50);
  const sma100 = calcSma(100);
  const sma200 = calcSma(200);
  const close20Ago = safeIdx >= 20 ? getClose(history[safeIdx - 20]) : current;
  const momentum20 = close20Ago ? ((current - close20Ago) / close20Ago) * 100 : 0;

  let high63 = current;
  let low63 = current;
  for (let i = safeIdx; i >= 0 && safeIdx - i < 63; i--) {
    const close = getClose(history[i]);
    if (typeof close !== 'number') continue;
    if (close > high63) high63 = close;
    if (close < low63) low63 = close;
  }

  const drawdown63 = high63 ? ((current - high63) / high63) * 100 : 0;
  const recoveryFrom63Low = low63 ? ((current - low63) / low63) * 100 : 0;
  const aboveSma50 = current >= sma50;
  const aboveSma100 = current >= sma100;
  const aboveSma200 = current >= sma200;
  const trendUp = aboveSma50 && sma20 >= sma50 && momentum20 >= 0;
  const weakTrend = (current < sma100 && momentum20 < -2) || (current < sma50 && drawdown63 <= -7.0);
  const deepDrawdown = drawdown63 <= -10;
  const recovering = current >= sma20 && momentum20 > 0 && recoveryFrom63Low >= 5;

  return {
    current,
    sma20,
    sma50,
    sma100,
    sma200,
    momentum20,
    drawdown63,
    recoveryFrom63Low,
    aboveSma50,
    aboveSma100,
    aboveSma200,
    trendUp,
    weakTrend,
    deepDrawdown,
    recovering
  };
}

function getSMAValue(dateStr, history, index, period = 5) {
  let startIdx = index;
  if (startIdx === undefined || startIdx === null) {
    startIdx = history.findIndex(item => item.date === dateStr);
    if (startIdx === -1) {
      for (let i = history.length - 1; i >= 0; i--) {
        if (history[i].date <= dateStr) {
          startIdx = i;
          break;
        }
      }
    }
  }
  if (startIdx === -1 || startIdx === undefined || startIdx === null) return null;
  
  let sum = 0;
  let count = 0;
  for (let i = 0; i < period; i++) {
    const curIdx = startIdx - i;
    if (curIdx >= 0) {
      sum += (history[curIdx].close !== undefined) ? history[curIdx].close : history[curIdx].value;
      count++;
    }
  }
  return count > 0 ? sum / count : null;
}

function getPeakInWindow(dateStr, history, index, windowSize = 20) {
  let startIdx = index;
  if (startIdx === undefined || startIdx === null) {
    startIdx = history.findIndex(item => item.date === dateStr);
    if (startIdx === -1) {
      for (let i = history.length - 1; i >= 0; i--) {
        if (history[i].date <= dateStr) {
          startIdx = i;
          break;
        }
      }
    }
  }
  if (startIdx === -1 || startIdx === undefined || startIdx === null) return null;
  
  let maxVal = -Infinity;
  for (let i = 0; i < windowSize; i++) {
    const curIdx = startIdx - i;
    if (curIdx >= 0) {
      const sma = getSMAValue(null, history, curIdx, 5);
      if (sma !== null && sma > maxVal) {
        maxVal = sma;
      }
    }
  }
  return maxVal === -Infinity ? null : maxVal;
}

function getVixValues(dateStr, vixHistory) {
  const idx = vixHistory.findIndex(item => item.date === dateStr);
  if (idx !== -1) {
    const current = vixHistory[idx].close;
    const previous = idx > 0 ? vixHistory[idx - 1].close : current;
    return { current, previous };
  }
  let current = null;
  let previous = null;
  for (let i = 0; i < vixHistory.length; i++) {
    if (vixHistory[i].date <= dateStr) {
      previous = current;
      current = vixHistory[i].close;
    } else {
      break;
    }
  }
  return { current, previous: previous || current };
}

function getDailyIndicator(dateStr, history) {
  let val = null;
  let prevVal = null;
  for (let i = 0; i < history.length; i++) {
    if (history[i].date < dateStr) {
      prevVal = val;
      val = history[i].value;
    } else {
      break;
    }
  }
  return { current: val, previous: prevVal };
}

function getUnemploymentRates(dateStr, unrateHistory) {
  const date = new Date(dateStr);
  const year = date.getFullYear();
  const month = date.getMonth();
  const day = date.getDate();
  
  let publishLimit;
  if (day >= 8) {
    publishLimit = new Date(year, month - 1, 1);
  } else {
    publishLimit = new Date(year, month - 2, 1);
  }
  
  const available = unrateHistory.filter(item => new Date(item.date) <= publishLimit);
  if (available.length >= 2) {
    const current = available[available.length - 1].value;
    const previous = available[available.length - 2].value;
    
    // Calculate Sahm Rule (3-month average compared to 12-month low of 3-month averages)
    let current3mAvg = current;
    if (available.length >= 3) {
      current3mAvg = (available[available.length - 1].value + available[available.length - 2].value + available[available.length - 3].value) / 3;
    }
    
    let min3mAvg12m = current3mAvg;
    const limit = Math.min(available.length, 12);
    let minVal = Infinity;
    for (let i = 0; i < limit; i++) {
      const idx = available.length - 1 - i;
      if (idx >= 2) {
        const avg = (available[idx].value + available[idx-1].value + available[idx-2].value) / 3;
        if (avg < minVal) {
          minVal = avg;
        }
      }
    }
    if (minVal !== Infinity) {
      min3mAvg12m = minVal;
    }
    
    const sahmValue = current3mAvg - min3mAvg12m;
    const sahmTrigger = sahmValue >= 0.5;

    return { current, previous, sahmTrigger, sahmValue };
  } else if (available.length === 1) {
    return { current: available[0].value, previous: available[0].value, sahmTrigger: false, sahmValue: 0 };
  }
  return { current: 4.0, previous: 4.0, sahmTrigger: false, sahmValue: 0 };
}

async function loadYahooHistory(ticker, start, end) {
  const p1 = Math.floor(start.getTime() / 1000);
  const p2 = Math.floor(end.getTime() / 1000);
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?period1=${p1}&period2=${p2}&interval=1d`;
  const data = await fetchWithProxy(url);
  if (!data || !data.chart || !data.chart.result || !data.chart.result[0]) {
    throw new Error(`${ticker} 데이터를 가져오지 못했습니다.`);
  }
  const result = data.chart.result[0];
  const timestamps = result.timestamp || [];
  const closes = result.indicators.quote[0].close || [];
  const history = [];
  for (let i = 0; i < timestamps.length; i++) {
    if (closes[i] === null || closes[i] === undefined || isNaN(closes[i])) continue;
    const dateStr = new Date(timestamps[i] * 1000).toISOString().split('T')[0];
    history.push({ date: dateStr, close: parseFloat(closes[i].toFixed(4)) });
  }
  return history;
}

async function loadFredHistory(seriesId) {
  const url = `https://fred.stlouisfed.org/graph/fredgraph.csv?id=${seriesId}`;
  const text = await fetchTextWithProxy(url);
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  const history = [];
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(',');
    if (parts.length !== 2) continue;
    const val = parseFloat(parts[1]);
    if (!isNaN(val)) {
      history.push({ date: parts[0], value: parseFloat(val.toFixed(4)) });
    }
  }
  return history;
}

function toggleCustomWeights() {
  const model = document.getElementById('backtestWeightModel').value;
  const container = document.getElementById('customWeightsContainer');
  if (model === 'custom') {
    container.style.display = 'grid';
  } else {
    container.style.display = 'none';
  }
}

// Chart.js instance variable
let backtestChartInstance = null;
let latestTradeLogs = [];

const STAGE_TARGET_STOCK_PCT = {
  "1단계: 평상시": 100,
  "2-1단계: 위기 감지 (역전 정상화 대기)": 85,
  "2-2단계: 위기 감지 (지표 악화)": 60,
  "3단계: 폭락 진행": 30,
  "4-1단계: 바닥 반등 1차": 80,
  "4-2단계: 바닥 반등 2차": 100
};

function getStageTargetStockPct(stageTitle) {
  if (Object.prototype.hasOwnProperty.call(STAGE_TARGET_STOCK_PCT, stageTitle)) {
    return STAGE_TARGET_STOCK_PCT[stageTitle];
  }
  return 100;
}

// --- MAIN BACKTEST FUNCTION ---
async function runHistoricalBacktest() {
  const startStr = document.getElementById('backtestStartDate').value;
  const endStr = document.getElementById('backtestEndDate').value;
  const principal = parseFloat(document.getElementById('backtestPrincipal').value) || 10000000;
  const feeRate = (parseFloat(document.getElementById('backtestFee').value) || 0.1) / 100;

  if (!startStr || !endStr) {
    showToast('시작일과 종료일을 지정하세요.', 'warning');
    return;
  }

  const startDate = new Date(startStr);
  const endDate = new Date(endStr);

  if (startDate >= endDate) {
    showToast('시작일은 종료일보다 이전이어야 합니다.', 'warning');
    return;
  }

  // Show progress
  const progressCard = document.getElementById('backtestProgressCard');
  const progressText = document.getElementById('backtestProgressText');
  const progressBar = document.getElementById('backtestProgressBar');
  const resultsSection = document.getElementById('backtestResultsSection');

  progressCard.style.display = 'block';
  resultsSection.style.display = 'none';
  progressBar.style.width = '0%';

  try {
    // Calculate query start date (1 year before selected start date) for technical indicator warm-up
    const queryStartDate = new Date(startDate);
    queryStartDate.setFullYear(queryStartDate.getFullYear() - 1);

    // Step 1: Load QQQ history
    progressText.innerText = '나스닥 (QQQ) 역사적 시세 다운로드 중...';
    progressBar.style.width = '15%';
    const qqqHistory = await loadYahooHistory('QQQ', queryStartDate, endDate);

    // Step 2: Load TLT history
    progressText.innerText = '미국 장기채 (TLT) 역사적 시세 다운로드 중...';
    progressBar.style.width = '30%';
    const tltHistory = await loadYahooHistory('TLT', queryStartDate, endDate);

    // Step 3: Load SHY history (cash proxy)
    progressText.innerText = '미국 단기채 (SHY) 역사적 시세 다운로드 중...';
    progressBar.style.width = '45%';
    const shyHistory = await loadYahooHistory('SHY', queryStartDate, endDate);

    // Step 4: Load VIX history
    progressText.innerText = '변동성 지수 (VIX) 역사적 시세 다운로드 중...';
    progressBar.style.width = '55%';
    const vixHistory = await loadYahooHistory('^VIX', queryStartDate, endDate);

    // Step 5: Load FRED indicators
    progressText.innerText = '미국채 장단기 금리차 (10Y-2Y) 데이터 다운로드 중...';
    progressBar.style.width = '68%';
    const yieldHistory = await loadFredHistory('T10Y2Y');

    progressText.innerText = '미국 신용 스프레드 (Baa) 데이터 다운로드 중...';
    progressBar.style.width = '80%';
    const hyHistory = await loadFredHistory('BAA10Y');

    progressText.innerText = '미국 실업률 데이터 다운로드 중...';
    progressBar.style.width = '90%';
    const unrateHistory = await loadFredHistory('UNRATE');

    // Step 6: Simulation
    progressText.innerText = '자산 배분 백테스트 시뮬레이션 계산 중...';
    progressBar.style.width = '95%';

    // Map pricing histories for O(1) lookups
    const tltMap = new Map();
    tltHistory.forEach(item => tltMap.set(item.date, item.close));
    const shyMap = new Map();
    shyHistory.forEach(item => shyMap.set(item.date, item.close));

    // Setup timeline of trading days where both exist
    const timeline = qqqHistory.filter(item => tltMap.has(item.date));

    if (timeline.length === 0) {
      throw new Error('선택된 기간에 유효한 시세 데이터 거래일이 존재하지 않습니다.');
    }

    // Find the first index in timeline where date is on or after the selected startDate
    const startSimulationIdx = timeline.findIndex(item => new Date(item.date) >= startDate);
    if (startSimulationIdx === -1) {
      throw new Error('선택된 시작일에 해당하는 거래일 데이터를 찾을 수 없습니다.');
    }

    // Initialize variables for strategies
    // Strategy 1: 100% QQQ
    let s1Shares = 0;
    let s1Cash = principal;

    // Strategy 2: Compass Active Trading
    let s2Shares = 0;
    let s2Cash = principal;
    
    // History logs for chart
    const dates = [];
    const s1Values = [];
    const s2Values = [];
    const tradeLogs = [];
    const stages = [];
    const triggerReasons = [];
    let lastStage = null;
    let priceWeakDays = 0;

    // State machine for stage transition filtering (Hysteresis & Cooldown)
    const STAGE_SEVERITY = {
      "1단계: 평상시": 1,
      "4-2단계: 바닥 반등 2차": 2,
      "4-1단계: 바닥 반등 1차": 3,
      "2-1단계: 위기 감지 (역전 정상화 대기)": 4,
      "2-2단계: 위기 감지 (지표 악화)": 5,
      "3단계: 폭락 진행": 6
    };
    let currentStage = "1단계: 평상시";
    let daysInCurrentStage = 0;
    let lastTriggerReason = "최초 포트폴리오 설정";

    const stageCounts = {
      "1단계: 평상시": 0,
      "2-1단계: 위기 감지 (역전 정상화 대기)": 0,
      "2-2단계: 위기 감지 (지표 악화)": 0,
      "3단계: 폭락 진행": 0,
      "4-1단계: 바닥 반등 1차": 0,
      "4-2단계: 바닥 반등 2차": 0
    };

    // Loop over the timeline
    for (let idx = 0; idx < timeline.length; idx++) {
      const item = timeline[idx];
      const dateStr = item.date;
      const qqqPrice = item.close;
      const tltPrice = tltMap.get(dateStr);

      // Get macro indicators for this day
      const vix = getVixValues(dateStr, vixHistory);
      const yieldCurve = getDailyIndicator(dateStr, yieldHistory);
      const hy = getDailyIndicator(dateStr, hyHistory);
      const unrate = getUnemploymentRates(dateStr, unrateHistory);

      // Find current indexes in history lists to compute SMA
      let vixIdx = vixHistory.findIndex(v => v.date === dateStr);
      if (vixIdx === -1) vixIdx = vixHistory.findIndex(v => v.date <= dateStr);
      
      let yieldIdx = yieldHistory.findIndex(y => y.date === dateStr);
      if (yieldIdx === -1) {
        for (let i = yieldHistory.length - 1; i >= 0; i--) {
          if (yieldHistory[i].date <= dateStr) { yieldIdx = i; break; }
        }
      }

      let hyIdx = hyHistory.findIndex(h => h.date === dateStr);
      if (hyIdx === -1) {
        for (let i = hyHistory.length - 1; i >= 0; i--) {
          if (hyHistory[i].date <= dateStr) { hyIdx = i; break; }
        }
      }

      // Calculate smoothed SMA indicators
      const vixSMA = getSMAValue(null, vixHistory, vixIdx, 5) || vix.current;
      const previousVixSMA = getSMAValue(null, vixHistory, vixIdx - 1, 5) || vixSMA;
      const vixPeak20d = getPeakInWindow(null, vixHistory, vixIdx, 20) || vixSMA;

      const hySMA = getSMAValue(null, hyHistory, hyIdx, 5) || hy.current;
      const previousHySMA = getSMAValue(null, hyHistory, hyIdx - 1, 5) || hySMA;
      const hyPeak20d = getPeakInWindow(null, hyHistory, hyIdx, 20) || hySMA;

      // Check T10Y2Y recent inversion in past 252 business days
      let yieldCurveInvertedRecently = false;
      if (yieldIdx !== -1) {
        const limit = Math.min(yieldIdx + 1, 252);
        for (let i = 0; i < limit; i++) {
          if (yieldHistory[yieldIdx - i].value < 0) {
            yieldCurveInvertedRecently = true;
            break;
          }
        }
      }

      // Refined Stage Decision Logic with Double Regime Model (Bull vs Bear Regime Filter)
      const vixFallingFromStress = vixPeak20d >= 28 && vixSMA <= vixPeak20d - 3;
      const highYieldRising = previousHySMA !== null && hySMA > previousHySMA;
      const highYieldRisingFromStress = highYieldRising && hySMA >= 2.6;
      const highYieldFallingFromStress = hyPeak20d >= 2.3 && hySMA <= hyPeak20d - 0.1;
      const priceSignal = getPriceTrendSignal(qqqHistory, qqqHistory.findIndex(q => q.date === dateStr));
      const hasPriceSignal = priceSignal.current !== null;
      
      // Time filter (5 consecutive trading days of weakness required to trigger warning)
      const isPriceWeakCandidate = hasPriceSignal && (priceSignal.weakTrend || priceSignal.deepDrawdown);
      if (isPriceWeakCandidate) {
        priceWeakDays++;
      } else {
        priceWeakDays = 0;
      }
      const priceWeakWarning = priceWeakDays >= 5;
      
      const priceRecoveryConfirmed = hasPriceSignal && (priceSignal.recovering || priceSignal.trendUp);
      const yieldCurveRiskConfirmed = yieldCurveInvertedRecently && (vix.current >= 20 || (hasPriceSignal && (priceSignal.weakTrend || !priceSignal.aboveSma100)));

      let candidateStage = "1단계: 평상시";
      let candidateReason = "안정적 매크로 지표";

      if (hasPriceSignal && !priceSignal.aboveSma200) {
        // Bear Regime (QQQ Price < SMA 200) - Structurally Defensive
        if (vixSMA >= 28 || hySMA >= 2.8 || priceSignal.drawdown63 <= -15.0) {
          candidateStage = "3단계: 폭락 진행";
          if (vixSMA >= 28) candidateReason = `곰시장 폭락 (VIX SMA ${vixSMA.toFixed(1)} ≥ 28)`;
          else if (hySMA >= 2.8) candidateReason = `곰시장 신용 위험 (스프레드 ${hySMA.toFixed(2)}% ≥ 2.8%)`;
          else candidateReason = `곰시장 폭락 심화 (낙폭 ${priceSignal.drawdown63.toFixed(1)}%)`;
        } else if (vixSMA >= 22 || (unrate.sahmTrigger && unrate.current >= 4.5) || priceSignal.drawdown63 <= -8.0) {
          candidateStage = "2-2단계: 위기 감지 (지표 악화)";
          if (vixSMA >= 22) candidateReason = `곰시장 지표 불안 (VIX SMA ${vixSMA.toFixed(1)} ≥ 22)`;
          else if (unrate.sahmTrigger) candidateReason = `곰시장 경기침체 (Sahm Rule)`;
          else candidateReason = `곰시장 추세 하락 (낙폭 ${priceSignal.drawdown63.toFixed(1)}%)`;
        } else if (highYieldFallingFromStress && priceRecoveryConfirmed) {
          candidateStage = "4-2단계: 바닥 반등 2차";
          candidateReason = `곰시장 바닥 반등 (신용 스프레드 하락 및 가격 반등)`;
        } else if (vixFallingFromStress && priceRecoveryConfirmed) {
          candidateStage = "4-1단계: 바닥 반등 1차";
          candidateReason = `곰시장 바닥 반등 (VIX 하락 및 가격 반등)`;
        } else {
          // Default defensive state in bear market
          candidateStage = "2-1단계: 위기 감지 (역전 정상화 대기)";
          candidateReason = `곰시장 장기 침체 국면 (이평선 아래 횡보)`;
        }
      } else {
        // Bull Regime (QQQ Price >= SMA 200) - Structurally Growth
        if (highYieldFallingFromStress && priceRecoveryConfirmed) {
          candidateStage = "4-2단계: 바닥 반등 2차";
          candidateReason = `신용 스프레드 안정 (SMA ${hySMA.toFixed(2)}% ≤ 고점 ${hyPeak20d.toFixed(2)}% - 0.1%) & 가격 반등`;
        } else if (vixFallingFromStress && priceRecoveryConfirmed) {
          candidateStage = "4-1단계: 바닥 반등 1차";
          candidateReason = `VIX 안정 (SMA ${vixSMA.toFixed(1)} ≤ 고점 ${vixPeak20d.toFixed(1)} - 3.0) & 가격 반등`;
        } else if (vixSMA >= 30 || hySMA >= 3.0 || (highYieldRising && hySMA >= 2.8) || (priceSignal.deepDrawdown && priceSignal.weakTrend)) {
          candidateStage = "3단계: 폭락 진행";
          if (vixSMA >= 30) candidateReason = `강세장 중 시스템 위기 (VIX SMA ${vixSMA.toFixed(1)} ≥ 30)`;
          else if (hySMA >= 3.0) candidateReason = `강세장 중 신용 위기 (스프레드 ${hySMA.toFixed(2)}% ≥ 3.0%)`;
          else if (highYieldRising && hySMA >= 2.8) candidateReason = `강세장 중 스프레드 급등 (${hySMA.toFixed(2)}%)`;
          else candidateReason = `강세장 중 폭락 발생 (낙폭 ${priceSignal.drawdown63.toFixed(1)}% & 추세 약화)`;
        } else if (vixSMA >= 25 || (unrate.sahmTrigger && unrate.current >= 4.5) || priceWeakWarning) {
          candidateStage = "2-2단계: 위기 감지 (지표 악화)";
          if (vixSMA >= 25) candidateReason = `강세장 중 지표 경고 (VIX SMA ${vixSMA.toFixed(1)} ≥ 25)`;
          else if (unrate.sahmTrigger && unrate.current >= 4.5) candidateReason = `강세장 중 고용 경보 (Sahm Rule)`;
          else candidateReason = `강세장 중 추세 약화 (낙폭 ${priceSignal.drawdown63.toFixed(1)}%)`;
        } else if (yieldCurveRiskConfirmed) {
          candidateStage = "2-1단계: 위기 감지 (역전 정상화 대기)";
          candidateReason = `강세장 중 금리역전 대기 상태 (역전 후 변동성 상승)`;
        } else {
          candidateStage = "1단계: 평상시";
          candidateReason = "안정적 매크로 지표 (구조적 강세장)";
        }
      }

      // Hysteresis & Cooldown filter to prevent whipsaw
      let stageTitle = currentStage;
      let triggerReason = lastTriggerReason;

      if (idx === 0) {
        stageTitle = candidateStage;
        triggerReason = "최초 포트폴리오 설정";
        daysInCurrentStage = 0;
      } else {
        const currentSeverity = STAGE_SEVERITY[currentStage] || 1;
        const candidateSeverity = STAGE_SEVERITY[candidateStage] || 1;

        daysInCurrentStage++;

        if (candidateSeverity > currentSeverity) {
          // Risk is rising: Upgrade severity immediately for capital protection
          stageTitle = candidateStage;
          triggerReason = candidateReason;
          daysInCurrentStage = 0;
        } else if (candidateSeverity < currentSeverity) {
          // Risk is declining: Cooldown and Hysteresis check
          let canDowngrade = false;

          // Accelarated downgrade if price recovery is strongly confirmed
          if (priceRecoveryConfirmed && candidateStage.includes("바닥 반등")) {
            canDowngrade = true;
          } else if (daysInCurrentStage >= 10) {
            // Otherwise, wait at least 10 trading days (approx 2 weeks) to ensure stability
            canDowngrade = true;
          }

          // Hysteresis: Do not leave high-risk states if indicators are still close to warning thresholds
          if (currentStage === "3단계: 폭락 진행") {
            if (vixSMA >= 27 || hySMA >= 2.7) {
              canDowngrade = false; // Block downgrade
            }
          } else if (currentStage === "2-2단계: 위기 감지 (지표 악화)") {
            if (vixSMA >= 23 || (unrate.sahmTrigger && unrate.current >= 4.5)) {
              canDowngrade = false; // Block downgrade
            }
          }

          if (canDowngrade) {
            stageTitle = candidateStage;
            triggerReason = candidateReason;
            daysInCurrentStage = 0;
          }
        }
      }

      currentStage = stageTitle;
      lastTriggerReason = triggerReason;

      // Skip portfolio calculations during the warm-up period
      if (idx < startSimulationIdx) {
        continue;
      }

      stageCounts[stageTitle] = (stageCounts[stageTitle] || 0) + 1;

      // Day 0: Initial Purchases
      if (idx === startSimulationIdx) {
        // Strategy 1: QQQ 100%
        s1Shares = (principal * (1 - feeRate)) / qqqPrice;
        s1Cash = 0;

        // Strategy 2: Compass Active Trading
        const targetStockPct = getStageTargetStockPct(stageTitle);
        s2Shares = (principal * (targetStockPct / 100) * (1 - feeRate)) / qqqPrice;
        s2Cash = principal * (1 - targetStockPct / 100);

        let initialActionText = "최초 포트폴리오 설정 (Init)";
        let initialActionHtml = `<span class="action-badge buy" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.30); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">🟢 최초 ${targetStockPct}% 설정</span>`;
        if (targetStockPct <= 20) {
          initialActionHtml = `<span class="action-badge hold-cash" style="background: rgba(156, 163, 175, 0.05); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.15); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">⚪ 최초 방어 ${targetStockPct}% 설정</span>`;
        }

        tradeLogs.push({
          date: dateStr,
          stage: stageTitle,
          triggerReason: "최초 포트폴리오 설정",
          vix: vixSMA,
          yieldCurve: yieldCurve.current,
          hy: hySMA,
          unrate: unrate.current,
          qqqPrice,
          actionText: initialActionText,
          actionBadge: initialActionHtml
        });
        lastStage = stageTitle;
      } else {
        // Daily cash growth from SHY (cash proxy), fallback to fixed risk-free rate
        const currentShy = shyMap.get(dateStr);
        const prevDayDate = timeline[idx - 1] ? timeline[idx - 1].date : null;
        const prevShy = prevDayDate ? shyMap.get(prevDayDate) : null;
        let dailyRfRate = 0.02 / 252;
        if (typeof currentShy === 'number' && typeof prevShy === 'number' && prevShy > 0) {
          dailyRfRate = (currentShy - prevShy) / prevShy;
        }
        s2Cash = s2Cash * (1 + dailyRfRate);

        // 1. Determine target allocation using Weekly Trend + Macro Mapped Strategy
        const nextItem = timeline[idx + 1];
        const isEndOfWeek = !nextItem || new Date(nextItem.date).getDay() < new Date(dateStr).getDay();
        
        const prevS2Val = s2Shares * qqqPrice + s2Cash;
        const currentStockPct = prevS2Val > 0 ? ((s2Shares * qqqPrice) / prevS2Val) * 100 : 0;
        let targetStockPct = currentStockPct;
        let actionText = "보유 (Hold)";
        let actionHtml = `<span class="action-badge hold" style="background: rgba(156, 163, 175, 0.1); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.20); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">⚪ 보유</span>`;

        // Evaluate signal updates only at the end of each week (Friday) to filter noise/whipsaws
        if (isEndOfWeek) {
          const baseTargetPct = getStageTargetStockPct(stageTitle);
          targetStockPct = baseTargetPct;

          // Re-entry boost: if trend recovers before full regime normalization, raise target faster
          if (priceSignal.current >= priceSignal.sma200 || (priceSignal.current >= priceSignal.sma50 && priceSignal.momentum20 > 0)) {
            targetStockPct = Math.max(targetStockPct, 90);
          }

          // Strong upside trend: do not underinvest in prolonged bull legs
          if (priceSignal.trendUp && priceSignal.aboveSma200 && priceSignal.momentum20 > 2) {
            targetStockPct = 100;
          }

          // Extra defense in full crash trend
          if (stageTitle === "3단계: 폭락 진행" && priceSignal.current < priceSignal.sma200) {
            targetStockPct = Math.min(targetStockPct, 30);
          }

          const diffPct = targetStockPct - currentStockPct;
          if (Math.abs(diffPct) >= 10) {
            if (diffPct > 0) {
              actionText = `비중확대 (+${diffPct.toFixed(0)}%p)`;
              actionHtml = `<span class="action-badge buy" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.30); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">🟢 비중확대 ${targetStockPct.toFixed(0)}%</span>`;
            } else {
              actionText = `비중축소 (${diffPct.toFixed(0)}%p)`;
              actionHtml = `<span class="action-badge sell" style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.35); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">🔴 비중축소 ${targetStockPct.toFixed(0)}%</span>`;
            }
          } else {
            targetStockPct = currentStockPct;
          }
        }

        // Mid-week fast re-entry: avoid missing V-shaped recoveries between weekly checks
        if (!isEndOfWeek) {
          const quickReentry = (priceSignal.current >= priceSignal.sma200) || (priceSignal.current >= priceSignal.sma50 && priceSignal.momentum20 > 1.0);
          if (quickReentry) {
            const boostedTarget = Math.max(targetStockPct, 90);
            if (boostedTarget > currentStockPct) {
              targetStockPct = boostedTarget;
              const diffPct = targetStockPct - currentStockPct;
              actionText = `빠른 재진입 (+${diffPct.toFixed(0)}%p)`;
              actionHtml = `<span class="action-badge buy" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.30); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">🟢 빠른 재진입 ${targetStockPct.toFixed(0)}%</span>`;
            }
          }
        }

        // 2. Decide if we should trade
        let shouldTrade = false;
        if (Math.abs(targetStockPct - currentStockPct) >= 5) shouldTrade = true;

        if (shouldTrade) {
          const targetQQQVal = prevS2Val * (targetStockPct / 100);
          const currentQQQVal = s2Shares * qqqPrice;
          const tradeValue = Math.abs(targetQQQVal - currentQQQVal);
          const fee = tradeValue * feeRate;
          const netTotalVal = prevS2Val - fee;

          s2Shares = (netTotalVal * (targetStockPct / 100)) / qqqPrice;
          s2Cash = netTotalVal * (1 - targetStockPct / 100);

          tradeLogs.push({
            date: dateStr,
            stage: stageTitle,
            triggerReason: triggerReason,
            vix: vixSMA,
            yieldCurve: yieldCurve.current,
            hy: hySMA,
            unrate: unrate.current,
            qqqPrice,
            actionText: actionText,
            actionBadge: actionHtml
          });
          lastStage = stageTitle;
        } else {
          // Log stage changes for compass diagnosis even if no trade was executed
          if (stageTitle !== lastStage) {
            const logActionText = `보유 (주식 ${targetStockPct.toFixed(0)}%)`;
            const logActionHtml = targetStockPct >= 50 ?
              `<span class="action-badge hold" style="background: rgba(156, 163, 175, 0.1); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.20); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">⚪ 보유</span>` :
              `<span class="action-badge hold-cash" style="background: rgba(156, 163, 175, 0.05); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.15); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.72rem; white-space: nowrap;">⚪ 현금 보유</span>`;

            tradeLogs.push({
              date: dateStr,
              stage: stageTitle,
              triggerReason: triggerReason,
              vix: vixSMA,
              yieldCurve: yieldCurve.current,
              hy: hySMA,
              unrate: unrate.current,
              qqqPrice,
              actionText: logActionText,
              actionBadge: logActionHtml
            });
            lastStage = stageTitle;
          }
        }
      }

      // Record valuations
      const s1Val = s1Shares * qqqPrice + s1Cash;
      const s2Val = s2Shares * qqqPrice + s2Cash;

      dates.push(dateStr);
      s1Values.push(s1Val);
      s2Values.push(s2Val);
      stages.push(stageTitle);
      triggerReasons.push(triggerReason);
    }

    // Calculate performance metrics
    const years = timeline.length / 252; // Market days per year

    const calcMetrics = (vals) => {
      const finalVal = vals[vals.length - 1];
      const totalReturn = ((finalVal - principal) / principal) * 100;
      const cagr = (Math.pow(finalVal / principal, 1 / years) - 1) * 100;

      // MDD
      let peak = -Infinity;
      let maxD = 0;
      for (let v of vals) {
        if (v > peak) peak = v;
        const draw = (peak - v) / peak;
        if (draw > maxD) maxD = draw;
      }
      const mdd = maxD * 100;

      // Sharpe Ratio (daily returns based, rf=2.0%)
      const dReturns = [];
      for (let i = 1; i < vals.length; i++) {
        dReturns.push((vals[i] - vals[i - 1]) / vals[i - 1]);
      }
      const mean = dReturns.reduce((sum, r) => sum + r, 0) / dReturns.length;
      const variance = dReturns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / (dReturns.length - 1);
      const std = Math.sqrt(variance);
      
      const annReturn = mean * 252;
      const annVol = std * Math.sqrt(252);
      const sharpe = annVol > 0 ? (annReturn - 0.02) / annVol : 0;

      return { finalVal, totalReturn, cagr, mdd, sharpe };
    };

    const m1 = calcMetrics(s1Values);
    const m2 = calcMetrics(s2Values);

    // Update KPI Cards UI
    const kpiGrid = document.getElementById('backtestKpiGrid');
    kpiGrid.innerHTML = '';
    kpiGrid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(280px, 1fr))';
    kpiGrid.style.justifyContent = 'stretch';

    // QQQ Buy & Hold Card
    const roiColor1 = m1.totalReturn >= 0 ? 'var(--success)' : 'var(--danger)';
    const card1 = document.createElement('div');
    card1.className = 'card kpi-card';
    card1.style.marginBottom = '0';
    card1.style.borderLeft = `4px solid #f97316`;
    card1.innerHTML = `
      <div class="kpi-title" style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600;">나스닥 100% 매수보유 (QQQ)</div>
      <div class="kpi-value" style="font-size: 1.4rem; font-weight: 700; margin: 0.5rem 0; font-family: var(--font-display); color: var(--text-primary);">${formatMoney(m1.finalVal)}</div>
      <div class="kpi-stats" style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.6;">
        <div>누적 수익률: <span style="font-weight: 600; color: ${roiColor1};">${m1.totalReturn.toFixed(2)}%</span></div>
        <div>연평균 수익률 (CAGR): <span style="font-weight: 600; color: var(--text-primary);">${m1.cagr.toFixed(2)}%</span></div>
        <div>최대 낙폭 (MDD): <span style="font-weight: 600; color: var(--danger);">${m1.mdd > 0 ? '-' : ''}${m1.mdd.toFixed(2)}%</span></div>
        <div>샤프 지수 (Sharpe): <span style="font-weight: 600; color: var(--text-primary);">${m1.sharpe.toFixed(2)}</span></div>
      </div>
    `;
    kpiGrid.appendChild(card1);

    // Compass Active Card
    const roiColor2 = m2.totalReturn >= 0 ? 'var(--success)' : 'var(--danger)';
    const card2 = document.createElement('div');
    card2.className = 'card kpi-card';
    card2.style.marginBottom = '0';
    card2.style.borderLeft = `4px solid #06b6d4`;
    card2.innerHTML = `
      <div class="kpi-title" style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600;">나침반 신호매매 전략 (Active)</div>
      <div class="kpi-value" style="font-size: 1.4rem; font-weight: 700; margin: 0.5rem 0; font-family: var(--font-display); color: var(--text-primary);">${formatMoney(m2.finalVal)}</div>
      <div class="kpi-stats" style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.6;">
        <div>누적 수익률: <span style="font-weight: 600; color: ${roiColor2};">${m2.totalReturn.toFixed(2)}%</span></div>
        <div>연평균 수익률 (CAGR): <span style="font-weight: 600; color: var(--text-primary);">${m2.cagr.toFixed(2)}%</span></div>
        <div>최대 낙폭 (MDD): <span style="font-weight: 600; color: var(--danger);">${m2.mdd > 0 ? '-' : ''}${m2.mdd.toFixed(2)}%</span></div>
        <div>샤프 지수 (Sharpe): <span style="font-weight: 600; color: var(--text-primary);">${m2.sharpe.toFixed(2)}</span></div>
      </div>
    `;
    kpiGrid.appendChild(card2);

    // Render logs
    const logBody = document.getElementById('backtestLogBody');
    logBody.innerHTML = '';

    const LOG_STAGE_STYLES = {
      "1단계: 평상시": "background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25);",
      "2-1단계: 위기 감지 (역전 정상화 대기)": "background: rgba(245, 158, 11, 0.12); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25);",
      "2-2단계: 위기 감지 (지표 악화)": "background: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.25);",
      "3단계: 폭락 진행": "background: rgba(185, 28, 28, 0.18); color: #f87171; border: 1px solid rgba(185, 28, 28, 0.35);",
      "4-1단계: 바닥 반등 1차": "background: rgba(6, 182, 212, 0.12); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.25);",
      "4-2단계: 바닥 반등 2차": "background: rgba(59, 130, 246, 0.12); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.25);"
    };

    const LOG_STAGE_BADGES = {
      "1단계: 평상시": "☀️ 평상시",
      "2-1단계: 위기 감지 (역전 정상화 대기)": "⛅ 위기 (역전대기)",
      "2-2단계: 위기 감지 (지표 악화)": "⛅ 위기 (지표악화)",
      "3단계: 폭락 진행": "⛈️ 폭락 진행",
      "4-1단계: 바닥 반등 1차": "🌅 바닥 1차",
      "4-2단계: 바닥 반등 2차": "🌅 바닥 2차"
    };

    if (tradeLogs.length === 0) {
      logBody.innerHTML = `<tr><td colspan="9" style="text-align:center;">국면 진단 내역이 존재하지 않습니다.</td></tr>`;
    } else {
      // Sort reverse to see latest at top
      [...tradeLogs].reverse().forEach(log => {
        const tr = document.createElement('tr');
        const badgeStyle = LOG_STAGE_STYLES[log.stage] || "background: rgba(255,255,255,0.05); color: var(--text-primary);";
        const badgeLabel = LOG_STAGE_BADGES[log.stage] || log.stage;

        tr.innerHTML = `
          <td>${log.date}</td>
          <td><span class="stage-badge" style="${badgeStyle}">${badgeLabel}</span></td>
          <td style="font-size: 0.8rem; color: var(--text-secondary); max-width: 220px; word-break: keep-all; font-weight: 500;">${log.triggerReason || '-'}</td>
          <td style="text-align:right;">${log.vix !== null ? log.vix.toFixed(2) : '-'}</td>
          <td style="text-align:right;">${log.yieldCurve !== null ? log.yieldCurve.toFixed(2) + '%' : '-'}</td>
          <td style="text-align:right;">${log.hy !== null ? log.hy.toFixed(2) + '%' : '-'}</td>
          <td style="text-align:right;">${log.unrate !== null ? log.unrate.toFixed(1) + '%' : '-'}</td>
          <td style="text-align:right; font-family:var(--font-display); font-size:0.85rem;">$${log.qqqPrice.toFixed(2)}</td>
          <td style="text-align:center;">${log.actionBadge || '-'}</td>
        `;
        logBody.appendChild(tr);
      });
    }

    // Render Stage Distribution UI
    const totalDays = timeline.length;
    const stageBar = document.getElementById('backtestStageBar');
    const stageGrid = document.getElementById('backtestStageGrid');
    
    stageBar.innerHTML = '';
    stageGrid.innerHTML = '';
    
    const STAGE_COLORS = {
      "1단계: 평상시": "#10b981",
      "2-1단계: 위기 감지 (역전 정상화 대기)": "#f59e0b",
      "2-2단계: 위기 감지 (지표 악화)": "#ef4444",
      "3단계: 폭락 진행": "#b91c1c",
      "4-1단계: 바닥 반등 1차": "#06b6d4",
      "4-2단계: 바닥 반등 2차": "#3b82f6"
    };
    
    const STAGE_BADGES = {
      "1단계: 평상시": "☀️ 1단계: 평상시",
      "2-1단계: 위기 감지 (역전 정상화 대기)": "⛅ 2-1단계: 위기 (역전)",
      "2-2단계: 위기 감지 (지표 악화)": "⛅ 2-2단계: 위기 (지표악화)",
      "3단계: 폭락 진행": "⛈️ 3단계: 폭락 진행",
      "4-1단계: 바닥 반등 1차": "🌅 4-1단계: 바닥 1차",
      "4-2단계: 바닥 반등 2차": "🌅 4-2단계: 바닥 2차"
    };

    const stagesList = [
      "1단계: 평상시",
      "2-1단계: 위기 감지 (역전 정상화 대기)",
      "2-2단계: 위기 감지 (지표 악화)",
      "3단계: 폭락 진행",
      "4-1단계: 바닥 반등 1차",
      "4-2단계: 바닥 반등 2차"
    ];

    stagesList.forEach(stg => {
      const count = stageCounts[stg] || 0;
      const pct = totalDays > 0 ? (count / totalDays) * 100 : 0;
      
      if (count > 0) {
        const seg = document.createElement('div');
        seg.style.width = `${pct}%`;
        seg.style.backgroundColor = STAGE_COLORS[stg];
        seg.style.height = '100%';
        seg.style.transition = 'width 0.5s ease';
        seg.title = `${stg}: ${count}일 (${pct.toFixed(1)}%)`;
        stageBar.appendChild(seg);
      }
      
      const card = document.createElement('div');
      card.style.display = 'flex';
      card.style.alignItems = 'center';
      card.style.justifyContent = 'space-between';
      card.style.padding = '0.75rem 1rem';
      card.style.borderRadius = '10px';
      card.style.border = '1px solid rgba(255,255,255,0.03)';
      card.style.backgroundColor = 'rgba(255,255,255,0.01)';
      card.style.borderLeft = `4px solid ${STAGE_COLORS[stg]}`;
      
      card.innerHTML = `
        <div>
          <div style="font-weight:600; font-size:0.88rem; color:var(--text-primary);">${STAGE_BADGES[stg]}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.15rem;">
            국면 설명: ${stg.split(': ')[1] || stg}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:700; font-family:var(--font-display); font-size:1.1rem; color:var(--text-primary);">${count}일</div>
          <div style="font-weight:500; font-size:0.75rem; color:var(--text-secondary);">${pct.toFixed(1)}%</div>
        </div>
      `;
      stageGrid.appendChild(card);
    });

    // Store logs globally for clipboard copy functionality
    latestTradeLogs = tradeLogs;

    // Render Chart
    renderPerformanceChart(dates, s1Values, s2Values, stages, triggerReasons, principal);

    // Display results section
    progressCard.style.display = 'none';
    resultsSection.style.display = 'block';
    showToast('백테스트 시뮬레이션 계산이 정상 완료되었습니다.', 'success');

  } catch (err) {
    console.error(err);
    progressCard.style.display = 'none';
    showToast('시뮬레이션 도중 오류가 발생했습니다: ' + err.message, 'error');
  }
}

function renderPerformanceChart(dates, s1, s2, stages, triggerReasons, principal) {
  const ctx = document.getElementById('backtestChart').getContext('2d');

  // Convert absolute values to returns (%)
  const s1Returns = s1.map(v => ((v - principal) / principal) * 100);
  const s2Returns = s2.map(v => ((v - principal) / principal) * 100);

  // Initialize controls
  const scrollbar = document.getElementById('chartScrollbar');
  const zoomSlider = document.getElementById('chartZoomSlider');
  const zoomValue = document.getElementById('chartZoomValue');
  const minDateLabel = document.getElementById('chartMinDateLabel');
  const maxDateLabel = document.getElementById('chartMaxDateLabel');

  const totalPoints = dates.length;

  function updateChartRange(startIndex, visibleCount) {
    if (!backtestChartInstance) return;
    const endIndex = Math.min(totalPoints - 1, startIndex + visibleCount - 1);
    
    backtestChartInstance.options.scales.x.min = startIndex;
    backtestChartInstance.options.scales.x.max = endIndex;
    backtestChartInstance.update('none');

    if (minDateLabel) minDateLabel.textContent = dates[startIndex] || '';
    if (maxDateLabel) maxDateLabel.textContent = dates[endIndex] || '';
  }

  function syncSliders(chartObj) {
    const activeChart = chartObj || backtestChartInstance;
    if (!activeChart) return;
    const x = activeChart.scales.x;
    if (!x) return;
    
    const minIdx = Math.max(0, Math.round(x.min));
    const maxIdx = Math.min(totalPoints - 1, Math.round(x.max));
    
    const visibleCount = maxIdx - minIdx + 1;
    const zoomPercent = Math.max(5, Math.min(100, Math.round((visibleCount / totalPoints) * 100)));
    
    if (zoomSlider) zoomSlider.value = zoomPercent;
    if (zoomValue) zoomValue.textContent = zoomPercent + '%';
    if (scrollbar) {
      scrollbar.max = totalPoints - visibleCount;
      scrollbar.value = minIdx;
    }
    if (minDateLabel) minDateLabel.textContent = dates[minIdx] || '';
    if (maxDateLabel) maxDateLabel.textContent = dates[maxIdx] || '';
  }

  if (scrollbar && zoomSlider && zoomValue && minDateLabel && maxDateLabel) {
    zoomSlider.value = 100;
    zoomValue.textContent = '100%';
    scrollbar.min = 0;
    scrollbar.max = 0;
    scrollbar.value = 0;
    minDateLabel.textContent = dates[0] || '-----';
    maxDateLabel.textContent = dates[totalPoints - 1] || '-----';

    zoomSlider.oninput = function() {
      const zoomPercent = parseInt(zoomSlider.value, 10);
      zoomValue.textContent = zoomPercent + '%';
      if (!backtestChartInstance) return;
      const visibleCount = Math.min(totalPoints, Math.max(5, Math.round((zoomPercent / 100) * totalPoints)));
      let startIndex = parseInt(scrollbar.value, 10);
      if (startIndex + visibleCount > totalPoints) {
        startIndex = totalPoints - visibleCount;
      }
      startIndex = Math.max(0, startIndex);
      scrollbar.max = totalPoints - visibleCount;
      scrollbar.value = startIndex;
      updateChartRange(startIndex, visibleCount);
    };

    scrollbar.oninput = function() {
      if (!backtestChartInstance) return;
      const startIndex = parseInt(scrollbar.value, 10);
      const zoomPercent = parseInt(zoomSlider.value, 10);
      const visibleCount = Math.min(totalPoints, Math.max(5, Math.round((zoomPercent / 100) * totalPoints)));
      updateChartRange(startIndex, visibleCount);
    };
  }

  if (backtestChartInstance) {
    backtestChartInstance.destroy();
  }

  // Chart.js plugin to draw vertical bands behind lines according to stage
  const stageBackgroundPlugin = {
    id: 'stageBackgrounds',
    beforeDraw: (chart) => {
      const { ctx, chartArea, scales } = chart;
      const xScale = scales.x;
      const yScale = scales.y;
      if (!xScale || !yScale || !chartArea) return;

      const chartStages = chart.config.data.stages;
      if (!chartStages || chartStages.length === 0) return;

      const STAGE_BG_COLORS = {
        "1단계: 평상시": "rgba(16, 185, 129, 0.18)",
        "2-1단계: 위기 감지 (역전 정상화 대기)": "rgba(245, 158, 11, 0.25)",
        "2-2단계: 위기 감지 (지표 악화)": "rgba(239, 68, 68, 0.25)",
        "3단계: 폭락 진행": "rgba(185, 28, 28, 0.38)",
        "4-1단계: 바닥 반등 1차": "rgba(6, 182, 212, 0.25)",
        "4-2단계: 바닥 반등 2차": "rgba(59, 130, 246, 0.25)"
      };

      const count = chartStages.length;
      const meta = chart.getDatasetMeta(0);
      if (!meta || !meta.data || meta.data.length === 0) return;

      ctx.save();
      // Clip drawing area to chartArea so background bands don't overflow when zoomed/panned
      ctx.beginPath();
      ctx.rect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);
      ctx.clip();

      for (let i = 0; i < count; i++) {
        if (!meta.data[i]) continue;
        const currentX = meta.data[i].x;
        let nextX;
        if (i < count - 1 && meta.data[i + 1]) {
          nextX = meta.data[i + 1].x;
        } else {
          const prevX = (i > 0 && meta.data[i - 1]) ? meta.data[i - 1].x : currentX;
          nextX = currentX + (currentX - prevX);
        }

        const stage = chartStages[i];
        const color = STAGE_BG_COLORS[stage] || "transparent";
        
        ctx.fillStyle = color;
        ctx.fillRect(
          currentX,
          chartArea.top,
          nextX - currentX + 0.5,
          chartArea.bottom - chartArea.top
        );

        // Draw thin division line when the stage changes on the next point
        if (i < count - 1 && chartStages[i + 1] !== stage && meta.data[i + 1]) {
          ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(nextX, chartArea.top);
          ctx.lineTo(nextX, chartArea.bottom);
          ctx.stroke();
        }
      }
      ctx.restore();
    }
  };

  backtestChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      stages: stages,
      triggerReasons: triggerReasons,
      datasets: [
        {
          label: '나스닥 100% 매수보유 (QQQ)',
          data: s1Returns,
          borderColor: '#f97316',
          borderWidth: 2.0,
          pointRadius: 0,
          fill: false
        },
        {
          label: '나침반 신호매매 전략 (Active)',
          data: s2Returns,
          borderColor: '#06b6d4',
          borderWidth: 2.5,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    plugins: [stageBackgroundPlugin],
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          labels: {
            color: '#f9fafb',
            font: {
              family: 'Outfit'
            }
          }
        },
        tooltip: {
          backgroundColor: '#111827',
          borderColor: 'rgba(255,255,255,0.08)',
          borderWidth: 1,
          titleColor: '#f9fafb',
          bodyColor: '#f9fafb',
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
            },
            afterBody: function(context) {
              const dataIndex = context[0].dataIndex;
              const chartStages = context[0].chart.config.data.stages;
              const chartReasons = context[0].chart.config.data.triggerReasons;
              if (!chartStages || !chartStages[dataIndex]) return '';
              
              const stage = chartStages[dataIndex];
              const reason = chartReasons ? chartReasons[dataIndex] : '';
              
              const STAGE_EXPLANATIONS = {
                "1단계: 평상시": "☀️ 1단계 (평상시): VIX 및 거시 지표가 안정적인 온전한 성장기",
                "2-1단계: 위기 감지 (역전 정상화 대기)": "⛅ 2-1단계 (위기 대기): 1년 내 장단기 금리차 역전 발생으로 잠재 위기 상태",
                "2-2단계: 위기 감지 (지표 악화)": "⛅ 2-2단계 (지표 악화): VIX 경고치 진입 또는 실업률이 전월 대비 상승",
                "3단계: 폭락 진행": "⛈️ 3단계 (폭락 진행): VIX 30 이상 폭락 진행 또는 회사채 하이일드 스프레드 급등",
                "4-1단계: 바닥 반등 1차": "🌅 4-1단계 (바닥 반등): 변동성 극대화(VIX 35 이상) 이후 하락 반전으로 바닥 확인 시점",
                "4-2단계: 바닥 반등 2차": "🌅 4-2단계 (바닥 반등): 회사채 신용 위험(신용 스프레드)이 안정세로 진입하는 시점"
              };
              
              let text = '\n[시장 국면]\n' + (STAGE_EXPLANATIONS[stage] || stage);
              if (reason) {
                text += '\n진단 근거: ' + reason;
              }
              return text;
            }
          }
        },
        zoom: {
          pan: {
            enabled: true,
            mode: 'x',
            modifierKey: null,
            onPan: function({chart}) {
              syncSliders(chart);
            }
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.08
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            onZoom: function({chart}) {
              syncSliders(chart);
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255,255,255,0.02)'
          },
          ticks: {
            color: '#9ca3af',
            maxTicksLimit: 12,
            font: {
              family: 'Outfit'
            }
          }
        },
        y: {
          grid: {
            color: 'rgba(255,255,255,0.05)'
          },
          ticks: {
            color: '#9ca3af',
            callback: function(value) {
              return value.toFixed(0) + '%';
            },
            font: {
              family: 'Outfit'
            }
          }
        }
      }
    }
  });
}

function resetChartZoom() {
  if (backtestChartInstance) {
    backtestChartInstance.resetZoom();
    
    // Manually update sliders to 100% zoom and start index 0
    const scrollbar = document.getElementById('chartScrollbar');
    const zoomSlider = document.getElementById('chartZoomSlider');
    const zoomValue = document.getElementById('chartZoomValue');
    const minDateLabel = document.getElementById('chartMinDateLabel');
    const maxDateLabel = document.getElementById('chartMaxDateLabel');
    const dates = backtestChartInstance.data.labels;
    
    if (scrollbar && zoomSlider && zoomValue && minDateLabel && maxDateLabel && dates) {
      zoomSlider.value = 100;
      zoomValue.textContent = '100%';
      scrollbar.max = 0;
      scrollbar.value = 0;
      minDateLabel.textContent = dates[0] || '-----';
      maxDateLabel.textContent = dates[dates.length - 1] || '-----';
    }
  }
}

function copyTradeLogsToClipboard() {
  if (!latestTradeLogs || latestTradeLogs.length === 0) {
    showToast('복사할 기록이 없습니다.', 'warning');
    return;
  }
  
  const headers = ['날짜', '시장 상태 (Stage)', '진단 근거 / 임계값', 'VIX', '금리차', '하이일드', '실업률', 'QQQ 가격', '추천 액션'];
  let text = headers.join('\t') + '\n';
  
  const sortedLogs = [...latestTradeLogs].reverse();
  sortedLogs.forEach(log => {
    const row = [
      log.date,
      log.stage,
      log.triggerReason || '',
      log.vix !== null ? log.vix.toFixed(2) : '',
      log.yieldCurve !== null ? log.yieldCurve.toFixed(2) + '%' : '',
      log.hy !== null ? log.hy.toFixed(2) + '%' : '',
      log.unrate !== null ? log.unrate.toFixed(1) + '%' : '',
      `$${log.qqqPrice.toFixed(2)}`,
      log.actionText || ''
    ];
    text += row.join('\t') + '\n';
  });
  
  const tempTextArea = document.createElement('textarea');
  tempTextArea.value = text;
  document.body.appendChild(tempTextArea);
  tempTextArea.select();
  try {
    document.execCommand('copy');
    showToast('클립보드에 복사되었습니다.', 'success');
  } catch (err) {
    console.error('클립보드 복사 실패:', err);
    showToast('복사에 실패했습니다.', 'error');
  }
  document.body.removeChild(tempTextArea);
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
  const today = new Date();
  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(today.getFullYear() - 5);
  
  const startInput = document.getElementById('backtestStartDate');
  const endInput = document.getElementById('backtestEndDate');
  
  if (startInput && !startInput.value) {
    startInput.value = fiveYearsAgo.toISOString().split('T')[0];
  }
  if (endInput && !endInput.value) {
    endInput.value = today.toISOString().split('T')[0];
  }
  
  // Show warnings/guidelines for file protocol if needed
  if (window.location.protocol === 'file:') {
    showToast('외부 지표와 시세 조회는 로컬 서버로 열 때 가장 안정적입니다. start-server.bat을 실행한 뒤 표시되는 주소로 접속해 주세요.', 'warning');
  }
});
