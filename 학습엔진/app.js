const KEY = "roadmap-year-v3";
const LEGACY = "roadmap-year-v1";
const PREV = "roadmap-year-v2";
const E = window.RoadmapEngine;

let DATA = { tracks: [] };
let state = null;

function todayISO() { return E.fmt(new Date()); }
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function trackById(id) { return DATA.tracks.find((t) => t.id === id); }
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
    done: state.done,
    pass: state.pass,
    skip: state.skip,
    why: state.why,
    stuck: state.stuck,
    cards: state.cards,
    activity: state.activity,
    deferred: state.deferred,
    track: state.track,
    week: state.week,
    view: state.view,
    q: state.q || "",
    iq: state.iq || ""
  };
}
function persist() { localStorage.setItem(KEY, JSON.stringify(snapshot())); }
function normalize(saved) {
  const s = E.blankState(saved.start || todayISO());
  ["done", "pass", "skip", "why", "stuck", "cards", "activity", "deferred"].forEach((k) => {
    if (saved[k] && typeof saved[k] === "object") s[k] = saved[k];
  });
  if (saved.track) s.track = saved.track;
  if (saved.week) s.week = saved.week;
  if (saved.view) s.view = saved.view;
  s.q = saved.q || "";
  s.iq = saved.iq || "";
  return s;
}
function freshFrom(saved) {
  const start = saved && typeof saved.start === "string" ? saved.start : todayISO();
  return E.blankState(start);
}
function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return normalize(JSON.parse(raw));
  } catch (err) { /* 새 기록 */ }
  for (const oldKey of [PREV, LEGACY]) {
    try {
      const old = localStorage.getItem(oldKey);
      if (old) return freshFrom(JSON.parse(old));
    } catch (err) { /* 이전 기록 없음 */ }
  }
  return E.blankState(todayISO());
}
function needsRecord(tr) { return tr.confirm === "record"; }
function weekDoneCount(tr, week) {
  const n = tr.weeks[week - 1].days.length;
  let c = 0;
  for (let d = 0; d < n; d++) if (state.done[E.sessionId(tr.id, week, d)]) c += 1;
  return c;
}
function summary() {
  const hours = DATA.tracks.map((tr) => E.trackDayCount(tr));
  const weeks = DATA.tracks.map((tr) => tr.weeks.length);
  const phases = DATA.tracks.map((tr) => tr.phases.length);
  const same = (arr) => arr.every((n) => n === arr[0]);
  return {
    hours: same(hours) ? String(hours[0]) : "트랙별",
    hoursSub: same(hours) ? "도메인당 시간" : DATA.tracks.map((tr, i) => tr.name + " " + hours[i]).join(" · "),
    parallel: String(DATA.tracks.length),
    weeks: same(weeks) ? String(weeks[0]) : "트랙별",
    weeksSub: same(phases) ? "주 · " + phases[0] + "단계" : "주 · 단계",
    sessions: hours.reduce((a, b) => a + b, 0),
    samePhases: same(phases)
  };
}
function offsetToday() { return E.offsetOf(state.start, todayISO()); }
function studyFor(tr) { return E.studyPos(tr, offsetToday(), state); }
function prepareQueues() {
  const today = todayISO();
  let changed = false;
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
    const tomorrow = E.addDaysISO(today, 1);
    q.defer.forEach((card) => {
      card.due = tomorrow;
      card.phase = "prompt";
    });
    state.deferred[key] = (state.deferred[key] || 0) + q.defer.length;
    changed = true;
  });
  if (changed) persist();
}
function shownReviews(tr) { return E.takeQueue(E.dueCards(state, tr.id, todayISO())).shown; }
function reviewCount() { return DATA.tracks.reduce((n, tr) => n + shownReviews(tr).length, 0); }

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
  const head = card.kind === "week"
    ? card.week + "주 · " + week.title
    : card.week + "주 " + (card.day + 1) + "일차 · " + ((week.days[card.day] && week.days[card.day].title) || "");
  const cue = card.kind === "week" ? week.check : (card.line || "");
  const answer = revealed && card.kind === "week"
    ? "<div class=\"answer\"><b>산출물과 대조</b><p>" + esc(week.outcome) + "</p></div>"
    : revealed
      ? "<div class=\"answer\"><b>대조</b><p>방금 말한 내용이 이 줄을 넘었으면 맞음입니다. 수업 블록은 열지 않습니다.</p></div>"
      : "";
  const buttons = revealed
    ? "<button class=\"btn primary\" type=\"button\" data-act=\"recall-yes\" data-card=\"" + esc(card.id) + "\">맞음</button><button class=\"btn\" type=\"button\" data-act=\"recall-no\" data-card=\"" + esc(card.id) + "\">틀림</button>"
    : "<button class=\"btn primary\" type=\"button\" data-act=\"recall-commit\" data-card=\"" + esc(card.id) + "\">답을 냈다</button>";
  return "<article class=\"recall\"><p class=\"kicker\">" + (retry ? "한 번 더 · " : "복습 · ") + esc(head) + "</p><p>" + esc(cue) + "</p>" + answer + "<div class=\"row\">" + buttons + "</div></article>";
}
function reviewSection(tr) {
  const shown = shownReviews(tr);
  const deferred = state.deferred[tr.id + ":" + todayISO()] || 0;
  if (!shown.length && !deferred) return "";
  const note = deferred ? "<p class=\"defer-note muted\">같은 주이거나 오늘 칸을 넘긴 " + deferred + "장은 내일로 넘겼습니다.</p>" : "";
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
  const record = english ? "<label><input type=\"checkbox\" data-field=\"record\"" + (draft.record ? " checked" : "") + "> 녹음이나 초고가 남았다</label>" : "";
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
  state.week = n >= 1 && n <= tr.weeks.length ? n : 1;
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
  document.getElementById("statLine").textContent = "세션 " + Object.keys(state.done).length + "/" + info.sessions + " · 복습 " + reviewCount() + " · 연속 " + E.streak(state, todayISO()) + "일";
  applyAccent();
}

