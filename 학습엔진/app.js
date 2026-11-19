const KEY = "roadmap-year-v3";
const LEGACY = "roadmap-year-v1";
const PREV = "roadmap-year-v2";
const BASE_TITLE = document.title;
const E = window.RoadmapEngine;

let DATA = { tracks: [] };
let state = null;
let indexFilter = "all";
let indexLimit = 200;
let remoteSyncEnabled = false;
let remoteTimer = 0;
let remoteDirty = false;
let audioCtx = null;

function todayISO() { return E.fmt(new Date()); }
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function trackById(id) { return DATA.tracks.find((t) => t.id === id); }
function isPlainObj(v) { return !!v && typeof v === "object" && !Array.isArray(v); }
function softOf(tr) {
  if (tr.soft) return tr.soft;
  const hex = String(tr.color || "").replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(hex)) return "#efe8d8";
  const mix = (c) => Math.round(c + (255 - c) * 0.82).toString(16).padStart(2, "0");
  return "#" + mix(parseInt(hex.slice(0, 2), 16)) + mix(parseInt(hex.slice(2, 4), 16)) + mix(parseInt(hex.slice(4, 6), 16));
}

function snapshot() {
  return {
    v: 3,
    start: state.start,
    starts: state.starts || {},
    done: state.done,
    pass: state.pass,
    skip: state.skip,
    why: state.why,
    stuck: state.stuck,
    cards: state.cards,
    activity: state.activity,
    deferred: state.deferred,
    reviewed: state.reviewed || {},
    track: state.track,
    week: state.week,
    view: state.view,
    q: state.q || "",
    iq: state.iq || "",
    updatedAt: state.updatedAt || 0
  };
}

function sendRemote(body, immediate) {
  if (!remoteSyncEnabled || location.protocol === "file:") return;
  remoteDirty = true;
  const run = () => {
    remoteTimer = 0;
    fetch("/api/state", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body || JSON.stringify(snapshot()),
      keepalive: true
    }).then((res) => {
      if (res && res.ok) remoteDirty = false;
    }).catch(() => {});
  };
  clearTimeout(remoteTimer);
  if (immediate) run();
  else remoteTimer = setTimeout(run, 150);
}

function persist(markDataChange) {
  if (markDataChange) remoteSyncEnabled = true;
  state.updatedAt = Date.now();
  const payload = JSON.stringify(snapshot());
  try {
    localStorage.setItem(KEY, payload);
  } catch (e) {
    console.warn("localStorage 저장 실패", e);
  }
  if (remoteSyncEnabled) sendRemote(payload, false);
}

window.addEventListener("pagehide", () => {
  if (remoteDirty && state) sendRemote(JSON.stringify(snapshot()), true);
});

function normalize(saved) {
  const s = E.blankState(E.isValidISO(saved.start) ? saved.start : todayISO());
  ["starts", "done", "pass", "skip", "why", "stuck", "cards", "activity", "deferred", "reviewed"].forEach((k) => {
    if (isPlainObj(saved[k])) s[k] = saved[k];
  });
  const cleanCards = {};
  Object.keys(s.cards).forEach((id) => {
    const c = s.cards[id];
    if (!isPlainObj(c) || !c.track || !Number.isInteger(c.week) || c.week < 1) return;
    const step = Number.isInteger(c.step) && c.step >= 0 ? Math.min(c.step, E.INTERVALS.length - 1) : (c.kind === "week" ? 1 : 0);
    const due = c.retired ? null : (E.isValidISO(c.due) ? c.due : todayISO());
    const ease = (typeof c.ease === "number" && isFinite(c.ease)) ? Math.max(1.3, Math.min(2.6, +c.ease.toFixed(2))) : 2.0;
    const lapses = Number.isInteger(c.lapses) && c.lapses >= 0 ? c.lapses : 0;
    const reviews = Number.isInteger(c.reviews) && c.reviews >= 0 ? c.reviews : 0;
    const leech = !!c.leech;
    const lastQuality = typeof c.lastQuality === "string" ? c.lastQuality : "";
    cleanCards[id] = Object.assign({}, c, {
      id: c.id || id,
      step: step,
      due: due,
      ease: ease,
      lapses: lapses,
      reviews: reviews,
      leech: leech,
      lastQuality: lastQuality
    });
  });
  s.cards = cleanCards;
  if (saved.track) s.track = saved.track;
  if (saved.week) s.week = saved.week;
  if (saved.view) s.view = saved.view;
  s.q = typeof saved.q === "string" ? saved.q : "";
  s.iq = typeof saved.iq === "string" ? saved.iq : "";
  s.updatedAt = typeof saved.updatedAt === "number" && isFinite(saved.updatedAt) && saved.updatedAt >= 0 ? saved.updatedAt : 0;
  return s;
}

function freshFrom(saved) {
  const start = saved && E.isValidISO(saved.start) ? saved.start : todayISO();
  return E.blankState(start);
}

function stateFromSaved(saved) {
  if (!isPlainObj(saved)) return E.blankState(todayISO());
  if (saved.v === 3) return normalize(saved);
  if (isPlainObj(saved.done) || isPlainObj(saved.pass)) return E.migrateV1(saved, todayISO());
  return freshFrom(saved);
}

function clampState(s) {
  if (!E.isValidISO(s.start)) s.start = todayISO();
  const validTracks = new Set(DATA.tracks.map((t) => t.id));
  const cleanStarts = {};
  Object.keys(s.starts || {}).forEach((k) => {
    if (validTracks.has(k) && E.isValidISO(s.starts[k])) cleanStarts[k] = s.starts[k];
  });
  s.starts = cleanStarts;
  const cleanReviewed = {};
  const today = todayISO();
  Object.keys(s.reviewed || {}).forEach((k) => {
    if (!validTracks.has(k)) return;
    const rev = s.reviewed[k];
    if (rev === today) cleanReviewed[k] = today;
    else if (isPlainObj(rev) && rev.date === today) {
      cleanReviewed[k] = { date: today, session: typeof rev.session === "string" ? rev.session : "" };
    }
  });
  s.reviewed = cleanReviewed;
  if (!trackById(s.track)) s.track = DATA.tracks[0].id;
  const max = trackById(s.track).weeks.length;
  const w = Number(s.week);
  s.week = Number.isInteger(w) && w >= 1 && w <= max ? w : 1;
  if (s.view !== "home" && s.view !== "track" && s.view !== "index") s.view = "home";
  return s;
}

function loadLocalRaw() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (isPlainObj(parsed)) return { state: stateFromSaved(parsed), existed: true };
    }
  } catch (err) { /* 새 기록 */ }
  for (const oldKey of [PREV, LEGACY]) {
    try {
      const old = localStorage.getItem(oldKey);
      if (old) {
        const parsed = JSON.parse(old);
        if (isPlainObj(parsed)) return { state: stateFromSaved(parsed), existed: true };
      }
    } catch (err) { /* 이전 기록 없음 */ }
  }
  return { state: null, existed: false };
}

