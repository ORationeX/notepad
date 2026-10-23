(function (root) {
  const INTERVALS = [1, 3, 7, 16, 35, 70];

  function parseISO(s) {
    const [y, m, d] = String(s).split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  function fmt(d) {
    const z = (n) => String(n).padStart(2, "0");
    return d.getFullYear() + "-" + z(d.getMonth() + 1) + "-" + z(d.getDate());
  }
  function addDaysISO(iso, n) {
    const x = parseISO(iso);
    x.setDate(x.getDate() + n);
    return fmt(x);
  }
  function trackDayCount(track) {
    return track.weeks.reduce((n, w) => n + w.days.length, 0);
  }
  function posFromOffset(track, off) {
    if (off < 0) return null;
    let left = off;
    for (let w = 0; w < track.weeks.length; w++) {
      const n = track.weeks[w].days.length;
      if (left < n) return { week: w + 1, day: left };
      left -= n;
    }
    return null;
  }
  function dateOf(track, start, week, day) {
    let idx = day;
    for (let w = 0; w < week - 1; w++) idx += track.weeks[w].days.length;
    return addDaysISO(start, idx);
  }
  function offsetOf(start, todayISO) {
    return Math.round((parseISO(todayISO) - parseISO(start)) / 86400000);
  }
  function blankState(start) {
    return {
      v: 3,
      start: start,
      done: {},
      pass: {},
      skip: {},
      why: {},
      stuck: {},
      cards: {},
      activity: {},
      deferred: {},
      track: "en",
      week: 1,
      view: "home",
      q: "",
      iq: ""
    };
  }
  function weekCardId(trackId, week) { return trackId + ":w:" + week; }
  function dayCardId(trackId, week, day) { return trackId + ":d:" + week + ":" + day; }
  function sessionId(trackId, week, day) { return trackId + ":" + week + ":" + day; }

  function migrateV1(saved, todayISO) {
    const state = blankState(saved.start || todayISO);
    state.done = saved.done || {};
    state.pass = saved.pass || {};
    if (saved.track) state.track = saved.track;
    if (saved.week) state.week = saved.week;
    if (saved.view === "home" || saved.view === "track" || saved.view === "index") state.view = saved.view;
    Object.keys(state.pass).forEach((key) => {
      const parts = key.split(":");
      if (parts.length < 2) return;
      const trackId = parts[0];
      const week = Number(parts[1]);
      if (!trackId || !week) return;
      const when = String(state.pass[key] || "");
      const base = /^\d{4}-\d{2}-\d{2}$/.test(when) ? when : todayISO;
      let due = addDaysISO(base, INTERVALS[1]);
      if (due < todayISO) due = todayISO;
      const id = weekCardId(trackId, week);
      state.cards[id] = { id: id, kind: "week", track: trackId, week: week, step: 1, due: due, phase: "prompt" };
    });
    return state;
  }

  function studyPos(track, offset, state) {
    const total = trackDayCount(track);
    if (offset < 0 || offset >= total) return null;
    const cal = posFromOffset(track, offset);
    if (cal.week > 1 && !state.pass[track.id + ":" + (cal.week - 1)]) {
      const prev = cal.week - 1;
      const n = track.weeks[prev - 1].days.length;
      for (let d = 0; d < n; d++) {
        if (!state.done[sessionId(track.id, prev, d)]) return { week: prev, day: d, repair: true, calendar: cal };
      }
      return { week: prev, day: n - 1, repair: true, calendar: cal };
    }
    return { week: cal.week, day: cal.day, repair: false, calendar: cal };
  }

  function dueCards(state, trackId, todayISO) {
    return Object.keys(state.cards).map((id) => state.cards[id]).filter((c) => c && c.track === trackId && c.due <= todayISO);
  }

  function takeQueue(cards) {
    const sorted = cards.slice().sort((a, b) => a.due.localeCompare(b.due) || a.week - b.week || (a.kind === b.kind ? 0 : a.kind === "day" ? -1 : 1) || String(a.id).localeCompare(String(b.id)));
    const shown = [];
    const weeks = new Set();
    const defer = [];
    sorted.forEach((card) => {
      if (shown.length >= 2 || weeks.has(card.week)) defer.push(card);
      else {
        shown.push(card);
        weeks.add(card.week);
      }
    });
    return { shown: shown, defer: defer };
  }

  function commitAnswer(card) {
    const phase = card.phase || "prompt";
    if (phase === "prompt") card.phase = "reveal";
    else if (phase === "retry") card.phase = "retryReveal";
    else return false;
    return true;
  }

  function grade(card, correct, todayISO) {
    const phase = card.phase || "prompt";
    if (phase !== "reveal" && phase !== "retryReveal") return { ok: false };
    const second = phase === "retryReveal";
    if (correct) {
      card.step = Math.min(card.step + 1, INTERVALS.length - 1);
      card.due = addDaysISO(todayISO, INTERVALS[card.step]);
      card.phase = "prompt";
      return { ok: true, result: "success" };
    }
    if (!second) {
      card.phase = "retry";
      return { ok: true, result: "retry" };
    }
    card.step = card.kind === "week" ? 1 : 0;
    card.due = addDaysISO(todayISO, INTERVALS[card.step]);
    card.phase = "prompt";
    return { ok: true, result: "fail" };
  }

  function scheduleWeek(state, trackId, week, todayISO, reset) {
    const id = weekCardId(trackId, week);
    if (state.cards[id] && !reset) return state.cards[id];
    state.cards[id] = {
      id: id,
      kind: "week",
      track: trackId,
      week: Number(week),
      step: 1,
      due: addDaysISO(todayISO, INTERVALS[1]),
      phase: "prompt"
    };
    return state.cards[id];
  }

  function scheduleStuck(state, trackId, week, day, line, fromISO, todayISO) {
    const id = dayCardId(trackId, week, day);
    let due = addDaysISO(fromISO, 1);
    if (due < todayISO) due = todayISO;
    state.cards[id] = {
      id: id,
      kind: "day",
      track: trackId,
      week: Number(week),
      day: Number(day),
      line: line,
      step: 0,
      due: due,
      phase: "prompt"
    };
    state.stuck[sessionId(trackId, week, day)] = line;
    return state.cards[id];
  }

  function isActive(state, iso) {
    if (state.activity && state.activity[iso]) return true;
    return Object.keys(state.done).some((k) => state.done[k] === iso);
  }
  function streak(state, todayISO) {
    let d = todayISO;
    if (!isActive(state, d)) d = addDaysISO(d, -1);
    let n = 0;
    while (d >= state.start && isActive(state, d)) {
      n += 1;
      d = addDaysISO(d, -1);
      if (n > 4000) break;
    }
    return n;
  }

  function validate(data) {
    const errors = [];
    if (!data || !data.tracks || !data.tracks.length) {
      errors.push("tracks");
      return errors;
    }
    const ids = new Set();
    data.tracks.forEach((tr) => {
      if (!tr.id || ids.has(tr.id)) errors.push("id " + (tr.id || "?"));
      ids.add(tr.id);
      if (!tr.color) errors.push(tr.id + " color");
      if (!tr.weeks || !tr.weeks.length) errors.push(tr.id + " weeks");
      if (!tr.phases || !tr.phases.length) errors.push(tr.id + " phases");
      (tr.weeks || []).forEach((w, i) => {
        if (!w.days || !w.days.length) errors.push(tr.id + " w" + (i + 1) + " days");
        if (!w.check) errors.push(tr.id + " w" + (i + 1) + " check");
        (w.days || []).forEach((d) => {
          const sum = (d.blocks || []).reduce((a, b) => a + Number(b.m), 0);
          if (sum !== 60) errors.push(tr.id + " w" + (i + 1) + " " + (d.title || "") + " " + sum);
        });
      });
    });
    return errors;
  }

  root.RoadmapEngine = {
    INTERVALS: INTERVALS,
    parseISO: parseISO,
    fmt: fmt,
    addDaysISO: addDaysISO,
    trackDayCount: trackDayCount,
    posFromOffset: posFromOffset,
    dateOf: dateOf,
    offsetOf: offsetOf,
    blankState: blankState,
    weekCardId: weekCardId,
    dayCardId: dayCardId,
    sessionId: sessionId,
    migrateV1: migrateV1,
    studyPos: studyPos,
    dueCards: dueCards,
    takeQueue: takeQueue,
    commitAnswer: commitAnswer,
    grade: grade,
    scheduleWeek: scheduleWeek,
    scheduleStuck: scheduleStuck,
    isActive: isActive,
    streak: streak,
    validate: validate
  };
})(typeof globalThis !== "undefined" ? globalThis : this);