function todayCard(tr) {
  const off = offsetToday();
  const reviews = reviewSection(tr);
  const deferred = state.deferred[tr.id + ":" + todayISO()] || 0;
  const waiting = shownReviews(tr).length;
  const status = "복습 " + waiting + "장" + (deferred ? " · 내일 " + deferred + "장" : "");
  if (off < 0) {
    return "<article class=\"today\" style=\"--c:" + esc(tr.color) + "\"><p class=\"kicker\">" + esc(tr.name) + " · " + status + "</p><h3>시작 전</h3><p>시작일 전에 노트와 녹음만 준비하면 됩니다.</p>" + reviews + "</article>";
  }
  if (off >= E.trackDayCount(tr)) {
    return "<article class=\"today\" style=\"--c:" + esc(tr.color) + "\"><p class=\"kicker\">" + esc(tr.name) + " · " + status + "</p><h3>일정이 끝났습니다</h3><p>" + esc(tr.after) + "</p>" + reviews + "<div class=\"row\"><button class=\"btn\" type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + tr.weeks.length + "\">마지막 주</button></div></article>";
  }
  const pos = studyFor(tr);
  const week = tr.weeks[pos.week - 1];
  const day = week.days[pos.day];
  const when = E.dateOf(tr, state.start, pos.week, pos.day);
  const done = !!state.done[E.sessionId(tr.id, pos.week, pos.day)];
  const repair = pos.repair ? "<p class=\"err\">이전 주가 미통과입니다. 오늘은 " + pos.week + "주 " + (pos.day + 1) + "일차를 합니다.</p>" : "";
  return "<article class=\"today\" style=\"--c:" + esc(tr.color) + "\"><p class=\"kicker\">" + esc(tr.name) + " · " + status + "</p><h3>" + esc(day.title) + "</h3><p class=\"when\">" + esc(when) + " · " + pos.week + "주 " + (pos.day + 1) + "일차 · " + (done ? "학습 완료" : "학습 전") + "</p>" + repair + reviews + "<div class=\"row\"><button class=\"btn\" type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + pos.week + "\">계획 열기</button>" + passControls(tr, pos.week) + "</div>" + doneForm(tr, pos.week, pos.day) + "</article>";
}

