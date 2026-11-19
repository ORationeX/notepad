(function (root) {
  const INTERVALS = [1, 3, 7, 16, 35, 70, 180];

  function parseISO(s) {
    const [y, m, d] = String(s).split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  function fmt(d) {
    const z = (n) => String(n).padStart(2, "0");
    return d.getFullYear() + "-" + z(d.getMonth() + 1) + "-" + z(d.getDate());
  }
  function isValidISO(s) {
    if (typeof s !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
    const d = parseISO(s);
    return !isNaN(d.getTime()) && fmt(d) === s;
  }
  function addDaysISO(iso, n) {
    if (!isValidISO(iso)) return "";
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
    if (!isValidISO(start)) return "";
    let idx = day;
    for (let w = 0; w < week - 1; w++) idx += track.weeks[w].days.length;
    return addDaysISO(start, idx);
  }
  function offsetOf(start, todayISO) {
    if (!isValidISO(start) || !isValidISO(todayISO)) return 0;
    return Math.round((parseISO(todayISO) - parseISO(start)) / 86400000);
  }
  function blankState(start) {
    return {
      v: 3,
      start: start,
      starts: {},
      done: {},
      pass: {},
      skip: {},
      why: {},
      stuck: {},
      cards: {},
      activity: {},
      deferred: {},
      reviewed: {},
      track: "en",
      week: 1,
      view: "home",
      q: "",
      iq: "",
      updatedAt: 0
    };
  }
  function trackStart(state, trackId) {
    if (state && state.starts && isValidISO(state.starts[trackId])) return state.starts[trackId];
    return state ? state.start : "";
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
      const base = isValidISO(when) ? when : todayISO;
      let due = addDaysISO(base, INTERVALS[1]);
      if (due < todayISO) due = todayISO;
      const id = weekCardId(trackId, week);
      state.cards[id] = { id: id, kind: "week", track: trackId, week: week, step: 1, due: due, phase: "prompt" };
    });
    return state;
  }

  function firstUndoneDay(track, state, week) {
    const n = track.weeks[week - 1].days.length;
    for (let d = 0; d < n; d++) {
      if (!state.done[sessionId(track.id, week, d)]) return d;
    }
    return n - 1;
  }

  function firstUnpassedWeek(track, state) {
    for (let w = 1; w <= track.weeks.length; w++) {
      if (!state.pass[track.id + ":" + w]) return w;
    }
    return null;
  }

  function studyPos(track, offset, state) {
    if (!track || !track.weeks || !track.weeks.length) return null;
    if (offset === null || offset === undefined || typeof offset !== "number" || !isFinite(offset) || offset < 0) return null;
    const total = trackDayCount(track);
    const unpassed = firstUnpassedWeek(track, state);
    if (offset >= total) {
      if (unpassed === null) {
        const lastW = track.weeks.length;
        const lastD = track.weeks[lastW - 1].days.length - 1;
        return { week: lastW, day: lastD, repair: false, completed: true, calendar: null };
      }
      return { week: unpassed, day: firstUndoneDay(track, state, unpassed), repair: true, overtime: true, calendar: null };
    }
    const cal = posFromOffset(track, offset);
    if (unpassed === null) {
      const lastW = track.weeks.length;
      const lastD = track.weeks[lastW - 1].days.length - 1;
      return { week: lastW, day: lastD, repair: false, completed: true, calendar: cal };
    }
    if (unpassed < cal.week) {
      return { week: unpassed, day: firstUndoneDay(track, state, unpassed), repair: true, calendar: cal };
    }
    if (unpassed > cal.week) {
      return { week: unpassed, day: firstUndoneDay(track, state, unpassed), repair: false, skippedAhead: true, calendar: cal };
    }
    return { week: cal.week, day: cal.day, repair: false, calendar: cal };
  }

  function dueCards(state, trackId, todayISO) {
    return Object.keys(state.cards)
      .map((id) => state.cards[id])
      .filter((c) => c && !c.retired && c.track === trackId && c.due && c.due <= todayISO);
  }

  function phaseRank(card) {
    const p = card && card.phase;
    if (p === "reveal" || p === "retryReveal") return 0;
    if (p === "retry") return 1;
    return 2;
  }

  function takeQueue(cards) {
    const sorted = cards.slice().sort((a, b) => {
      const rp = phaseRank(a) - phaseRank(b);
      if (rp) return rp;
      const ad = a.origDue || a.due || "";
      const bd = b.origDue || b.due || "";
      return ad.localeCompare(bd) ||
        (a.due || "").localeCompare(b.due || "") ||
        a.week - b.week ||
        (a.kind === b.kind ? 0 : a.kind === "day" ? -1 : 1) ||
        String(a.id).localeCompare(String(b.id));
    });
    const shown = [];
    const defer = [];
    if (sorted.length) {
      shown.push(sorted[0]);
      const diffCandidates = [];
      for (let i = 1; i < sorted.length; i++) {
        if (sorted[i].week !== sorted[0].week) diffCandidates.push(sorted[i]);
      }
      let second = null;
      if (diffCandidates.length) {
        if (phaseRank(diffCandidates[0]) < 2 || diffCandidates.length === 1) {
          second = diffCandidates[0];
        } else {
          const topDue = diffCandidates[0].origDue || diffCandidates[0].due || "";
          second = diffCandidates.find((c) => (c.origDue || c.due || "") === topDue && Math.abs(c.week - sorted[0].week) >= 2) || diffCandidates[0];
        }
      }
      if (second) shown.push(second);
      for (let i = 1; i < sorted.length; i++) {
        if (sorted[i] !== second) defer.push(sorted[i]);
      }
    }
    return { shown: shown, defer: defer };
  }

  function deferCards(cards, todayISO) {
    cards.forEach((card, idx) => {
      const shift = 1 + Math.floor(idx / 2);
      if (!card.origDue && card.due) card.origDue = card.due;
      card.due = addDaysISO(todayISO, shift);
      card.phase = (card.phase === "retry" || card.phase === "retryReveal") ? "retry" : "prompt";
    });
  }

  function commitAnswer(card) {
    const phase = card.phase || "prompt";
    if (phase === "prompt") card.phase = "reveal";
    else if (phase === "retry") card.phase = "retryReveal";
    else return false;
    return true;
  }

  function clampEase(val) {
    return Math.max(1.3, Math.min(2.6, +Number(val).toFixed(2)));
  }

  function scaledInterval(step, ease, mult) {
    const m = typeof mult === "number" && isFinite(mult) ? mult : 1.0;
    return Math.max(1, Math.round(INTERVALS[step] * (ease / 2.0) * m));
  }

  function normalizeRating(rating) {
    if (rating === true) return "good";
    if (rating === false) return "again";
    if (rating === "again" || rating === "hard" || rating === "good" || rating === "easy") return rating;
    return null;
  }

  function grade(card, rating, todayISO) {
    const q = normalizeRating(rating);
    if (!q) return { ok: false };
    const phase = card.phase || "prompt";
    if (phase !== "reveal" && phase !== "retryReveal") return { ok: false };
    card.step = Number.isInteger(card.step)
      ? Math.max(0, Math.min(card.step, INTERVALS.length - 1))
      : (card.kind === "week" ? 1 : 0);
    card.ease = (typeof card.ease === "number" && isFinite(card.ease)) ? clampEase(card.ease) : 2.0;
    card.lapses = Number.isInteger(card.lapses) && card.lapses >= 0 ? card.lapses : 0;
    card.reviews = Number.isInteger(card.reviews) && card.reviews >= 0 ? card.reviews : 0;
    const second = phase === "retryReveal";

    if (q === "again") {
      if (!second) {
        card.phase = "retry";
        return { ok: true, result: "retry" };
      }
      card.lapses += 1;
      card.reviews += 1;
      card.ease = clampEase(card.ease - 0.2);
      card.leech = card.lapses >= 4;
      card.lastQuality = "again";
      const baseStep = card.kind === "week" ? 1 : 0;
      if (card.step >= 3 && card.lapses === 1) {
        card.step = Math.max(baseStep, card.step - 2);
      } else {
        card.step = baseStep;
      }
      let days = scaledInterval(card.step, card.ease, 1.0);
      if (card.step === baseStep) days = Math.min(INTERVALS[baseStep], days);
      card.retired = false;
      card.due = addDaysISO(todayISO, days);
      delete card.origDue;
      card.phase = "prompt";
      return { ok: true, result: "fail" };
    }

    card.reviews += 1;
    card.lastQuality = q;

    if (q === "hard") {
      card.ease = clampEase(card.ease - 0.1);
      if (card.step === 0) card.step = 1;
      card.retired = false;
      card.due = addDaysISO(todayISO, scaledInterval(card.step, card.ease, 0.75));
      delete card.origDue;
      card.phase = "prompt";
      return { ok: true, result: "success", graduated: false };
    }

    if (q === "easy") {
      card.ease = clampEase(card.ease + 0.15);
      if (!second && card.step >= INTERVALS.length - 2) {
        card.retired = true;
        card.due = null;
        delete card.origDue;
        card.phase = "prompt";
        return { ok: true, result: "success", graduated: true };
      }
      if (!second) {
        card.step = Math.min(INTERVALS.length - 1, card.step + (card.step <= 2 ? 2 : 1));
      } else {
        card.step = Math.min(INTERVALS.length - 1, card.step + 1);
      }
      card.retired = false;
      card.due = addDaysISO(todayISO, scaledInterval(card.step, card.ease, 1.0));
      delete card.origDue;
      card.phase = "prompt";
      return { ok: true, result: "success", graduated: false };
    }

    // q === "good"
    if (card.ease < 2.0) card.ease = Math.min(2.0, +(card.ease + 0.05).toFixed(2));
    if (!second) {
      if (card.step >= INTERVALS.length - 1) {
        card.retired = true;
        card.due = null;
        delete card.origDue;
        card.phase = "prompt";
        return { ok: true, result: "success", graduated: true };
      }
      card.step += 1;
    } else if (card.step === 0) {
      card.step = 1;
    }
    card.retired = false;
    card.due = addDaysISO(todayISO, scaledInterval(card.step, card.ease, 1.0));
    delete card.origDue;
    card.phase = "prompt";
    return { ok: true, result: "success", graduated: false };
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
      phase: "prompt",
      retired: false,
      ease: 2.0,
      lapses: 0,
      reviews: 0,
      leech: false
    };
    return state.cards[id];
  }

  function scheduleStuck(state, trackId, week, day, line, fromISO, todayISO) {
    const id = dayCardId(trackId, week, day);
    let due = isValidISO(fromISO) ? addDaysISO(fromISO, 1) : addDaysISO(todayISO, 1);
    if (due < todayISO) due = todayISO;
    const tomorrow = addDaysISO(todayISO, 1);
    if (due > tomorrow) due = tomorrow;
    state.cards[id] = {
      id: id,
      kind: "day",
      track: trackId,
      week: Number(week),
      day: Number(day),
      line: line,
      step: 0,
      due: due,
      phase: "prompt",
      retired: false,
      ease: 2.0,
      lapses: 0,
      reviews: 0,
      leech: false
    };
    state.stuck[sessionId(trackId, week, day)] = line;
    return state.cards[id];
  }

  function weeklyConsistency(state, todayISO, targetDays) {
    const target = Number.isInteger(targetDays) && targetDays >= 1 && targetDays <= 7 ? targetDays : 5;
    if (!isValidISO(todayISO)) return { activeLast7: 0, targetDays: target, consecutiveWeeks: 0 };
    const activeDates = new Set();
    Object.keys((state && state.done) || {}).forEach((k) => {
      const d = state.done[k];
      if (isValidISO(d)) activeDates.add(d);
    });
    Object.keys((state && state.activity) || {}).forEach((d) => {
      if (state.activity[d] && isValidISO(d)) activeDates.add(d);
    });
    const countWindow = (endISO) => {
      let c = 0;
      for (let i = 0; i < 7; i++) {
        if (activeDates.has(addDaysISO(endISO, -i))) c += 1;
      }
      return c;
    };
    const activeLast7 = countWindow(todayISO);
    let cursor = activeLast7 >= target ? todayISO : addDaysISO(todayISO, -7);
    let consecutiveWeeks = 0;
    for (let w = 0; w < 400; w++) {
      if (countWindow(cursor) >= target) {
        consecutiveWeeks += 1;
        cursor = addDaysISO(cursor, -7);
      } else {
        break;
      }
    }
    return { activeLast7: activeLast7, targetDays: target, consecutiveWeeks: consecutiveWeeks };
  }

  function applyDiagnosticPlacement(track, state, unitIds, todayISO) {
    if (!track || !state || !Array.isArray(track.units) || !Array.isArray(unitIds) || !isValidISO(todayISO)) {
      return { skippedWeeks: 0, seededCards: 0 };
    }
    const wanted = new Set(unitIds);
    let skippedWeeks = 0;
    let seededCards = 0;
    let phaseOffset = 0;
    state.pass = state.pass || {};
    state.skip = state.skip || {};
    state.cards = state.cards || {};
    track.units.forEach((u) => {
      if (!u || !wanted.has(u.id)) return;
      const startW = Math.max(1, Number(u.start) || 1);
      const endW = Math.min(track.weeks.length, Number(u.end) || 0);
      for (let w = startW; w <= endW; w++) {
        const key = track.id + ":" + w;
        if (!state.pass[key]) {
          state.pass[key] = todayISO;
          state.skip[key] = todayISO;
          skippedWeeks += 1;
        }
      }
      (u.phases || []).forEach((pi) => {
        const p = track.phases && track.phases[pi];
        if (!p || !Number.isInteger(p.end) || p.end < 1 || p.end > track.weeks.length) return;
        const id = weekCardId(track.id, p.end);
        if (!state.cards[id]) {
          const baseInt = INTERVALS[1 + (phaseOffset % 3)];
          state.cards[id] = {
            id: id,
            kind: "week",
            track: track.id,
            week: Number(p.end),
            step: 1,
            due: addDaysISO(todayISO, baseInt + phaseOffset * 2),
            phase: "prompt",
            retired: false,
            ease: 2.0,
            lapses: 0,
            reviews: 0,
            leech: false
          };
          seededCards += 1;
          phaseOffset += 1;
        }
      });
    });
    return { skippedWeeks: skippedWeeks, seededCards: seededCards };
  }

  function minStartISO(state) {
    const candidates = [];
    if (state && isValidISO(state.start)) candidates.push(state.start);
    if (state && state.starts) {
      Object.keys(state.starts).forEach((k) => {
        if (isValidISO(state.starts[k])) candidates.push(state.starts[k]);
      });
    }
    if (!candidates.length) return "";
    return candidates.reduce((a, b) => (a < b ? a : b));
  }

  function isActive(state, iso) {
    if (state.activity && state.activity[iso]) return true;
    return Object.keys(state.done || {}).some((k) => state.done[k] === iso);
  }
  function streak(state, todayISO) {
    const minStart = minStartISO(state);
    if (!minStart || !isValidISO(todayISO)) return 0;
    const doneDates = new Set();
    Object.keys(state.done || {}).forEach((k) => {
      if (state.done[k]) doneDates.add(state.done[k]);
    });
    const active = (iso) => !!(state.activity && state.activity[iso]) || doneDates.has(iso);
    let d = todayISO;
    if (!active(d)) d = addDaysISO(d, -1);
    let n = 0;
    while (d && active(d)) {
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
      let prevEnd = 0;
      let hasPhaseBounds = false;
      (tr.phases || []).forEach((p, pi) => {
        if (typeof p.start === "number" || typeof p.end === "number") {
          hasPhaseBounds = true;
          if (!Number.isInteger(p.start) || !Number.isInteger(p.end) || p.start !== prevEnd + 1 || p.end < p.start) {
            errors.push(tr.id + " phase " + (pi + 1) + " range");
          }
          prevEnd = Number.isInteger(p.end) ? p.end : prevEnd;
        }
      });
      if (hasPhaseBounds && tr.weeks && prevEnd !== tr.weeks.length) {
        errors.push(tr.id + " phases end " + prevEnd + "!=" + tr.weeks.length);
      }
      if (Array.isArray(tr.units)) {
        if (!tr.units.length) {
          errors.push(tr.id + " units");
        } else {
          let unitPhaseCursor = 0;
          let unitPrevEnd = 0;
          const unitIds = new Set();
          const phaseCount = (tr.phases || []).length;
          tr.units.forEach((u, ui) => {
            if (!u || !u.id || !u.title) {
              errors.push(tr.id + " unit " + (ui + 1) + " meta");
              return;
            }
            if (unitIds.has(u.id)) {
              errors.push(tr.id + " unit " + u.id + " dup");
            }
            unitIds.add(u.id);
            if (!Array.isArray(u.phases) || !u.phases.length) {
              errors.push(tr.id + " unit " + (ui + 1) + " phases");
              return;
            }
            for (let k = 0; k < u.phases.length; k++) {
              if (u.phases[k] !== unitPhaseCursor + k || u.phases[k] >= phaseCount) {
                errors.push(tr.id + " unit " + (ui + 1) + " phases range");
                break;
              }
            }
            const firstP = (tr.phases || [])[u.phases[0]];
            const lastP = (tr.phases || [])[u.phases[u.phases.length - 1]];
            const badRange =
              !Number.isInteger(u.start) ||
              !Number.isInteger(u.end) ||
              u.start !== unitPrevEnd + 1 ||
              u.end < u.start ||
              (firstP && typeof firstP.start === "number" && u.start !== firstP.start) ||
              (lastP && typeof lastP.end === "number" && u.end !== lastP.end);
            if (badRange) {
              errors.push(tr.id + " unit " + (ui + 1) + " range");
            }
            unitPhaseCursor += u.phases.length;
            unitPrevEnd = Number.isInteger(u.end) ? u.end : unitPrevEnd;
          });
          if (unitPhaseCursor !== phaseCount) {
            errors.push(tr.id + " units coverage " + unitPhaseCursor + "!=" + phaseCount);
          }
            if (hasPhaseBounds && tr.weeks && unitPrevEnd !== tr.weeks.length) {
            errors.push(tr.id + " units end " + unitPrevEnd + "!=" + tr.weeks.length);
          }
        }
      }
      if (Array.isArray(tr.prerequisites)) {
        tr.prerequisites.forEach((pr, pri) => {
          if (!pr || !Number.isInteger(pr.week) || pr.week < 1 || (tr.weeks && pr.week > tr.weeks.length)) {
            errors.push(tr.id + " prereq " + (pri + 1) + " week");
          }
          const reqTr = pr && data.tracks.find((x) => x.id === pr.reqTrack);
          if (!reqTr || !Number.isInteger(pr.reqWeek) || pr.reqWeek < 1 || (reqTr.weeks && pr.reqWeek > reqTr.weeks.length)) {
            errors.push(tr.id + " prereq " + (pri + 1) + " target");
          }
          if (!pr || !String(pr.topic || "").trim()) {
            errors.push(tr.id + " prereq " + (pri + 1) + " topic");
          }
        });
      }
      (tr.weeks || []).forEach((w, i) => {
        if (!w.days || !w.days.length) errors.push(tr.id + " w" + (i + 1) + " days");
        if (!w.check) errors.push(tr.id + " w" + (i + 1) + " check");
        (w.days || []).forEach((d) => {
          const blocks = d.blocks || [];
          blocks.forEach((b, bi) => {
            const bm = Number(b && b.m);
            if (!Number.isFinite(bm) || bm <= 0) {
              errors.push(tr.id + " w" + (i + 1) + " " + (d.title || "") + " b" + (bi + 1) + " min");
            }
            if (!b || !String(b.t || "").trim()) {
              errors.push(tr.id + " w" + (i + 1) + " " + (d.title || "") + " b" + (bi + 1) + " text");
            }
          });
          const sum = blocks.reduce((a, b) => a + Number(b.m), 0);
          if (sum !== 60) errors.push(tr.id + " w" + (i + 1) + " " + (d.title || "") + " " + sum);
          if (blocks.length > 1 && Number(blocks[0].m) !== 10) {
            errors.push(tr.id + " w" + (i + 1) + " " + (d.title || "") + " first " + blocks[0].m);
          }
        });
      });
    });
    return errors;
  }

  root.RoadmapEngine = {
    INTERVALS: INTERVALS,
    isValidISO: isValidISO,
    parseISO: parseISO,
    fmt: fmt,
    addDaysISO: addDaysISO,
    trackDayCount: trackDayCount,
    posFromOffset: posFromOffset,
    dateOf: dateOf,
    offsetOf: offsetOf,
    blankState: blankState,
    trackStart: trackStart,
    weekCardId: weekCardId,
    dayCardId: dayCardId,
    sessionId: sessionId,
    migrateV1: migrateV1,
    studyPos: studyPos,
    dueCards: dueCards,
    takeQueue: takeQueue,
    deferCards: deferCards,
    commitAnswer: commitAnswer,
    grade: grade,
    scheduleWeek: scheduleWeek,
    scheduleStuck: scheduleStuck,
    weeklyConsistency: weeklyConsistency,
    applyDiagnosticPlacement: applyDiagnosticPlacement,
    isActive: isActive,
    streak: streak,
    validate: validate
  };
})(typeof globalThis !== "undefined" ? globalThis : this);
