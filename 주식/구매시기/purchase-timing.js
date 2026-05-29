const CORS_PROXIES = [
  url => `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`,
  url => `https://thingproxy.freeboard.io/fetch/${url}`,
  url => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`
];

let timingChart = null;

function getProxyUrls(url) {
  const urls = [];
  const isLocalHttp = ["localhost", "127.0.0.1"].includes(window.location.hostname);
  if (isLocalHttp) {
    urls.push(`${window.location.origin}/proxy?url=${encodeURIComponent(url)}`);
  }
  urls.push(...CORS_PROXIES.map(proxyFn => proxyFn(url)));
  return urls;
}

async function fetchWithTimeout(url, timeoutMs = 12000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function fetchJsonWithProxy(url) {
  let lastError = null;
  for (const proxyUrl of getProxyUrls(url)) {
    try {
      const res = await fetchWithTimeout(proxyUrl);
      if (!res.ok) {
        lastError = new Error(`HTTP ${res.status}`);
        continue;
      }
      const text = await res.text();
      if (text.trim().startsWith("<")) {
        throw new Error("Invalid HTML response");
      }
      return JSON.parse(text);
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError || new Error("데이터 조회 실패");
}

function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  const icon = document.getElementById("toastIcon");
  const msg = document.getElementById("toastMessage");
  if (!toast || !icon || !msg) return;
  msg.innerText = message;
  icon.innerText = type === "success" ? "✅" : type === "error" ? "❌" : type === "warning" ? "⚠️" : "ℹ️";
  toast.classList.add("active");
  setTimeout(() => toast.classList.remove("active"), 3200);
}

function formatMoney(value) {
  return new Intl.NumberFormat("ko-KR").format(Math.round(value)) + "원";
}

function updateProgress(text, pct) {
  document.getElementById("progressText").innerText = text;
  document.getElementById("progressBar").style.width = `${pct}%`;
}

function calcSma(history, index, period) {
  let sum = 0;
  let count = 0;
  for (let i = index; i >= 0 && count < period; i--) {
    const close = history[i].close;
    if (typeof close === "number") {
      sum += close;
      count++;
    }
  }
  return count > 0 ? sum / count : history[index].close;
}

function calcDrawdown(history, index, windowSize = 252) {
  let peak = history[index].close;
  for (let i = index; i >= 0 && index - i < windowSize; i--) {
    if (history[i].close > peak) peak = history[i].close;
  }
  return peak > 0 ? ((history[index].close - peak) / peak) * 100 : 0;
}

async function loadYahooHistory(ticker, startDate, endDate) {
  const p1 = Math.floor(startDate.getTime() / 1000);
  const p2 = Math.floor(endDate.getTime() / 1000);
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?period1=${p1}&period2=${p2}&interval=1d`;
  const data = await fetchJsonWithProxy(url);
  if (!data?.chart?.result?.[0]) {
    throw new Error("Yahoo Finance 응답 오류");
  }
  const result = data.chart.result[0];
  const ts = result.timestamp || [];
  const closes = result.indicators?.quote?.[0]?.close || [];
  const out = [];
  for (let i = 0; i < ts.length; i++) {
    if (closes[i] === null || closes[i] === undefined || Number.isNaN(closes[i])) continue;
    out.push({
      date: new Date(ts[i] * 1000).toISOString().split("T")[0],
      close: parseFloat(closes[i].toFixed(4))
    });
  }
  return out;
}

function isFirstTradingDayOfMonth(history, index) {
  if (index === 0) return true;
  const d = new Date(history[index].date);
  const prev = new Date(history[index - 1].date);
  return d.getFullYear() !== prev.getFullYear() || d.getMonth() !== prev.getMonth();
}

function computeMetrics(values, totalInvested, years) {
  const finalValue = values[values.length - 1] || 0;
  const totalReturn = totalInvested > 0 ? ((finalValue - totalInvested) / totalInvested) * 100 : 0;
  const cagr = totalInvested > 0 && years > 0 ? (Math.pow(finalValue / totalInvested, 1 / years) - 1) * 100 : 0;
  let peak = -Infinity;
  let maxDrawdown = 0;
  for (const v of values) {
    if (v > peak) peak = v;
    const dd = peak > 0 ? ((v - peak) / peak) * 100 : 0;
    if (dd < maxDrawdown) maxDrawdown = dd;
  }
  return { finalValue, totalReturn, cagr, maxDrawdown };
}