function renderHome() {
  const info = summary();
  const off = offsetToday();
  const where = off < 0 ? "시작 전" : "오늘";
  let map = "";
  if (info.samePhases) {
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
    map = DATA.tracks.map((tr) => "<h3 class=\"track-label\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</h3><div class=\"map map-solo\">" + tr.phases.map((p) => "<button type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + p.start + "\"><em style=\"color:" + esc(tr.color) + "\">" + esc(p.from) + " → " + esc(p.to) + "</em><strong>" + esc(p.name) + "</strong><small>" + p.start + "–" + p.end + "주 · " + esc(p.result) + "</small></button>").join("") + "</div>").join("");
  }
  const whereDetail = (function () {
    const hours = DATA.tracks.map((tr) => E.trackDayCount(tr));
    if (!hours.every((n) => n === hours[0])) return off < 0 ? "시작 전" : "시작 후 " + Math.max(0, off) + "일";
    if (off < 0) return "시작 전";
    if (off >= hours[0]) return "일정 끝";
    const pos = E.posFromOffset(DATA.tracks[0], off);
    return pos.week + "주차 " + (pos.day + 1) + "일차";
  })();
  return [
    "<section class=\"hero\">",
    "<p class=\"kicker\">오늘 위치 · " + esc(whereDetail) + "</p>",
    "<h1>하루 한 시간씩, 세 번.</h1>",
    "<p class=\"lead\">영어 7년, 수학 5년, 알고리즘 7년입니다. 하루 60분이고, 첫 10분은 기한이 된 복습입니다. 없으면 그 주에 적힌 어제 회상입니다. 세 도메인을 같은 날에 하면 하루 합계는 " + info.parallel + "시간입니다.</p>",
    "<div class=\"hero-stats\"><div><b>" + esc(info.hours) + "</b><span>" + esc(info.hoursSub) + "</span></div><div><b>" + esc(info.parallel) + "</b><span>병렬이면 하루 시간</span></div><div><b>" + esc(info.weeks) + "</b><span>" + esc(info.weeksSub) + "</span></div><div><b>" + info.sessions.toLocaleString("ko-KR") + "</b><span>전체 세션</span></div></div>",
    "</section>",
    "<section class=\"section\"><h2>오늘</h2><p class=\"muted\">" + esc(where) + " · 복습은 답을 낸 뒤에만 맞음과 틀림이 열립니다. 한 도메인에는 서로 다른 주 두 장까지입니다.</p><div class=\"today-grid\">" + DATA.tracks.map(todayCard).join("") + "</div></section>",
    "<section class=\"section\"><h2>전체 지도</h2><p class=\"muted\">칸을 누르면 그 단계의 첫 주로 갑니다. 1년 뒤에는 분기마다 한 칸입니다.</p>" + map + "</section>",
    "<section class=\"section\"><h2>60분을 쓰는 방법</h2><div class=\"principles\">" + DATA.tracks.map((tr) => "<article class=\"hour\"><p class=\"kicker\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</p><h3>" + esc(tr.hourTitle) + "</h3>" + hourList(tr.hour) + "</article>").join("") + "</div></section>",
    "<section class=\"section prep\"><h2>시작 전 60분</h2><p>노트 세 칸(영어·알고리즘·수학)과 녹음 앱을 준비합니다. 계산기, 파이썬, Anki는 1주차 지시가 나오기 전에 미리 깔아 두지 않아도 됩니다. 매일 같은 시각에 영어 60분, 수학 60분, 알고리즘 60분 순으로 캘린더에 넣고, 세션 사이에 10분 쉽니다. 말이 나오는 시간을 영어에 두는 편이 좋습니다.</p></section>",
    "<section class=\"section\"><h2>과정의 끝</h2><div class=\"dest-grid\">" + DATA.tracks.map((tr) => "<article class=\"dest\"><p class=\"kicker\" style=\"color:" + esc(tr.color) + "\">" + esc(tr.name) + "</p><h3>" + esc(tr.destination) + "</h3><p>" + esc(tr.limit) + "</p><p style=\"margin-top:8px\"><b>이후.</b> " + esc(tr.after) + "</p></article>").join("") + "</div></section>",
    "<section class=\"section\"><h2>공통 규칙</h2><div class=\"principles\"><article><h3>통과해야 다음 주다</h3><p>이전 주가 통과되기 전에는 달력의 새 주 대신, 그 주의 아직 안 끝난 날을 합니다. 알고 넘어가기는 한 번 더 확인한 뒤 3일 간격의 복습으로 남습니다.</p></article><article><h3>산출이 있어야 진도다</h3><p>영상을 보는 것으로 60분을 채우지 않습니다. 영어는 녹음이나 초고, 알고리즘과 수학은 왜 맞는지 한 문장이 있어야 완료입니다.</p></article><article><h3>기록은 이 브라우저에</h3><p>완료, 통과, 복습 기한은 이 기기에 저장됩니다. 컴퓨터를 바꾸기 전에 기록 메뉴에서 내보내 두십시오.</p></article></div></section>",
    "<p class=\"foot\">이 로드맵은 학습 계획입니다. 계약 영어는 문장을 읽고 고치는 언어 훈련이며 법률 자문이 아닙니다. 교재명은 그 책을 사야 한다는 뜻이 아니라, 그 주에 펼칠 출처입니다. 무료 자료를 우선 적었습니다.</p>"
  ].join("");
}