async function fetchRemoteState() {
  if (location.protocol === "file:") return null;
  try {
    const res = await fetch("/api/state", { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    if (data && data.exists && isPlainObj(data.state) && data.state.v === 3) {
      return normalize(data.state);
    }
  } catch (err) { /* 정적 HTTP 서버 폴백 */ }
  return null;
}

function stateScore(s) {
  if (!s) return 0;
  const len = (o) => (isPlainObj(o) ? Object.keys(o).length : 0);
  return len(s.done) * 10 + len(s.pass) * 5 + len(s.cards) + len(s.starts) * 2;
}

function pickInitialState(local, remote) {
  if (local && remote) {
    if (remote.updatedAt > local.updatedAt) return { chosen: remote, source: "remote" };
    if (local.updatedAt > remote.updatedAt) return { chosen: local, source: "local" };
    if (stateScore(remote) > stateScore(local)) return { chosen: remote, source: "remote" };
    return { chosen: local, source: "local" };
  }
  if (remote) return { chosen: remote, source: "remote" };
  if (local) return { chosen: local, source: "local" };
  return { chosen: E.blankState(todayISO()), source: "fresh" };
}

function needsRecord(tr) { return tr.confirm === "record"; }
function weekDoneCount(tr, week) {
  const n = tr.weeks[week - 1].days.length;
  let c = 0;
  for (let d = 0; d < n; d++) if (state.done[E.sessionId(tr.id, week, d)]) c += 1;
  return c;
}
function unitForWeek(tr, weekNo) {
  const units = Array.isArray(tr && tr.units) ? tr.units : [];
  for (let i = 0; i < units.length; i++) {
    if (weekNo >= units[i].start && weekNo <= units[i].end) {
      return { unit: units[i], index: i };
    }
  }
  return null;
}
function unitOfPhase(tr, phaseIdx) {
  const units = Array.isArray(tr && tr.units) ? tr.units : [];
  for (let i = 0; i < units.length; i++) {
    const pis = units[i].phases || [];
    if (pis.indexOf(phaseIdx) !== -1) return { unit: units[i], index: i };
  }
  return null;
}
function phaseMapButtonHTML(tr, p) {
  return "<button type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + p.start + "\"><em style=\"color:" + esc(tr.color) + "\">" + esc(p.from) + " → " + esc(p.to) + "</em><strong>" + esc(p.name) + "</strong><small>" + p.start + "–" + p.end + "주 · " + esc(p.result) + "</small></button>";
}
function summary() {
  const hours = DATA.tracks.map((tr) => E.trackDayCount(tr));
  const weeks = DATA.tracks.map((tr) => tr.weeks.length);
  const phases = DATA.tracks.map((tr) => tr.phases.length);
  const same = (arr) => arr.every((n) => n === arr[0]);
  const durationText = DATA.tracks.map((tr) => {
    const years = tr.weeks.length / 52;
    return tr.name + " " + (Number.isInteger(years) ? years + "년" : tr.weeks.length + "주");
  }).join(", ");
  return {
    hours: same(hours) ? String(hours[0]) : "트랙별",
    hoursSub: same(hours) ? "도메인당 시간" : DATA.tracks.map((tr, i) => tr.name + " " + hours[i]).join(" · "),
    parallel: String(DATA.tracks.length),
    weeks: same(weeks) ? String(weeks[0]) : "트랙별",
    weeksSub: same(phases) ? "주 · " + phases[0] + "단계" : "주 · 단계",
    sessions: hours.reduce((a, b) => a + b, 0),
    samePhases: same(phases),
    durationText: durationText
  };
}
function startFor(tr) { return E.trackStart(state, tr.id); }
function offsetToday(tr) {
  if (tr) return E.offsetOf(startFor(tr), todayISO());
  return E.offsetOf(state.start, todayISO());
}
function studyFor(tr) { return E.studyPos(tr, offsetToday(tr), state); }
function prepareQueues() {
  const today = todayISO();
  const cutoff = E.addDaysISO(today, -7);
  let changed = false;
  Object.keys(state.deferred || {}).forEach((k) => {
    const idx = k.indexOf(":");
    const dayStr = idx >= 0 ? k.slice(idx + 1) : "";
    if (E.isValidISO(dayStr) && dayStr < cutoff) {
      delete state.deferred[k];
      changed = true;
    }
  });
  Object.keys(state.reviewed || {}).forEach((k) => {
    const rev = state.reviewed[k];
    const revDate = isPlainObj(rev) ? rev.date : rev;
    if (revDate !== today) {
      delete state.reviewed[k];
      changed = true;
    }
  });
  DATA.tracks.forEach((tr) => {
    const key = tr.id + ":" + today;
    const q = E.takeQueue(E.dueCards(state, tr.id, today));
    if (!q.defer.length) {
      if (state.deferred[key] == null) {
        state.deferred[key] = 0;
        changed = true;
      }
      return;
    }
    E.deferCards(q.defer, today);
    state.deferred[key] = (state.deferred[key] || 0) + q.defer.length;
    changed = true;
  });
  if (changed) persist(false);
}
function shownReviews(tr) { return E.takeQueue(E.dueCards(state, tr.id, todayISO())).shown; }
function reviewCount() { return DATA.tracks.reduce((n, tr) => n + shownReviews(tr).length, 0); }
function distinctIdeas(week) {
  const goal = String(week.goal || "").trim();
  return (week.ideas || []).filter((it) => String(it[1] || "").trim() !== goal);
}

function captureDrafts() {
  if (!state) return;
  document.querySelectorAll(".done-box").forEach((box) => {
    const why = box.querySelector("[data-field='why']");
    const line = box.querySelector("[data-field='line']");
    const stuck = box.querySelector("[data-field='stuck']");
    const record = box.querySelector("[data-field='record']");
    state.drafts[box.dataset.session] = {
      why: why ? why.value : "",
      line: line ? line.value : "",
      stuck: !!(stuck && stuck.checked),
      record: !!(record && record.checked)
    };
  });
}
function draftOf(id) {
  return state.drafts[id] || { why: "", line: "", stuck: false, record: false };
}

function reviewCardHTML(card, tr) {
  const week = tr.weeks[card.week - 1];
  if (!week) return "";
  const phase = card.phase || "prompt";
  const revealed = phase === "reveal" || phase === "retryReveal";
  const retry = phase === "retry" || phase === "retryReveal";
  const dayObj = card.kind === "day" ? week.days[card.day] : null;
  const head = card.kind === "week"
    ? card.week + "주 · " + week.title
    : card.week + "주 " + (card.day + 1) + "일차 · " + ((dayObj && dayObj.title) || "");
  const cue = card.kind === "week" ? week.check : (card.line || "");
  const reviews = Number.isInteger(card.reviews) ? card.reviews : 0;
  const ease = typeof card.ease === "number" && isFinite(card.ease) ? card.ease : 2.0;
  const meta = "복습 " + reviews + "회 · 간격 배율 " + (ease / 2).toFixed(2) + "x";
  const leechHTML = card.leech
    ? "<p class=\"leech-warn\">반복 막힘(Leech): 4회 이상 막힌 항목입니다. 개념을 더 작은 단위나 반례 1개로 쪼개 정리해 보세요.</p>"
    : "";
  let answer = "";
  if (revealed && card.kind === "week") {
    const ideaItems = distinctIdeas(week).slice(0, 3).map((it) => "<li><b>" + esc(it[0]) + ":</b> " + esc(it[1]) + "</li>").join("");
    answer = "<div class=\"answer\"><b>핵심 기준과 대조</b><p>" + esc(week.goal) + "</p>" + (ideaItems ? "<ul>" + ideaItems + "</ul>" : "") + "<p class=\"muted\">산출물: " + esc(week.outcome) + "</p></div>";
  } else if (revealed) {
    const core = dayObj && dayObj.blocks && dayObj.blocks[1] ? dayObj.blocks[1].t : week.goal;
    answer = "<div class=\"answer\"><b>핵심 내용과 대조</b><p>" + esc(core) + "</p><p class=\"muted\">주간 기준: " + esc(week.goal) + "</p></div>";
  }
  const hintHTML = revealed ? "" : "<p class=\"muted recall-hint\">먼저 노트를 덮고 머릿속이나 종이에 답을 인출한 뒤 열어 대조하세요.</p>";
  const buttons = revealed
    ? "<button class=\"btn\" type=\"button\" data-act=\"recall-rate\" data-rating=\"again\" data-card=\"" + esc(card.id) + "\">다시 (틀림)</button>" +
      "<button class=\"btn\" type=\"button\" data-act=\"recall-rate\" data-rating=\"hard\" data-card=\"" + esc(card.id) + "\">힘겹게 맞음</button>" +
      "<button class=\"btn primary\" type=\"button\" data-act=\"recall-rate\" data-rating=\"good\" data-card=\"" + esc(card.id) + "\">맞음</button>" +
      "<button class=\"btn\" type=\"button\" data-act=\"recall-rate\" data-rating=\"easy\" data-card=\"" + esc(card.id) + "\">완전히 익힘</button>"
    : "<button class=\"btn primary\" type=\"button\" data-act=\"recall-commit\" data-card=\"" + esc(card.id) + "\">답을 냈다</button>";
  return "<article class=\"recall\"><div class=\"recall-head\"><p class=\"kicker\">" + (retry ? "한 번 더 · " : "복습 · ") + esc(head) + "</p><span class=\"recall-meta\">" + esc(meta) + "</span></div>" + leechHTML + "<p>" + esc(cue) + "</p>" + hintHTML + answer + "<div class=\"row\">" + buttons + "</div></article>";
}
function reviewSection(tr) {
  const shown = shownReviews(tr);
  const deferred = state.deferred[tr.id + ":" + todayISO()] || 0;
  if (!shown.length && !deferred) return "";
  const note = deferred ? "<p class=\"defer-note muted\">같은 주이거나 하루 한도(2장)를 넘긴 " + deferred + "장은 내일 이후로 분산했습니다.</p>" : "";
  return "<div class=\"reviews\"><p class=\"kicker\">오늘 첫 10분</p>" + shown.map((card) => reviewCardHTML(card, tr)).join("") + note + "</div>";
}
function doneForm(tr, week, day) {
  const id = E.sessionId(tr.id, week, day);
  if (state.done[id]) {
    return "<button class=\"check on\" type=\"button\" data-act=\"done-clear\" data-id=\"" + esc(id) + "\">완료됨</button>";
  }
  const draft = draftOf(id);
  const english = needsRecord(tr);
  const why = english ? "" : "<textarea class=\"field\" data-field=\"why\" placeholder=\"왜 맞는지 한 문장\">" + esc(draft.why) + "</textarea>";
  const record = english ? "<label><input type=\"checkbox\" data-field=\"record\"" + (draft.record ? " checked" : "") + "> 녹음·받아쓰기·고친 글이 남았다</label>" : "";
  const err = state.error && state.error.id === id ? "<p class=\"err\">" + esc(state.error.text) + "</p>" : "";
  return "<div class=\"done-box\" data-session=\"" + esc(id) + "\">" + record + why +
    "<label><input type=\"checkbox\" data-field=\"stuck\"" + (draft.stuck ? " checked" : "") + "> 막힘</label>" +
    "<input class=\"field\" data-field=\"line\" placeholder=\"막힌 한 줄\" value=\"" + esc(draft.line) + "\">" +
    err +
    "<button class=\"btn primary\" type=\"button\" data-act=\"done-submit\" data-id=\"" + esc(id) + "\">학습 완료</button></div>";
}
function passControls(tr, week) {
  const key = tr.id + ":" + week;
  const total = tr.weeks[week - 1].days.length;
  const count = weekDoneCount(tr, week);
  const passed = !!state.pass[key];
  const ready = count >= total;
  const passBtn = passed
    ? "<button class=\"pass on btn\" type=\"button\" data-act=\"pass\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + week + "\">통과함" + (state.skip[key] ? " · 넘어감" : "") + "</button>"
    : "<button class=\"btn primary\" type=\"button\" data-act=\"pass\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + week + "\"" + (ready ? "" : " disabled") + " title=\"" + (ready ? "이 주를 통과합니다" : "이번 주를 마친 뒤에 켜집니다") + "\">이 주 통과 " + count + "/" + total + "</button>";
  const skipBtn = passed ? "" : "<button class=\"btn\" type=\"button\" data-act=\"skip-pass\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + week + "\">알고 넘어가기</button>";
  return passBtn + skipBtn;
}

function hourList(items) {
  return "<ol>" + items.map((it) => "<li><span class=\"min\">" + esc(it[0]) + "</span><span>" + esc(it[1]) + "</span></li>").join("") + "</ol>";
}
function blocksHTML(blocks, replaced) {
  return "<ol class=\"blocks\">" + blocks.map((b, i) => {
    const text = i === 0 && replaced ? "이 " + b.m + "분은 위 복습 카드로 대체되어 있습니다. 노트 없이 말한 뒤 대조합니다." : b.t;
    return "<li><span class=\"min\">" + esc(b.m) + "분</span><span>" + esc(text) + "</span></li>";
  }).join("") + "</ol>";
}

function applyAccent() {
  if (state.view === "track") {
    const tr = trackById(state.track);
    document.body.dataset.track = tr.id;
    document.body.style.setProperty("--accent", tr.color);
    document.body.style.setProperty("--accent-soft", softOf(tr));
  } else {
    document.body.dataset.track = "home";
    document.body.style.removeProperty("--accent");
    document.body.style.removeProperty("--accent-soft");
  }
}
function writeHash() {
  const next = state.view === "home" ? "#/home" : state.view === "index" ? "#/index" : "#/" + state.track + "/" + state.week;
  if (location.hash !== next) history.replaceState(null, "", next);
}
function readHash() {
  const h = location.hash.replace(/^#\/?/, "");
  if (!h || h === "home") { state.view = "home"; return; }
  if (h === "index") { state.view = "index"; return; }
  const parts = h.split("/");
  const tr = trackById(parts[0]);
  if (!tr) return;
  state.view = "track";
  state.track = tr.id;
  const n = Number(parts[1]);
  state.week = Number.isInteger(n) && n >= 1 && n <= tr.weeks.length ? n : 1;
}

function renderNav() {
  const info = summary();
  document.querySelector(".brand-kicker").textContent = DATA.tracks.map((tr) => {
    const years = tr.weeks.length / 52;
    return Number.isInteger(years) ? tr.name + " " + years + "년" : tr.name + " " + tr.weeks.length + "주";
  }).join(" · ");
  document.getElementById("trackNav").innerHTML = DATA.tracks.map((tr) => {
    const on = state.view === "track" && state.track === tr.id;
    const n = shownReviews(tr).length;
    return "<button class=\"tab\" type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\"" + (on ? " aria-current=\"page\"" : "") + ">" + esc(tr.name) + (n ? " " + n : "") + "</button>";
  }).join("") + "<button class=\"tab\" type=\"button\" data-act=\"index\"" + (state.view === "index" ? " aria-current=\"page\"" : "") + ">개념</button>";
  document.getElementById("startDate").value = state.start;
  const wc = E.weeklyConsistency(state, todayISO(), 5);
  document.getElementById("statLine").textContent = "세션 " + Object.keys(state.done).length + "/" + info.sessions + " · 복습 " + reviewCount() + " · 최근 7일 " + wc.activeLast7 + "/7 · 주 " + wc.targetDays + "일 " + wc.consecutiveWeeks + "주 연속";
  applyAccent();
}

function todayCard(tr) {
  const off = offsetToday(tr);
  const reviews = reviewSection(tr);
  const deferred = state.deferred[tr.id + ":" + todayISO()] || 0;
  const waiting = shownReviews(tr).length;
  const status = "복습 " + waiting + "장" + (deferred ? " · 이연 " + deferred + "장" : "");
  if (off < 0) {
    return "<article class=\"today\" style=\"--c:" + esc(tr.color) + "\"><p class=\"kicker\">" + esc(tr.name) + " · " + status + "</p><h3>시작 전</h3><p>시작일 전에 노트와 녹음만 준비하면 됩니다.</p>" + reviews + "</article>";
  }
  const pos = studyFor(tr);
  if (!pos || pos.completed) {
    return "<article class=\"today\" style=\"--c:" + esc(tr.color) + "\"><p class=\"kicker\">" + esc(tr.name) + " · " + status + "</p><h3>전 과정을 통과했습니다</h3><p>" + esc(tr.after) + "</p>" + reviews + "<div class=\"row\"><button class=\"btn\" type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + tr.weeks.length + "\">마지막 주</button></div></article>";
  }
  const week = tr.weeks[pos.week - 1];
  const day = week.days[pos.day];
  const when = E.dateOf(tr, startFor(tr), pos.week, pos.day);
  const done = !!state.done[E.sessionId(tr.id, pos.week, pos.day)];
  const repair = pos.overtime
    ? "<p class=\"err\">달력 일정은 지났지만 미통과 주(" + pos.week + "주)가 남아 있습니다. 오늘은 " + pos.week + "주 " + (pos.day + 1) + "일차를 보충합니다.</p>"
    : pos.repair
      ? "<p class=\"muted\">가장 앞선 미통과 주(" + pos.week + "주)가 먼저 열립니다. 오늘은 " + pos.week + "주 " + (pos.day + 1) + "일차를 진행합니다.</p>"
      : "";
  const ahead = pos.skippedAhead ? "<p class=\"muted\">통과한 주를 건너뛰어 " + pos.week + "주 " + (pos.day + 1) + "일차로 이어집니다.</p>" : "";
  return "<article class=\"today\" style=\"--c:" + esc(tr.color) + "\"><p class=\"kicker\">" + esc(tr.name) + " · " + status + "</p><h3>" + esc(day.title) + "</h3><p class=\"when\">" + esc(when) + " · " + pos.week + "주 " + (pos.day + 1) + "일차 · " + (done ? "학습 완료" : "학습 전") + "</p>" + repair + ahead + reviews + "<div class=\"row\"><button class=\"btn\" type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + pos.week + "\">계획 열기</button>" + passControls(tr, pos.week) + "</div>" + doneForm(tr, pos.week, pos.day) + "</article>";
}

function renderHome() {
  const info = summary();
  const off = offsetToday();
  const where = off < 0 ? "시작 전" : "오늘";
  let map = "";
  const hasAllUnits = DATA.tracks.every((tr) => Array.isArray(tr.units) && tr.units.length > 0);
  if (hasAllUnits) {
    map = DATA.tracks.map((tr) => {
      const unitBlocks = tr.units.map((u, ui) => {
        const btns = (u.phases || []).map((pi) => {
          const p = tr.phases[pi];
          return p ? phaseMapButtonHTML(tr, p) : "";
        }).join("");
        const bm = u.benchmark;
        const bmHTML = bm
          ? "<div class=\"unit-badges\"><span class=\"badge\">" + esc(bm.level) + "</span><span class=\"badge\">" + esc(bm.standard) + "</span><span class=\"badge\">" + esc(bm.bloom) + "</span></div>"
          : "";
        return "<details class=\"unit-card\" data-unit=\"" + esc(tr.id + ":" + u.id) + "\" open><summary class=\"unit-card-head\"><span class=\"unit-badge\" style=\"color:" + esc(tr.color) + "\">" + (ui + 1) + "단원</span><strong>" + esc(u.title) + "</strong><span class=\"unit-range\">" + u.start + "–" + u.end + "주 · " + (u.phases ? u.phases.length : 0) + "단계</span></summary>" + bmHTML + "<p class=\"unit-summary muted\">" + esc(u.summary || "") + "</p><div class=\"map map-solo\">" + btns + "</div></details>";
      }).join("");
      return "<section class=\"track-map-section\"><h3 class=\"track-label\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + " <small class=\"track-label-meta\">" + tr.units.length + "개 대단원 · " + tr.phases.length + "개 중단원 · " + tr.weeks.length + "주</small></h3>" + unitBlocks + "</section>";
    }).join("");
  } else if (info.samePhases) {
    const rows = DATA.tracks[0].phases.map((_, qi) => {
      const head = "<div class=\"qh\">" + (qi + 1) + "단계</div>";
      const cells = DATA.tracks.map((tr) => {
        const p = tr.phases[qi];
        if (!p) return "";
        return "<button type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + p.start + "\"><em style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + " · " + esc(p.from) + " → " + esc(p.to) + "</em><strong>" + esc(p.name) + "</strong><small>" + p.start + "–" + p.end + "주 · " + esc(p.result) + "</small></button>";
      }).join("");
      return head + cells;
    }).join("");
    map = "<div class=\"map\" style=\"--n:" + DATA.tracks.length + "\">" + rows + "</div>";
  } else {
    map = DATA.tracks.map((tr) => "<h3 class=\"track-label\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</h3><div class=\"map map-solo\">" + tr.phases.map((p) => phaseMapButtonHTML(tr, p)).join("") + "</div>").join("");
  }
  const whereDetail = DATA.tracks.map((tr) => {
    const o = offsetToday(tr);
    if (o < 0) return tr.name + " 시작 전";
    const p = studyFor(tr);
    if (!p || p.completed) return tr.name + " 완주";
    return tr.name + " " + p.week + "주 " + (p.day + 1) + "일차";
  }).join(" · ");
  const mapDesc = DATA.tracks.map((tr) => {
    const years = Math.round(tr.weeks.length / 52);
    return tr.name + " " + years + "년(" + (tr.units ? tr.units.length : 0) + "대단원·" + tr.phases.length + "중단원)";
  }).join(", ");
  const standardsHTML = DATA.tracks.map((tr) => {
    const badges = (tr.standards || []).map((s) => "<span class=\"badge\">" + esc(s) + "</span>").join("");
    const methods = (tr.methodology || []).map((m) => "<li>" + esc(m) + "</li>").join("");
    return "<article class=\"std-card\"><p class=\"kicker\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</p><div class=\"unit-badges\">" + badges + "</div>" + (methods ? "<ul class=\"std-list\">" + methods + "</ul>" : "") + "</article>";
  }).join("");
  return [
    "<section class=\"hero\">",
    "<p class=\"kicker\">오늘 위치 · " + esc(whereDetail) + "</p>",
    "<h1>하루 60분, 인출·교차·대조로 깊어지는 학습.</h1>",
    "<p class=\"lead\">" + esc(info.durationText) + " 과정입니다. 한 주는 7세션(하루 60분 × 7일차)으로 구성되며, 첫 10분은 복습 주기가 돌아온 카드나 직전 핵심 개념을 노트를 덮고 인출하는 시간입니다. 학습과학 권장 페이스는 <b>한 번에 1~2개 도메인 집중, 주 5~6세션 + 1~2일 휴식(수면 공고화)</b>이며(4트랙 동시 진행 시 하루 " + info.parallel + "시간), 각 트랙 상단 진단 배치로 이미 숙달한 대단원을 건너뛰고 시작할 수 있습니다.</p>",
    "<div class=\"hero-stats\"><div><b>" + esc(info.hours) + "</b><span>" + esc(info.hoursSub) + "</span></div><div><b>" + esc(info.parallel) + "</b><span>전 트랙 병행 시 시간</span></div><div><b>" + esc(info.weeks) + "</b><span>" + esc(info.weeksSub) + "</span></div><div><b>" + info.sessions.toLocaleString("ko-KR") + "</b><span>전체 세션</span></div></div>",
    "</section>",
    "<section class=\"section\"><h2>오늘</h2><p class=\"muted\">" + esc(where) + " · 복습 카드는 스스로 답을 말하거나 적은 뒤에만 핵심 기준·대조 카드가 열리며, 4단계 인출 난이도(다시·힘겹게·맞음·완전히 익힘)에 따라 복습 배율과 간격이 적응형으로 조절됩니다. 도메인마다 하루 최대 두 장까지 교차 출제됩니다.</p><div class=\"today-grid\">" + DATA.tracks.map(todayCard).join("") + "</div></section>",
    "<section class=\"section\"><h2>전체 지도</h2><p class=\"muted\">도메인별 대단원 아래 중단원(13주)을 누르면 해당 첫 주로 이동합니다. " + esc(mapDesc) + " 구성입니다.</p>" + map + "</section>",
    "<section class=\"section\"><h2>60분을 쓰는 방법</h2><div class=\"hours-grid\">" + DATA.tracks.map((tr) => "<article class=\"hour\"><p class=\"kicker\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</p><h3>" + esc(tr.hourTitle) + "</h3>" + hourList(tr.hour) + "</article>").join("") + "</div></section>",
    "<section class=\"section\"><h2>검증 기관 커리큘럼 및 학습과학 근거</h2><p class=\"muted\">각 도메인은 공인 학회·대학·표준 기구 커리큘럼을 기반으로 설계되었으며, 인출 연습·분산 간격(Cepeda)·교차 판별(Rohrer)·점진적 소거·Nation Four Strands를 일일 블록에 통합했습니다.</p><div class=\"standards-grid\">" + standardsHTML + "</div></section>",
    "<section class=\"section prep\"><h2>시작 전 준비</h2><p>도메인별 노트(영어·알고리즘·수학·소프트웨어)와 녹음 앱을 준비합니다. 계산기와 프로그래밍 언어 환경은 1주차 과제를 수행할 때 준비해도 충분합니다. 주 7세션 단위로 설계되어 있으나 인지 과부하를 막기 위해 한 번에 1~2개 도메인만 시작하고 주 5~6일 리듬 + 1~2일 휴식을 취하는 것을 권장합니다. 이미 아는 대단원은 트랙 화면 상단 '진단 배치'에서 한 번에 건너뛸 수 있으며, 상단 지표는 휴식일을 벌주지 않는 주 5일 연속 일관성을 함께 추적합니다.</p></section>",
    "<section class=\"section\"><h2>과정의 끝</h2><div class=\"dest-grid\">" + DATA.tracks.map((tr) => "<article class=\"dest\"><p class=\"kicker\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</p><h3>" + esc(tr.destination) + "</h3><p>" + esc(tr.limit) + "</p><p style=\"margin-top:8px\"><b>이후.</b> " + esc(tr.after) + "</p></article>").join("") + "</div></section>",
    "<section class=\"section\"><h2>공통 규칙</h2><div class=\"principles\"><article><h3>통과해야 다음 주로 넘어간다</h3><p>이전 주 통과 기준을 충족하기 전에는 달력상 다음 주로 넘어가지 않고, 가장 앞선 미통과 주의 남은 일차를 먼저 마칩니다. 이미 아는 주제는 주간 '알고 넘어가기' 또는 대단원 '진단 배치'로 건너뛰고, 4단계 적응형 분산 복습과 1회 실수 재학습 절감(Savings)으로 장기 기억을 검증합니다.</p></article><article><h3>직접 만든 산출물이 있어야 진도다</h3><p>강의나 교재를 수동적으로 읽는 것만으로는 60분을 채우지 않습니다. 영어는 녹음·받아쓰기·퇴고 글, 수학·알고리즘은 백지 증명과 반례·코드, 소프트웨어는 상반된 설계 대안을 비교한 노트나 커밋이 남아야 완료입니다.</p></article><article><h3>기록은 로컬에 안전하게 보관된다</h3><p>학습 완료, 주차 통과, 복습 일정은 브라우저와 로컬 런처 폴더의 <code>roadmap-state.json</code>에 함께 저장됩니다. 기기를 옮기기 전에는 상단 기록 메뉴에서 JSON 백업을 내보내 두세요.</p></article></div></section>",
    "<p class=\"foot\">이 로드맵은 검증된 공인 표준(MAA CUPM · ACM/IEEE CS2023 · IEEE SWEBOK v4 · Council of Europe CEFR 2020)과 고전 교재를 바탕으로 재구성한 자기주도 학습 계획입니다. 계약 영어는 문장의 조건과 모호성을 다루는 언어 훈련이며 법률 자문이 아닙니다.</p>"
  ].join("");
}

function phaseAccordionHTML(tr, p, q, unitContextText) {
  const buttons = [];
  for (let w = p.start; w <= p.end && w <= tr.weeks.length; w++) {
    const week = tr.weeks[w - 1];
    if (!week) continue;
    const blob = ((unitContextText || "") + " " + p.name + " " + week.title + " " + week.goal + " " + (week.ideas || []).map((i) => i[0] + " " + i[1]).join(" ") + " " + week.days.map((d) => d.title).join(" ")).toLowerCase();
    if (q && blob.indexOf(q) === -1) continue;
    const on = w === state.week;
    buttons.push("<button class=\"wbtn\" type=\"button\" data-act=\"week\" data-week=\"" + w + "\"" + (on ? " aria-current=\"page\"" : "") + ">" + w + ". " + esc(week.title) + "<span>" + weekDoneCount(tr, w) + "/" + week.days.length + "</span></button>");
  }
  if (!buttons.length) return "";
  const open = q || (state.week >= p.start && state.week <= p.end);
  return "<details class=\"phase-group\" data-phase=\"" + esc(tr.id + ":" + p.start) + "\"" + (open ? " open" : "") + "><summary>" + esc(p.name) + " · " + p.start + "–" + p.end + "주</summary><div class=\"weekbtns\">" + buttons.join("") + "</div></details>";
}

function weekListHTML(tr) {
  const q = (state.q || "").trim().toLowerCase();
  if (Array.isArray(tr.units) && tr.units.length) {
    const unitsHTML = tr.units.map((u, ui) => {
      const ctx = (ui + 1) + "단원 " + u.title;
      const phasesHTML = (u.phases || []).map((pi) => {
        const p = tr.phases[pi];
        return p ? phaseAccordionHTML(tr, p, q, ctx) : "";
      }).join("");
      if (!phasesHTML) return "";
      const open = q || (state.week >= u.start && state.week <= u.end);
      return "<details class=\"unit-group\" data-unit=\"" + esc(tr.id + ":" + u.id) + "\"" + (open ? " open" : "") + "><summary class=\"unit-group-summary\"><span>" + (ui + 1) + ". " + esc(u.title) + "</span><small>" + u.start + "–" + u.end + "주</small></summary><div class=\"unit-phases\">" + phasesHTML + "</div></details>";
    }).join("");
    return unitsHTML || "<p class=\"muted\">맞는 주가 없습니다.</p>";
  }
  const phases = tr.phases.map((p) => phaseAccordionHTML(tr, p, q, "")).join("");
  return phases || "<p class=\"muted\">맞는 주가 없습니다.</p>";
}

function renderTrack() {
  const tr = trackById(state.track);
  const week = tr.weeks[state.week - 1];
  const phase = tr.phases.find((p) => state.week >= p.start && state.week <= p.end) || tr.phases[0];
  const unitInfo = unitForWeek(tr, state.week);
  const study = studyFor(tr);
  const off = offsetToday(tr);
  const today = todayISO();
  const hasCustomStart = !!(state.starts && E.isValidISO(state.starts[tr.id]) && state.starts[tr.id] !== state.start);
  const rev = state.reviewed && state.reviewed[tr.id];
  const revToday = !!(rev && (rev === today || rev.date === today));
  let warn = false;
  for (let prevW = 1; prevW < state.week; prevW++) {
    if (!state.pass[tr.id + ":" + prevW]) { warn = true; break; }
  }
  let prereqWarn = "";
  const reqs = Array.isArray(tr.prerequisites) ? tr.prerequisites : [];
  if (reqs.length) {
    const unmet = reqs.filter((r) => state.week >= r.week && !state.pass[r.reqTrack + ":" + r.reqWeek]);
    if (unmet.length) {
      const items = unmet.map((r) => {
        const reqTr = trackById(r.reqTrack);
        const reqName = reqTr ? reqTr.name : r.reqTrack;
        return "<button class=\"prereq-btn\" type=\"button\" data-act=\"track\" data-track=\"" + esc(r.reqTrack) + "\" data-week=\"" + r.reqWeek + "\">" + esc(r.topic) + " (" + r.week + "주~ → " + esc(reqName) + " " + r.reqWeek + "주)</button>";
      }).join(" ");
      prereqWarn = "<div class=\"banner\"><b>선수 학습 안내:</b> 현재 주차는 다음 선행 주제를 바탕으로 합니다. 눌러서 먼저 확인하거나 진단 통과할 수 있습니다.<div class=\"prereq-links\">" + items + "</div></div>";
    }
  }
  let diagPanel = "";
  if (Array.isArray(tr.units) && tr.units.length) {
    const hasDiagMsg = !!(state.diagNote && state.diagNote.track === tr.id);
    const unitChecks = tr.units.map((u, ui) => {
      let allPassed = true;
      for (let w = u.start; w <= u.end; w++) {
        if (!state.pass[tr.id + ":" + w]) { allPassed = false; break; }
      }
      const bm = u.benchmark;
      const bmText = bm ? "<span class=\"badge\">" + esc(bm.level) + "</span> <span class=\"badge\">" + esc(bm.standard) + "</span>" : "";
      const diagList = bm && Array.isArray(bm.diagnostic)
        ? "<ul class=\"diag-list\">" + bm.diagnostic.map((item) => "<li>" + esc(item) + "</li>").join("") + "</ul>"
        : "";
      return "<label class=\"diag-unit\"><div class=\"diag-unit-head\"><input type=\"checkbox\" data-diag-unit=\"" + esc(u.id) + "\"" + (allPassed ? " disabled" : "") + "><strong>" + (ui + 1) + "단원 · " + esc(u.title) + "</strong> <span class=\"muted\">(" + u.start + "–" + u.end + "주)</span> " + (allPassed ? "<span class=\"badge good\">통과됨</span>" : "") + bmText + "</div>" + diagList + "</label>";
    }).join("");
    const msgHTML = hasDiagMsg ? "<p class=\"diag-result\">" + esc(state.diagNote.text) + "</p>" : "";
    diagPanel = "<details class=\"diag-panel noprint\" data-diag=\"" + esc(tr.id) + "\"" + (hasDiagMsg ? " open" : "") + "><summary>진단 배치 · 이미 숙달한 대단원 건너뛰기</summary><p class=\"muted\">아래 성취 기준(Can-Do)을 이미 충족하는 대단원을 선택해 일괄 통과하면, 중단원별 대표 캡스톤 카드만 3·7·16일 간격으로 분산 시드해 검증합니다.</p><div class=\"diag-units\">" + unitChecks + "</div><div class=\"row\"><button class=\"btn primary\" type=\"button\" data-act=\"diag-apply\" data-track=\"" + esc(tr.id) + "\">선택 단원 진단 통과</button></div>" + msgHTML + "</details>";
  }
  const days = week.days.map((day, i) => {
    const when = E.dateOf(tr, startFor(tr), state.week, i);
    const isStudy = study && !study.completed && study.week === state.week && study.day === i && off >= 0;
    const revMatchesDay = revToday && (typeof rev === "string" || rev.session === E.sessionId(tr.id, state.week, i));
    const replaced = isStudy && (shownReviews(tr).length > 0 || revMatchesDay);
    return "<article class=\"day" + (isStudy ? " today" : "") + "\"><div><p class=\"when\">" + (i + 1) + "일차 · " + esc(when) + (isStudy ? " · 오늘 학습" : "") + (i === week.days.length - 1 ? " · 점검" : "") + "</p><h3>" + esc(day.title) + "</h3><div class=\"day-actions\">" + doneForm(tr, state.week, i) + "<button class=\"btn\" type=\"button\" data-act=\"timer\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + state.week + "\" data-day=\"" + i + "\">타이머</button></div></div>" + blocksHTML(day.blocks, replaced) + "</article>";
  }).join("");
  const ideas = distinctIdeas(week);
  const startResetBtn = hasCustomStart ? "<button class=\"btn-link\" type=\"button\" data-act=\"track-start-reset\" data-track=\"" + esc(tr.id) + "\">전역 시작일 따르기</button>" : "";
  const breadcrumb = (unitInfo ? (unitInfo.index + 1) + "단원 " + unitInfo.unit.title + " › " : "") + phase.name;
  return [
    "<div class=\"layout\">",
    "<aside class=\"side noprint\"><input class=\"search\" id=\"q\" placeholder=\"단원, 개념, 주 제목 검색\" value=\"" + esc(state.q || "") + "\"><div id=\"weekList\">" + weekListHTML(tr) + "</div></aside>",
    "<section id=\"week\">",
    "<div class=\"track-bar\"><p class=\"kicker\">" + esc(breadcrumb) + " · " + esc(phase.from) + " → " + esc(phase.to) + "</p><label class=\"track-start noprint\">도메인 시작일 <input type=\"date\" data-act=\"track-start\" data-track=\"" + esc(tr.id) + "\" value=\"" + esc(startFor(tr)) + "\">" + startResetBtn + "</label></div>",
    "<div class=\"week-head\"><h2><span class=\"min\">" + String(state.week).padStart(2, "0") + "</span> " + esc(week.title) + "</h2><p class=\"goal\">" + esc(week.goal) + "</p></div>",
    warn ? "<div class=\"banner\">이전 주 중 미통과 주간이 있습니다. 오늘 본학습은 가장 앞선 미통과 주의 아직 안 끝난 날로 돌아갑니다.</div>" : "",
    prereqWarn,
    diagPanel,
    reviewSection(tr),
    ideas.length ? "<div class=\"ideas\">" + ideas.map((idea) => "<article class=\"idea\"><b>" + esc(idea[0]) + "</b>" + esc(idea[1]) + "</article>").join("") + "</div>" : "",
    "<div class=\"meta\"><div><b>이번 주 산출물</b><small>" + esc(week.outcome) + "</small></div><div><b>펼칠 자료</b><small>" + esc(week.resource) + "</small></div><div><b>통과 기준</b><small>" + esc(week.check) + "</small></div></div>",
    "<div class=\"row noprint\">" + passControls(tr, state.week) + "<button class=\"btn\" type=\"button\" data-act=\"jump\" data-week=\"" + Math.max(1, state.week - 1) + "\"" + (state.week <= 1 ? " disabled" : "") + " title=\"단축키 [\">이전 주 ([)</button><button class=\"btn\" type=\"button\" data-act=\"jump\" data-week=\"" + Math.min(tr.weeks.length, state.week + 1) + "\"" + (state.week >= tr.weeks.length ? " disabled" : "") + " title=\"단축키 ]\">다음 주 (])</button><button class=\"btn\" type=\"button\" data-act=\"today-jump\"" + (!study ? " disabled title=\"시작일 전입니다\"" : "") + ">오늘 학습으로</button></div>",
    days,
    "<p class=\"foot\">" + esc(tr.name) + (unitInfo ? " · " + esc(unitInfo.unit.title) : "") + " · " + esc(phase.name) + " 결과: " + esc(phase.result) + "</p>",
    "</section></div>"
  ].join("");
}

function indexMatches() {
  const q = (state.iq || "").trim().toLowerCase();
  const rows = [];
  DATA.tracks.forEach((tr) => {
    if (indexFilter !== "all" && tr.id !== indexFilter) return;
    tr.phases.forEach((phase, pi) => {
      const unitInfo = unitOfPhase(tr, pi);
      const unitTitle = unitInfo ? unitInfo.unit.title : "";
      for (let weekNo = phase.start; weekNo <= phase.end && weekNo <= tr.weeks.length; weekNo++) {
        const week = tr.weeks[weekNo - 1];
        if (!week) continue;
        (week.ideas || []).forEach((idea) => {
          const blob = (tr.name + " " + unitTitle + " " + phase.name + " " + week.title + " " + idea[0] + " " + idea[1]).toLowerCase();
          if (q && blob.indexOf(q) === -1) return;
          rows.push({ tr: tr, unitTitle: unitTitle, phaseName: phase.name, weekNo: weekNo, title: week.title, idea: idea });
        });
      }
    });
  });
  return rows;
}

function indexRowHTML(row) {
  const ctx = [row.tr.name, row.unitTitle, row.phaseName, row.weekNo + "주 " + row.title].filter(Boolean).join(" · ");
  return "<button type=\"button\" data-act=\"track\" data-track=\"" + esc(row.tr.id) + "\" data-week=\"" + row.weekNo + "\"><small>" + esc(ctx) + "</small><br><b>" + esc(row.idea[0]) + "</b> " + esc(row.idea[1]) + "</button>";
}

function updateIndexResults() {
  const matches = indexMatches();
  const visible = matches.slice(0, indexLimit);
  const countEl = document.getElementById("indexCount");
  const listEl = document.getElementById("indexList");
  const moreEl = document.getElementById("indexMore");
  if (countEl) {
    countEl.textContent = "용어를 누르면 그 주로 이동합니다. " + matches.length.toLocaleString("ko-KR") + "개 중 " + visible.length.toLocaleString("ko-KR") + "개 표시.";
  }
  if (listEl) {
    listEl.innerHTML = visible.length ? visible.map(indexRowHTML).join("") : "<p class=\"muted\">맞는 개념이 없습니다.</p>";
  }
  if (moreEl) {
    moreEl.innerHTML = matches.length > indexLimit
      ? "<button class=\"btn\" type=\"button\" data-act=\"index-more\">더 보기 (남은 " + (matches.length - indexLimit).toLocaleString("ko-KR") + "개)</button>"
      : "";
  }
}

function renderIndex() {
  const matches = indexMatches();
  const visible = matches.slice(0, indexLimit);
  const filters = [{ id: "all", name: "전체" }].concat(DATA.tracks.map((tr) => ({ id: tr.id, name: tr.name })));
  const filterHTML = "<div class=\"index-filters\">" + filters.map((f) => "<button type=\"button\" class=\"filter-btn" + (indexFilter === f.id ? " on" : "") + "\" data-act=\"index-filter\" data-track=\"" + esc(f.id) + "\">" + esc(f.name) + "</button>").join("") + "</div>";
  const moreHTML = matches.length > indexLimit
    ? "<button class=\"btn\" type=\"button\" data-act=\"index-more\">더 보기 (남은 " + (matches.length - indexLimit).toLocaleString("ko-KR") + "개)</button>"
    : "";
  return "<section><p class=\"kicker\">개념 색인</p><h2>과정에서 만나는 개념</h2>" + filterHTML +
    "<p class=\"muted\" id=\"indexCount\">용어를 누르면 그 주로 이동합니다. " + matches.length.toLocaleString("ko-KR") + "개 중 " + visible.length.toLocaleString("ko-KR") + "개 표시.</p>" +
    "<input class=\"search\" id=\"indexQ\" placeholder=\"용어 검색\" value=\"" + esc(state.iq || "") + "\">" +
    "<div class=\"index-list\" id=\"indexList\">" + (visible.length ? visible.map(indexRowHTML).join("") : "<p class=\"muted\">맞는 개념이 없습니다.</p>") + "</div>" +
    "<div class=\"index-more\" id=\"indexMore\">" + moreHTML + "</div></section>";
}

function render(opts) {
  opts = opts || {};
  captureDrafts();
  prepareQueues();
  const y = opts.keepScroll ? window.scrollY : 0;
  renderNav();
  const app = document.getElementById("app");
  if (!DATA.tracks.length) {
    app.textContent = "커리큘럼 데이터가 비어 있습니다.";
    return;
  }
  const openMap = new Map();
  app.querySelectorAll("details[data-unit], details[data-phase], details[data-diag]").forEach((el) => {
    const k = el.dataset.unit ? "u:" + el.dataset.unit : el.dataset.phase ? "p:" + el.dataset.phase : "d:" + el.dataset.diag;
    openMap.set(k, el.open);
  });
  if (state.view === "home") app.innerHTML = renderHome();
  else if (state.view === "index") app.innerHTML = renderIndex();
  else app.innerHTML = renderTrack();
  if (openMap.size) {
    app.querySelectorAll("details[data-unit], details[data-phase], details[data-diag]").forEach((el) => {
      const k = el.dataset.unit ? "u:" + el.dataset.unit : el.dataset.phase ? "p:" + el.dataset.phase : "d:" + el.dataset.diag;
      if (openMap.has(k)) el.open = openMap.get(k);
    });
  }
  window.scrollTo(0, opts.keepScroll ? y : 0);
}

function finishCard(card, rating) {
  const today = todayISO();
  const result = E.grade(card, rating, today);
  if (!result.ok) return;
  if (result.result === "success" || result.result === "fail") {
    state.activity[today] = "card";
    state.reviewed = state.reviewed || {};
    const tr = trackById(card.track);
    const study = tr ? studyFor(tr) : null;
    const sid = study && !study.completed ? E.sessionId(card.track, study.week, study.day) : "";
    state.reviewed[card.track] = { date: today, session: sid };
  }
  persist(true);
  render({ keepScroll: true });
}

function submitDone(id) {
  captureDrafts();
  const parts = id.split(":");
  const tr = trackById(parts[0]);
  const week = Number(parts[1]);
  const day = Number(parts[2]);
  const draft = draftOf(id);
  if (!needsRecord(tr) && !String(draft.why || "").trim()) {
    state.error = { id: id, text: "왜 맞는지 한 문장을 적어야 완료됩니다." };
    render({ keepScroll: true });
    return;
  }
  if (needsRecord(tr) && !draft.record) {
    state.error = { id: id, text: "녹음이나 기록이 남았는지 확인해 주세요." };
    render({ keepScroll: true });
    return;
  }
  if (draft.stuck && !String(draft.line || "").trim()) {
    state.error = { id: id, text: "막힌 한 줄을 적어야 다음 복습 카드가 됩니다." };
    render({ keepScroll: true });
    return;
  }
  const today = todayISO();
  state.done[id] = today;
  if (!needsRecord(tr)) state.why[id] = String(draft.why).trim();
  if (draft.stuck) {
    const from = E.dateOf(tr, startFor(tr), week, day);
    E.scheduleStuck(state, tr.id, week, day, String(draft.line).trim(), from, today);
  }
  delete state.drafts[id];
  state.error = null;
  persist(true);
  render({ keepScroll: true });
}

function togglePass(trackId, week, skip) {
  const tr = trackById(trackId);
  const key = trackId + ":" + week;
  const today = todayISO();
  if (!skip && state.pass[key]) {
    if (!window.confirm(week + "주 통과 표시를 취소할까요?")) return;
    delete state.pass[key];
    delete state.skip[key];
    const card = state.cards[E.weekCardId(trackId, week)];
    if (card && card.step <= 1) delete state.cards[card.id];
    persist(true);
    render({ keepScroll: true });
    return;
  }
  if (!skip && weekDoneCount(tr, week) < tr.weeks[week - 1].days.length) return;
  if (skip && !window.confirm("통과 기준을 충족하지 못한 채로 넘어갑니다. 이 주는 3일 뒤 복습으로 돌아옵니다. 계속할까요?")) return;
  state.pass[key] = today;
  if (skip) state.skip[key] = today;
  else delete state.skip[key];
  E.scheduleWeek(state, trackId, Number(week), today, !!skip);
  persist(true);
  render({ keepScroll: true });
}

const timer = { running: false, left: 0, blocks: [], index: 0, handle: 0, endAt: 0, label: "" };
function showDock() {
  const dock = document.getElementById("dock");
  const block = timer.blocks[timer.index];
  if (!block) {
    dock.hidden = true;
    document.body.classList.remove("timing");
    document.title = BASE_TITLE;
    return;
  }
  dock.hidden = false;
  document.body.classList.add("timing");
  const total = timer.blocks.reduce((a, b) => a + b.m, 0) * 60;
  const spent = timer.blocks.slice(0, timer.index).reduce((a, b) => a + b.m, 0) * 60 + (block.m * 60 - timer.left);
  document.getElementById("dockLabel").textContent = timer.label + " (" + (timer.index + 1) + "/" + timer.blocks.length + ") · " + block.m + "분 · " + block.t;
  const sec = Math.ceil(timer.left);
  const clockStr = String(Math.floor(sec / 60)).padStart(2, "0") + ":" + String(sec % 60).padStart(2, "0");
  document.getElementById("dockClock").textContent = clockStr;
  document.getElementById("dockBar").style.width = (total > 0 ? Math.min(100, (spent / total) * 100) : 0) + "%";
  document.querySelector("[data-act='timer-toggle']").textContent = timer.running ? "일시정지" : "시작";
  const prevBtn = document.querySelector("[data-act='timer-prev']");
  const nextBtn = document.querySelector("[data-act='timer-next']");
  if (prevBtn) prevBtn.disabled = timer.index <= 0;
  if (nextBtn) nextBtn.disabled = timer.index >= timer.blocks.length - 1;
  document.title = "[" + clockStr + "] " + timer.label + " · " + BASE_TITLE;
}

function beep() {
  try {
    const AudioCtor = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtor) return;
    if (!audioCtx || audioCtx.state === "closed") audioCtx = new AudioCtor();
    if (audioCtx.state === "suspended") audioCtx.resume().catch(() => {});
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.frequency.value = 640;
    o.connect(g);
    g.connect(audioCtx.destination);
    g.gain.setValueAtTime(0.04, audioCtx.currentTime);
    o.start();
    o.stop(audioCtx.currentTime + 0.12);
  } catch (err) { /* 소리 없음 */ }
}

function tick() {
  if (!timer.running) return;
  let advanced = false;
  while (timer.running && Date.now() >= timer.endAt) {
    const overshootMs = Date.now() - timer.endAt;
    advanced = true;
    if (timer.index < timer.blocks.length - 1) {
      timer.index += 1;
      timer.left = timer.blocks[timer.index].m * 60;
      timer.endAt = Date.now() - overshootMs + timer.left * 1000;
    } else {
      timer.running = false;
      timer.left = 0;
      clearInterval(timer.handle);
      break;
    }
  }
  if (advanced) beep();
  if (timer.running) timer.left = Math.max(0, (timer.endAt - Date.now()) / 1000);
  showDock();
}

function startTimer(tr, week, day) {
  const source = tr.weeks[week - 1].days[day];
  const blocks = source.blocks.map((b) => ({ m: b.m, t: b.t }));
  const study = studyFor(tr);
  const rev = state.reviewed && state.reviewed[tr.id];
  const revToday = !!(rev && (rev === todayISO() || rev.date === todayISO()));
  const revMatchesDay = revToday && (typeof rev === "string" || rev.session === E.sessionId(tr.id, week, day));
  if (study && !study.completed && study.week === week && study.day === day && (shownReviews(tr).length || revMatchesDay)) {
    blocks[0] = { m: blocks[0].m, t: "기한 복습을 노트 없이 말한 뒤 대조한다." };
  }
  timer.blocks = blocks;
  timer.index = 0;
  timer.left = blocks[0].m * 60;
  timer.running = false;
  timer.label = tr.name + " " + week + "주 · " + source.title;
  clearInterval(timer.handle);
  showDock();
}

function closeMenus() {
  document.querySelectorAll("details.menu[open]").forEach((m) => { m.open = false; });
}

document.body.addEventListener("click", (e) => {
  if (!e.target.closest(".menu")) closeMenus();
  const t = e.target.closest("[data-act]");
  if (!t || !state) return;
  const act = t.dataset.act;
  if (act === "home") {
    state.view = "home";
    writeHash();
    persist(false);
    render();
  } else if (act === "index") {
    state.view = "index";
    writeHash();
    persist(false);
    render();
    closeMenus();
  } else if (act === "index-filter") {
    indexFilter = t.dataset.track || "all";
    indexLimit = 200;
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.classList.toggle("on", btn.dataset.track === indexFilter);
    });
    updateIndexResults();
  } else if (act === "index-more") {
    indexLimit += 200;
    updateIndexResults();
  } else if (act === "track") {
    if (state.track !== t.dataset.track) state.q = "";
    state.view = "track";
    state.track = t.dataset.track;
    if (t.dataset.week) state.week = Number(t.dataset.week);
    clampState(state);
    writeHash();
    persist(false);
    render();
  } else if (act === "week" || act === "jump") {
    state.week = Number(t.dataset.week);
    clampState(state);
    writeHash();
    persist(false);
    render();
  } else if (act === "today-jump") {
    const pos = studyFor(trackById(state.track));
    if (pos) state.week = pos.week;
    writeHash();
    persist(false);
    render();
  } else if (act === "track-start-reset") {
    if (state.starts) delete state.starts[t.dataset.track];
    persist(true);
    render({ keepScroll: true });
  } else if (act === "done-clear") {
    const id = t.dataset.id;
    const parts = id.split(":");
    const tr = trackById(parts[0]);
    state.drafts[id] = {
      why: state.why[id] || "",
      line: state.stuck[id] || "",
      stuck: !!state.stuck[id],
      record: !!(tr && needsRecord(tr))
    };
    const clearedDate = state.done[id];
    delete state.done[id];
    delete state.why[id];
    delete state.stuck[id];
    if (clearedDate && state.activity && state.activity[clearedDate] === true && !Object.keys(state.done).some((k) => state.done[k] === clearedDate)) {
      delete state.activity[clearedDate];
    }
    const dCardId = E.dayCardId(parts[0], Number(parts[1]), Number(parts[2]));
    const dCard = state.cards[dCardId];
    if (dCard && dCard.step === 0) {
      delete state.cards[dCardId];
    }
    const passKey = parts[0] + ":" + parts[1];
    if (state.pass[passKey] && !state.skip[passKey]) {
      delete state.pass[passKey];
      const wCard = state.cards[E.weekCardId(parts[0], Number(parts[1]))];
      if (wCard && wCard.step <= 1) delete state.cards[wCard.id];
    }
    persist(true);
    render({ keepScroll: true });
  } else if (act === "done-submit") {
    submitDone(t.dataset.id);
  } else if (act === "pass") {
    togglePass(t.dataset.track, Number(t.dataset.week), false);
  } else if (act === "skip-pass") {
    togglePass(t.dataset.track, Number(t.dataset.week), true);
  } else if (act === "recall-commit") {
    const card = state.cards[t.dataset.card];
    if (card && E.commitAnswer(card)) {
      persist(true);
      render({ keepScroll: true });
    }
  } else if (act === "recall-rate") {
    const card = state.cards[t.dataset.card];
    if (card) finishCard(card, t.dataset.rating);
  } else if (act === "recall-yes" || act === "recall-no") {
    const card = state.cards[t.dataset.card];
    if (card) finishCard(card, act === "recall-yes");
  } else if (act === "diag-apply") {
    const tr = trackById(t.dataset.track);
    const panel = t.closest(".diag-panel");
    if (!tr || !panel) return;
    const selectedIds = Array.from(panel.querySelectorAll("input[data-diag-unit]:checked:not(:disabled)")).map((el) => el.dataset.diagUnit);
    if (!selectedIds.length) {
      state.diagNote = { track: tr.id, text: "진단 통과할 대단원을 하나 이상 선택해 주세요." };
      render({ keepScroll: true });
      return;
    }
    const res = E.applyDiagnosticPlacement(tr, state, selectedIds, todayISO());
    state.diagNote = {
      track: tr.id,
      text: selectedIds.length + "개 단원(" + res.skippedWeeks + "주)을 진단 통과 처리하고, 중단원 대표 검증 카드 " + res.seededCards + "장을 3·7·16일 간격으로 분산 등록했습니다."
    };
    persist(true);
    render({ keepScroll: true });
  } else if (act === "timer") {
    startTimer(trackById(t.dataset.track), Number(t.dataset.week), Number(t.dataset.day));
  } else if (act === "timer-toggle") {
    if (!timer.blocks.length) return;
    timer.running = !timer.running;
    if (timer.running) {
      if (timer.left <= 0) {
        if (timer.index >= timer.blocks.length - 1) timer.index = 0;
        timer.left = timer.blocks[timer.index].m * 60;
      }
      timer.endAt = Date.now() + timer.left * 1000;
      clearInterval(timer.handle);
      timer.handle = setInterval(tick, 250);
    } else clearInterval(timer.handle);
    showDock();
  } else if (act === "timer-prev") {
    if (timer.index > 0) {
      timer.index -= 1;
      timer.left = timer.blocks[timer.index].m * 60;
      if (timer.running) timer.endAt = Date.now() + timer.left * 1000;
      showDock();
    }
  } else if (act === "timer-next") {
    if (timer.index < timer.blocks.length - 1) {
      timer.index += 1;
      timer.left = timer.blocks[timer.index].m * 60;
      if (timer.running) timer.endAt = Date.now() + timer.left * 1000;
      showDock();
    }
  } else if (act === "timer-close") {
    timer.running = false;
    clearInterval(timer.handle);
    timer.blocks = [];
    document.getElementById("dock").hidden = true;
    document.body.classList.remove("timing");
    document.title = BASE_TITLE;
  } else if (act === "export") {
    const blob = new Blob([JSON.stringify(snapshot(), null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "roadmap-progress.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    closeMenus();
  } else if (act === "import") {
    closeMenus();
    document.getElementById("importFile").click();
  } else if (act === "reset") {
    closeMenus();
    if (confirm("이 브라우저와 로컬 백업의 완료 기록, 복습 일정, 시작일을 지울까요?")) {
      localStorage.removeItem(KEY);
      localStorage.removeItem(PREV);
      localStorage.removeItem(LEGACY);
      clearTimeout(remoteTimer);
      remoteTimer = 0;
      remoteSyncEnabled = false;
      remoteDirty = false;
      fetch("/api/state", { method: "DELETE" }).catch(() => {}).finally(() => {
        location.hash = "#/home";
        location.reload();
      });
    }
  }
});

document.body.addEventListener("input", (e) => {
  if (!state) return;
  if (e.target.id === "q") {
    state.q = e.target.value;
    const list = document.getElementById("weekList");
    if (list) list.innerHTML = weekListHTML(trackById(state.track));
  } else if (e.target.id === "indexQ") {
    state.iq = e.target.value;
    indexLimit = 200;
    updateIndexResults();
  } else if (e.target.closest(".done-box")) {
    if (e.target.matches("[data-field='line']") && e.target.value.trim()) {
      const box = e.target.closest(".done-box");
      const cb = box && box.querySelector("[data-field='stuck']");
      if (cb) cb.checked = true;
    }
    captureDrafts();
  }
});
document.body.addEventListener("change", (e) => {
  if (!state) return;
  if (e.target.dataset && e.target.dataset.act === "track-start" && e.target.value) {
    if (!E.isValidISO(e.target.value)) return;
    state.starts = state.starts || {};
    state.starts[e.target.dataset.track] = e.target.value;
    persist(true);
    render({ keepScroll: true });
  }
});
document.getElementById("startDate").addEventListener("change", (e) => {
  if (!e.target.value || !state || !E.isValidISO(e.target.value)) return;
  state.start = e.target.value;
  persist(true);
  render({ keepScroll: true });
});
document.getElementById("importFile").addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      if (!isPlainObj(data)) throw new Error("형식");
      state = stateFromSaved(data);
      state.drafts = {};
      state.error = null;
      state.diagNote = null;
      clampState(state);
      writeHash();
      persist(true);
      render();
    } catch (err) {
      alert("가져올 수 없는 파일입니다.");
    }
  };
  reader.readAsText(file);
  e.target.value = "";
});
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.altKey || e.metaKey) return;
  if (e.key === "Escape") {
    closeMenus();
    return;
  }
  if (!state || e.target.matches("input, textarea") || state.view !== "track") return;
  const max = trackById(state.track).weeks.length;
  if (e.key === "[") state.week = Math.max(1, state.week - 1);
  else if (e.key === "]") state.week = Math.min(max, state.week + 1);
  else return;
  writeHash();
  persist(false);
  render();
});
window.addEventListener("hashchange", () => { if (!state) return; readHash(); clampState(state); render(); });