function renderKpis(results) {
  const grid = document.getElementById("kpiGrid");
  grid.innerHTML = "";

  const cards = [
    {
      title: "매월 정기매수 (DCA) 최종 평가금",
      value: formatMoney(results.dca.metrics.finalValue * results.fx),
      desc: `누적수익률 ${results.dca.metrics.totalReturn.toFixed(2)}% | CAGR ${results.dca.metrics.cagr.toFixed(2)}% | MDD ${results.dca.metrics.maxDrawdown.toFixed(2)}%`
    },
    {
      title: "신호 매수 최종 평가금",
      value: formatMoney(results.signal.metrics.finalValue * results.fx),
      desc: `누적수익률 ${results.signal.metrics.totalReturn.toFixed(2)}% | CAGR ${results.signal.metrics.cagr.toFixed(2)}% | MDD ${results.signal.metrics.maxDrawdown.toFixed(2)}%`
    },
    {
      title: "최종 성과 차이 (신호 - DCA)",
      value: formatMoney((results.signal.metrics.finalValue - results.dca.metrics.finalValue) * results.fx),
      desc: "양수면 신호 매수가 우위, 음수면 정기매수가 우위"
    }
  ];

  cards.forEach(card => {
    const div = document.createElement("div");
    div.className = "kpi-card";
    div.innerHTML = `
      <div class="kpi-title">${card.title}</div>
      <div class="kpi-value">${card.value}</div>
      <div class="kpi-desc">${card.desc}</div>
    `;
    grid.appendChild(div);
  });
}

function renderChart(results) {
  const ctx = document.getElementById("timingChart").getContext("2d");
  if (timingChart) timingChart.destroy();

  const principal = results.totalInvested;
  const dcaReturns = results.dca.values.map(v => ((v - principal) / principal) * 100);
  const signalReturns = results.signal.values.map(v => ((v - principal) / principal) * 100);

  timingChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: results.dates,
      datasets: [
        { label: "정기매수(DCA)", data: dcaReturns, borderColor: "#3b82f6", borderWidth: 2, pointRadius: 0 },
        { label: "신호매수", data: signalReturns, borderColor: "#10b981", borderWidth: 2, pointRadius: 0 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: "#f9fafb" } },
        tooltip: {
          callbacks: {
            label: (ctx2) => `${ctx2.dataset.label}: ${ctx2.parsed.y.toFixed(2)}%`
          }
        }
      },
      scales: {
        x: { ticks: { color: "#9ca3af", maxTicksLimit: 10 }, grid: { color: "rgba(255,255,255,0.03)" } },
        y: {
          ticks: { color: "#9ca3af", callback: value => `${Number(value).toFixed(0)}%` },
          grid: { color: "rgba(255,255,255,0.05)" }
        }
      }
    }
  });
}

function renderLogs(logs) {
  const body = document.getElementById("logTableBody");
  body.innerHTML = "";
  if (logs.length === 0) {
    body.innerHTML = '<tr><td colspan="6" style="text-align:center;">매수 이벤트가 없습니다.</td></tr>';
    return;
  }

  [...logs].reverse().forEach(log => {
    const tr = document.createElement("tr");
    const strategyBadge = log.strategy === "DCA"
      ? '<span class="event-badge dca">DCA</span>'
      : '<span class="event-badge signal">Signal</span>';

    tr.innerHTML = `
      <td>${log.date}</td>
      <td>${strategyBadge}</td>
      <td>${log.reason}</td>
      <td style="text-align:right;">${log.price.toFixed(2)}</td>
      <td style="text-align:right;">${log.shares.toFixed(4)}</td>
      <td style="text-align:right;">${log.notional.toFixed(2)}</td>
    `;
    body.appendChild(tr);
  });
}