function weekListHTML(tr) {
  const q = (state.q || "").trim().toLowerCase();
  const phases = tr.phases.map((p) => {
    const buttons = [];
    for (let w = p.start; w <= p.end && w <= tr.weeks.length; w++) {
      const week = tr.weeks[w - 1];
      if (!week) continue;
      const blob = (week.title + " " + week.goal + " " + (week.ideas || []).map((i) => i[0] + " " + i[1]).join(" ") + " " + week.days.map((d) => d.title).join(" ")).toLowerCase();
      if (q && blob.indexOf(q) === -1) continue;
      const on = w === state.week;
      buttons.push("<button class=\"wbtn\" type=\"button\" data-act=\"week\" data-week=\"" + w + "\"" + (on ? " aria-current=\"page\"" : "") + ">" + w + ". " + esc(week.title) + "<span>" + weekDoneCount(tr, w) + "/" + week.days.length + "</span></button>");
    }
    if (!buttons.length) return "";
    const open = q || (state.week >= p.start && state.week <= p.end);
    return "<details" + (open ? " open" : "") + "><summary>" + esc(p.name) + " · " + p.start + "–" + p.end + "주</summary><div class=\"weekbtns\">" + buttons.join("") + "</div></details>";
  }).join("");
  return phases || "<p class=\"muted\">맞는 주가 없습니다.</p>";
}

function renderTrack() {
  const tr = trackById(state.track);
  const week = tr.weeks[state.week - 1];
  const phase = tr.phases.find((p) => state.week >= p.start && state.week <= p.end) || tr.phases[0];
  const study = studyFor(tr);
  const warn = state.week > 1 && !state.pass[tr.id + ":" + (state.week - 1)];
  const days = week.days.map((day, i) => {
    const when = E.dateOf(tr, state.start, state.week, i);
    const isStudy = study && study.week === state.week && study.day === i && offsetToday() >= 0 && offsetToday() < E.trackDayCount(tr);
    const id = E.sessionId(tr.id, state.week, i);
    const replaced = isStudy && shownReviews(tr).length > 0;
    return "<article class=\"day" + (isStudy ? " today" : "") + "\"><div><p class=\"when\">" + (i + 1) + "일차 · " + esc(when) + (isStudy ? " · 오늘 학습" : "") + (i === week.days.length - 1 ? " · 점검" : "") + "</p><h3>" + esc(day.title) + "</h3><div class=\"day-actions\">" + doneForm(tr, state.week, i) + "<button class=\"btn\" type=\"button\" data-act=\"timer\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + state.week + "\" data-day=\"" + i + "\">타이머</button></div></div>" + blocksHTML(day.blocks, replaced) + "</article>";
  }).join("");
  return [
    "<div class=\"layout\">",
    "<aside class=\"side noprint\"><input class=\"search\" id=\"q\" placeholder=\"개념, 주 제목 검색\" value=\"" + esc(state.q || "") + "\"><div id=\"weekList\">" + weekListHTML(tr) + "</div></aside>",
    "<section id=\"week\">",
    "<p class=\"kicker\">" + esc(phase.name) + " · " + esc(phase.from) + " → " + esc(phase.to) + "</p>",
    "<div class=\"week-head\"><h2><span class=\"min\">" + String(state.week).padStart(2, "0") + "</span> " + esc(week.title) + "</h2><p class=\"goal\">" + esc(week.goal) + "</p></div>",
    warn ? "<div class=\"banner\">이전 주 통과 표시가 없습니다. 오늘 본학습은 그 주의 아직 안 끝난 날로 돌아갑니다.</div>" : "",
    reviewSection(tr),
    "<div class=\"ideas\">" + (week.ideas || []).map((idea) => "<article class=\"idea\"><b>" + esc(idea[0]) + "</b>" + esc(idea[1]) + "</article>").join("") + "</div>",
    "<div class=\"meta\"><div><b>이번 주 산출물</b><small>" + esc(week.outcome) + "</small></div><div><b>펼칠 자료</b><small>" + esc(week.resource) + "</small></div><div><b>통과 기준</b><small>" + esc(week.check) + "</small></div></div>",
    "<div class=\"row noprint\">" + passControls(tr, state.week) + "<button class=\"btn\" type=\"button\" data-act=\"jump\" data-week=\"" + Math.max(1, state.week - 1) + "\">이전 주</button><button class=\"btn\" type=\"button\" data-act=\"jump\" data-week=\"" + Math.min(tr.weeks.length, state.week + 1) + "\">다음 주</button><button class=\"btn\" type=\"button\" data-act=\"today-jump\">오늘 학습으로</button></div>",
    days,
    "<p class=\"foot\">" + esc(tr.name) + " 단계 결과: " + esc(phase.result) + "</p>",
    "</section></div>"
  ].join("");
}