function fileHelp() {
  document.getElementById("app").innerHTML = "<section class=\"file-help\"><h1>커리큘럼을 읽지 못했습니다</h1><p class=\"lead\">이 주소는 파일로 직접 열려 있어 도메인 JSON을 불러올 수 없습니다. 같은 폴더의 학습로드맵.bat 을 실행한 뒤 열린 로컬 주소로 다시 들어오세요.</p></section>";
}

async function boot() {
  const localInfo = loadLocalRaw();
  const remoteState = await fetchRemoteState();
  const picked = pickInitialState(localInfo.state, remoteState);
  state = clampState(picked.chosen);
  state.drafts = {};
  state.error = null;
  state.diagNote = null;
  remoteSyncEnabled = !!(localInfo.existed || remoteState);
  if (location.hash) readHash();
  clampState(state);
  if (!location.hash) writeHash();
  const errors = E.validate(DATA);
  window.validateRoadmap = function () { return E.validate(DATA); };
  if (errors.length) console.warn("로드맵 검증", errors);
  try {
    localStorage.setItem(KEY, JSON.stringify(snapshot()));
  } catch (e) {
    console.warn("localStorage 저장 실패", e);
  }
  if (remoteSyncEnabled && (picked.source === "local" || !remoteState)) {
    sendRemote(JSON.stringify(snapshot()), false);
  }
  render();
}

async function loadData() {
  if (location.protocol === "file:") {
    fileHelp();
    return;
  }
  const manifest = await fetch("roadmap/manifest.json").then((r) => {
    if (!r.ok) throw new Error("manifest");
    return r.json();
  });
  if (!Array.isArray(manifest) || !manifest.length) throw new Error("manifest");
  const tracks = await Promise.all(manifest.map((name) => {
    if (!/^[\w.-]+\.json$/.test(name)) throw new Error("파일 이름");
    return fetch("roadmap/" + name).then((r) => {
      if (!r.ok) throw new Error(name);
      return r.json();
    });
  }));
  DATA = { tracks: tracks };
  await boot();
}

loadData().catch((err) => {
  document.getElementById("app").innerHTML = "<section class=\"file-help\"><h1>커리큘럼을 읽지 못했습니다</h1><p class=\"lead\">학습로드맵.bat 으로 이 폴더를 연 뒤 새로고침하세요.</p><p class=\"muted\">" + esc(err.message) + "</p></section>";
});