async function runPurchaseTimingBacktest() {
  const ticker = (document.getElementById("tickerInput").value || "").trim().toUpperCase();
  const startStr = document.getElementById("startDateInput").value;
  const endStr = document.getElementById("endDateInput").value;
  const initialCapital = parseFloat(document.getElementById("initialCapitalInput").value) || 0;
  const monthlyContribution = parseFloat(document.getElementById("monthlyContributionInput").value) || 0;
  const feeRate = (parseFloat(document.getElementById("feeInput").value) || 0) / 100;
  const maPeriod = parseInt(document.getElementById("maPeriodInput").value, 10) || 200;
  const drawdownEnabled = document.getElementById("drawdownBuyToggle").checked;
  const drawdownThreshold = Math.abs(parseFloat(document.getElementById("drawdownThresholdInput").value) || 15);

  if (!ticker || !startStr || !endStr) {
    showToast("티커와 기간을 입력하세요.", "warning");
    return;
  }
  if (initialCapital <= 0) {
    showToast("초기 자금은 0보다 커야 합니다.", "warning");
    return;
  }

  const startDate = new Date(startStr);
  const endDate = new Date(endStr);
  if (startDate >= endDate) {
    showToast("시작일은 종료일보다 이전이어야 합니다.", "warning");
    return;
  }

  document.getElementById("progressCard").style.display = "block";
  document.getElementById("resultsSection").style.display = "none";
  updateProgress("시세 데이터 다운로드 중...", 15);

  try {
    const queryStart = new Date(startDate);
    queryStart.setFullYear(queryStart.getFullYear() - 1);
    const history = await loadYahooHistory(ticker, queryStart, endDate);
    updateProgress("백테스트 계산 중...", 65);

    const startIndex = history.findIndex(item => new Date(item.date) >= startDate);
    if (startIndex === -1) throw new Error("선택 기간 데이터가 없습니다.");

    let dcaShares = 0;
    let dcaCash = 0;
    let signalShares = 0;
    let signalCash = initialCapital;
    const dates = [];
    const dcaValues = [];
    const signalValues = [];
    const logs = [];
    let totalInvested = initialCapital;

    for (let i = startIndex; i < history.length; i++) {
      const price = history[i].close;
      const dateStr = history[i].date;

      if (i === startIndex) {
        const investable = initialCapital * (1 - feeRate);
        const shares = investable / price;
        dcaShares += shares;
        logs.push({ date: dateStr, strategy: "DCA", reason: "초기 매수", price, shares, notional: investable });
      }

      const firstTradingDay = isFirstTradingDayOfMonth(history, i);
      if (firstTradingDay && i > startIndex) {
        totalInvested += monthlyContribution;
        dcaCash += monthlyContribution;
        signalCash += monthlyContribution;

        if (dcaCash > 0) {
          const investable = dcaCash * (1 - feeRate);
          const shares = investable / price;
          dcaShares += shares;
          logs.push({ date: dateStr, strategy: "DCA", reason: "월 자동이체 매수", price, shares, notional: investable });
          dcaCash = 0;
        }
      }

      const sma = calcSma(history, i, maPeriod);
      const drawdown = calcDrawdown(history, i, 252);
      const maSignal = price > sma;
      const drawdownSignal = drawdownEnabled && drawdown <= -drawdownThreshold;

      if (signalCash > 0 && (maSignal || drawdownSignal)) {
        const investable = signalCash * (1 - feeRate);
        const shares = investable / price;
        signalShares += shares;
        logs.push({
          date: dateStr,
          strategy: "Signal",
          reason: maSignal ? `가격 > ${maPeriod}일선` : `고점대비 ${drawdown.toFixed(1)}% 하락`,
          price,
          shares,
          notional: investable
        });
        signalCash = 0;
      }

      dates.push(dateStr);
      dcaValues.push(dcaShares * price + dcaCash);
      signalValues.push(signalShares * price + signalCash);
    }

    const years = dates.length / 252;
    const dcaMetrics = computeMetrics(dcaValues, totalInvested, years);
    const signalMetrics = computeMetrics(signalValues, totalInvested, years);

    const results = {
      dates,
      totalInvested,
      dca: { values: dcaValues, metrics: dcaMetrics },
      signal: { values: signalValues, metrics: signalMetrics },
      logs,
      fx: 1
    };

    updateProgress("결과 렌더링 중...", 95);
    renderKpis(results);
    renderChart(results);
    renderLogs(logs);

    document.getElementById("progressCard").style.display = "none";
    document.getElementById("resultsSection").style.display = "block";
    showToast("구매시기 백테스트 완료", "success");
  } catch (err) {
    console.error(err);
    document.getElementById("progressCard").style.display = "none";
    showToast(`실행 중 오류: ${err.message}`, "error");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const today = new Date();
  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(today.getFullYear() - 5);
  document.getElementById("startDateInput").value = fiveYearsAgo.toISOString().split("T")[0];
  document.getElementById("endDateInput").value = today.toISOString().split("T")[0];
  if (window.location.protocol === "file:") {
    showToast("로컬 서버 실행 시 데이터 조회가 더 안정적입니다.", "warning");
  }
});