function renderIndex() {
  const q = (state.iq || "").trim().toLowerCase();
  const rows = [];
  DATA.tracks.forEach((tr) => {
    tr.weeks.forEach((week, wi) => {
      (week.ideas || []).forEach((idea) => {
        const blob = (tr.name + " " + week.title + " " + idea[0] + " " + idea[1]).toLowerCase();
        if (q && blob.indexOf(q) === -1) return;
        rows.push("<button type=\"button\" data-act=\"track\" data-track=\"" + esc(tr.id) + "\" data-week=\"" + (wi + 1) + "\"><small>" + esc(tr.name) + " · " + (wi + 1) + "주 " + esc(week.title) + "</small><br><b>" + esc(idea[0]) + "</b> " + esc(idea[1]) + "</button>");
      });
    });
  });
  return "<section><p class=\"kicker\">개념 색인</p><h2>과정에서 만나는 개념</h2><p class=\"muted\">용어를 누르면 그 주로 이동합니다. " + rows.length + "개.</p><input class=\"search\" id=\"indexQ\" placeholder=\"용어 검색\" value=\"" + esc(state.iq || "") + "\"><div class=\"index-list\">" + rows.join("") + "</div></section>";
}

function render(opts) {
  opts = opts || {};
  captureDrafts();
  prepareQueues();
  const y = opts.keepScroll ? window.scrollY : 0;
  const focusId = document.activeElement && document.activeElement.id;
  renderNav();
  const app = document.getElementById("app");
  if (!DATA.tracks.length) {
    app.textContent = "커리큘럼 데이터가 비어 있습니다.";
    return;
  }
  if (state.view === "home") app.innerHTML = renderHome();
  else if (state.view === "index") app.innerHTML = renderIndex();
  else app.innerHTML = renderTrack();
  if (focusId === "q" || focusId === "indexQ") {
    const el = document.getElementById(focusId);
    if (el) {
      el.focus();
      const n = el.value.length;
      el.setSelectionRange(n, n);
    }
  }
  window.scrollTo(0, opts.keepScroll ? y : 0);
}

function finishCard(card, correct) {
  const today = todayISO();
  const result = E.grade(card, correct, today);
  if (!result.ok) return;
  if (result.result === "success" || result.result === "fail") state.activity[today] = true;
  persist();
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
    state.error = { id: id, text: "녹음이나 초고가 남았는지 확인해 주세요." };
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
  state.activity[today] = true;
  if (!needsRecord(tr)) state.why[id] = String(draft.why).trim();
  if (draft.stuck) {
    const from = E.dateOf(tr, state.start, week, day);
    E.scheduleStuck(state, tr.id, week, day, String(draft.line).trim(), from, today);
  }
  delete state.drafts[id];
  state.error = null;
  persist();
  render({ keepScroll: true });
}
function togglePass(trackId, week, skip) {
  const tr = trackById(trackId);
  const key = trackId + ":" + week;
  const today = todayISO();
  if (!skip && state.pass[key]) {
    delete state.pass[key];
    delete state.skip[key];
    const card = state.cards[E.weekCardId(trackId, week)];
    if (card && card.step === 1 && (card.phase || "prompt") === "prompt") delete state.cards[card.id];
    persist();
    render({ keepScroll: true });
    return;
  }
  if (!skip && weekDoneCount(tr, week) < tr.weeks[week - 1].days.length) return;
  if (skip && !window.confirm("통과 기준을 충족하지 못한 채로 넘어갑니다. 이 주는 3일 뒤 복습으로 돌아옵니다. 계속할까요?")) return;
  state.pass[key] = today;
  if (skip) state.skip[key] = today;
  else delete state.skip[key];
  E.scheduleWeek(state, trackId, Number(week), today, !!skip);
  persist();
  render({ keepScroll: true });
}

const timer = { running: false, left: 0, blocks: [], index: 0, handle: 0, endAt: 0, label: "" };
function showDock() {
  const dock = document.getElementById("dock");
  const block = timer.blocks[timer.index];
  if (!block) { dock.hidden = true; document.body.classList.remove("timing"); return; }
  dock.hidden = false;
  document.body.classList.add("timing");
  const total = timer.blocks.reduce((a, b) => a + b.m, 0) * 60;
  const spent = timer.blocks.slice(0, timer.index).reduce((a, b) => a + b.m, 0) * 60 + (block.m * 60 - timer.left);
  document.getElementById("dockLabel").textContent = timer.label + " · " + block.m + "분 · " + block.t;
  const sec = Math.ceil(timer.left);
  document.getElementById("dockClock").textContent = String(Math.floor(sec / 60)).padStart(2, "0") + ":" + String(sec % 60).padStart(2, "0");
  document.getElementById("dockBar").style.width = Math.min(100, (spent / total) * 100) + "%";
  document.querySelector("[data-act='timer-toggle']").textContent = timer.running ? "일시정지" : "시작";
}
function beep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.frequency.value = 640;
    o.connect(g);
    g.connect(ctx.destination);
    g.gain.setValueAtTime(0.04, ctx.currentTime);
    o.start();
    o.stop(ctx.currentTime + 0.12);
  } catch (err) { /* 소리 없음 */ }
}
function tick() {
  if (!timer.running) return;
  timer.left = Math.max(0, (timer.endAt - Date.now()) / 1000);
  if (timer.left <= 0) {
    beep();
    if (timer.index < timer.blocks.length - 1) {
      timer.index += 1;
      timer.left = timer.blocks[timer.index].m * 60;
      timer.endAt = Date.now() + timer.left * 1000;
    } else {
      timer.running = false;
      timer.left = 0;
      clearInterval(timer.handle);
    }
  }
  showDock();
}
function startTimer(tr, week, day) {
  const source = tr.weeks[week - 1].days[day];
  const blocks = source.blocks.map((b) => ({ m: b.m, t: b.t }));
  const study = studyFor(tr);
  if (study && study.week === week && study.day === day && shownReviews(tr).length) {
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

document.body.addEventListener("click", (e) => {
  const t = e.target.closest("[data-act]");
  if (!t || !state) return;
  const act = t.dataset.act;
  if (act === "home") {
    state.view = "home";
    writeHash();
    persist();
    render();
  } else if (act === "index") {
    state.view = "index";
    writeHash();
    persist();
    render();
    const menu = document.querySelector(".menu");
    if (menu) menu.open = false;
  } else if (act === "track") {
    state.view = "track";
    state.track = t.dataset.track;
    if (t.dataset.week) state.week = Number(t.dataset.week);
    writeHash();
    persist();
    render();
  } else if (act === "week" || act === "jump") {
    state.week = Number(t.dataset.week);
    writeHash();
    persist();
    render();
  } else if (act === "today-jump") {
    const pos = studyFor(trackById(state.track));
    if (pos) state.week = pos.week;
    writeHash();
    persist();
    render();
  } else if (act === "done-clear") {
    delete state.done[t.dataset.id];
    persist();
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
      persist();
      render({ keepScroll: true });
    }
  } else if (act === "recall-yes" || act === "recall-no") {
    const card = state.cards[t.dataset.card];
    if (card) finishCard(card, act === "recall-yes");
  } else if (act === "timer") {
    startTimer(trackById(t.dataset.track), Number(t.dataset.week), Number(t.dataset.day));
  } else if (act === "timer-toggle") {
    if (!timer.blocks.length) return;
    timer.running = !timer.running;
    if (timer.running) {
      timer.endAt = Date.now() + timer.left * 1000;
      clearInterval(timer.handle);
      timer.handle = setInterval(tick, 250);
    } else clearInterval(timer.handle);
    showDock();
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
  } else if (act === "export") {
    const blob = new Blob([JSON.stringify(snapshot(), null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "roadmap-progress.json";
    a.click();
    URL.revokeObjectURL(a.href);
  } else if (act === "import") {
    document.getElementById("importFile").click();
  } else if (act === "reset") {
    if (confirm("이 브라우저의 완료 기록, 복습 일정, 시작일을 지울까요?")) {
      localStorage.removeItem(KEY);
      localStorage.removeItem(LEGACY);
      location.hash = "#/home";
      location.reload();
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
    render({ keepScroll: true });
  } else if (e.target.closest(".done-box")) {
    captureDrafts();
  }
});
document.getElementById("startDate").addEventListener("change", (e) => {
  if (!e.target.value || !state) return;
  state.start = e.target.value;
  persist();
  render({ keepScroll: true });
});
document.getElementById("importFile").addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      if (!data || typeof data !== "object") throw new Error("형식");
      state = data.v === 3 ? normalize(data) : freshFrom(data);
      state.drafts = {};
      state.error = null;
      if (!trackById(state.track)) state.track = DATA.tracks[0].id;
      persist();
      render();
    } catch (err) {
      alert("가져올 수 없는 파일입니다.");
    }
  };
  reader.readAsText(file);
  e.target.value = "";
});
document.addEventListener("keydown", (e) => {
  if (!state || e.target.matches("input, textarea") || state.view !== "track") return;
  const max = trackById(state.track).weeks.length;
  if (e.key === "[") state.week = Math.max(1, state.week - 1);
  else if (e.key === "]") state.week = Math.min(max, state.week + 1);
  else return;
  writeHash();
  persist();
  render();
});
window.addEventListener("hashchange", () => { if (!state) return; readHash(); render(); });

function fileHelp() {
  document.getElementById("app").innerHTML = "<section class=\"file-help\"><h1>커리큘럼을 읽지 못했습니다</h1><p class=\"lead\">이 주소는 파일로 직접 열려 있어 도메인 JSON을 불러올 수 없습니다. 같은 폴더의 학습로드맵.bat 을 실행한 뒤 열린 로컬 주소로 다시 들어오세요.</p></section>";
}
function boot() {
  state = load();
  state.drafts = {};
  state.error = null;
  if (!trackById(state.track)) state.track = DATA.tracks[0].id;
  const max = trackById(state.track).weeks.length;
  if (state.week < 1 || state.week > max) state.week = 1;
  if (location.hash) readHash();
  else writeHash();
  const errors = E.validate(DATA);
  window.validateRoadmap = function () { return E.validate(DATA); };
  if (errors.length) console.warn("로드맵 검증", errors);
  persist();
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
  const tracks = [];
  for (const name of manifest) {
    if (!/^[\w.-]+\.json$/.test(name)) throw new Error("파일 이름");
    const res = await fetch("roadmap/" + name);
    if (!res.ok) throw new Error(name);
    tracks.push(await res.json());
  }
  DATA = { tracks: tracks };
  boot();
}
loadData().catch((err) => {
  document.getElementById("app").innerHTML = "<section class=\"file-help\"><h1>커리큘럼을 읽지 못했습니다</h1><p class=\"lead\">학습로드맵.bat 으로 이 폴더를 연 뒤 새로고침하세요.</p><p class=\"muted\">" + esc(err.message) + "</p></section>";
});
