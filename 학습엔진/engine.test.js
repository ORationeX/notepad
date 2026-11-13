const assert = require("assert");
require("./engine.js");
const E = globalThis.RoadmapEngine;

function track(weeks) {
  return {
    id: "ma",
    color: "#234",
    phases: [{ name: "a", start: 1, end: weeks.length }],
    weeks: weeks.map((days, i) => ({
      title: "주" + (i + 1),
      check: "기준 " + (i + 1),
      outcome: "산출 " + (i + 1),
      days: Array.from({ length: days }, (_, d) => ({
        title: "날" + d,
        blocks: [{ m: 60, t: "한 블록" }]
      }))
    }))
  };
}

const today = "2026-10-13";
const state = E.blankState("2026-10-12");

// Stuck day card: retry does not graduate or jump past step 1
const stuck = E.scheduleStuck(state, "ma", 1, 0, "첫 연산", today, today);
assert.strictEqual(stuck.due, "2026-10-14");
assert.strictEqual(stuck.step, 0);
assert.strictEqual(E.grade(stuck, true, today).ok, false);
assert.strictEqual(E.commitAnswer(stuck), true);
assert.strictEqual(E.grade(stuck, false, today).result, "retry");
assert.strictEqual(stuck.phase, "retry");
assert.strictEqual(E.commitAnswer(stuck), true);
const retryPass = E.grade(stuck, true, today);
assert.strictEqual(retryPass.result, "success");
assert.strictEqual(retryPass.graduated, false);
assert.strictEqual(stuck.step, 1);
assert.strictEqual(stuck.due, "2026-10-16");

// Retry-pass at higher step holds step without advancing
const highCard = { kind: "week", step: 3, phase: "prompt", due: today };
E.commitAnswer(highCard);
E.grade(highCard, false, today);
E.commitAnswer(highCard);
const highRetryPass = E.grade(highCard, true, today);
assert.strictEqual(highRetryPass.graduated, false);
assert.strictEqual(highCard.step, 3);
assert.strictEqual(highCard.due, E.addDaysISO(today, E.INTERVALS[3]));

// Fail resets to step 0 (day) or step 1 (week)
const again = E.scheduleStuck(state, "ma", 1, 2, "막힘", "2026-10-01", today);
assert.strictEqual(again.due, today);
assert.strictEqual(E.commitAnswer(again), true);
assert.strictEqual(E.grade(again, false, today).result, "retry");
assert.strictEqual(E.commitAnswer(again), true);
assert.strictEqual(E.grade(again, false, today).result, "fail");
assert.strictEqual(again.step, 0);
assert.strictEqual(again.due, "2026-10-14");

// Week card scheduling & reset
const week = E.scheduleWeek(state, "ma", 3, today, false);
assert.strictEqual(week.due, "2026-10-16");
assert.strictEqual(week.step, 1);
E.scheduleWeek(state, "ma", 3, today, false);
assert.strictEqual(state.cards[week.id].due, "2026-10-16");
const reset = E.scheduleWeek(state, "ma", 3, today, true);
assert.strictEqual(reset.due, "2026-10-16");
assert.strictEqual(E.commitAnswer(reset), true);
assert.strictEqual(E.grade(reset, true, today).result, "success");
assert.strictEqual(reset.step, 2);
assert.strictEqual(reset.due, "2026-10-20");

// Spaced repetition intervals + graduation at final step
let cursor = today;
let card = { id: "grad", track: "ma", kind: "day", step: 0, phase: "prompt", due: today };
const gaps = [];
for (let i = 0; i < 6; i++) {
  assert.strictEqual(E.commitAnswer(card), true);
  const res = E.grade(card, true, cursor);
  assert.strictEqual(res.graduated, false);
  gaps.push(E.offsetOf(cursor, card.due));
  cursor = card.due;
}
assert.deepStrictEqual(gaps, [3, 7, 16, 35, 70, 180]);
assert.strictEqual(E.commitAnswer(card), true);
const finalRes = E.grade(card, true, cursor);
assert.strictEqual(finalRes.result, "success");
assert.strictEqual(finalRes.graduated, true);
assert.strictEqual(card.retired, true);
assert.strictEqual(card.due, null);

// Retired cards do not appear in dueCards
const stDue = E.blankState(today);
stDue.cards["grad"] = card;
assert.strictEqual(E.dueCards(stDue, "ma", cursor).length, 0);

// Queue cap & stagger deferral
const cards = [
  { id: "a", track: "ma", week: 1, kind: "week", due: "2026-10-10" },
  { id: "b", track: "ma", week: 1, kind: "day", due: "2026-10-10" },
  { id: "c", track: "ma", week: 2, kind: "week", due: "2026-10-12" },
  { id: "d", track: "ma", week: 4, kind: "week", due: "2026-10-11" },
  { id: "e", track: "ma", week: 5, kind: "week", due: "2026-10-12" }
];
const queue = E.takeQueue(cards);
assert.deepStrictEqual(queue.shown.map((c) => c.id), ["b", "d"]);
assert.deepStrictEqual(queue.defer.map((c) => c.id), ["a", "c", "e"]);
E.deferCards(queue.defer, today);
assert.strictEqual(queue.defer[0].due, "2026-10-14");
assert.strictEqual(queue.defer[1].due, "2026-10-14");
assert.strictEqual(queue.defer[2].due, "2026-10-15");

// studyPos: multi-week catch-up and skip-ahead
const tr = track([7, 7, 7, 7]);
const st = E.blankState("2026-10-12");
assert.deepStrictEqual(E.studyPos(tr, 0, st), { week: 1, day: 0, repair: false, calendar: { week: 1, day: 0 } });
// Missed 3 weeks -> repair starts at earliest unpassed week (1), not week 3!
assert.strictEqual(E.studyPos(tr, 21, st).repair, true);
assert.strictEqual(E.studyPos(tr, 21, st).week, 1);
assert.strictEqual(E.studyPos(tr, 7, st).repair, true);
assert.strictEqual(E.studyPos(tr, 7, st).week, 1);
assert.strictEqual(E.studyPos(tr, 7, st).day, 0);
st.done["ma:1:0"] = "2026-10-12";
st.done["ma:1:1"] = "2026-10-13";
assert.strictEqual(E.studyPos(tr, 7, st).day, 2);
for (let d = 0; d < 7; d++) st.done["ma:1:" + d] = "2026-10-12";
assert.strictEqual(E.studyPos(tr, 7, st).day, 6);
st.pass["ma:1"] = "2026-10-18";
assert.strictEqual(E.studyPos(tr, 7, st).repair, false);
assert.strictEqual(E.studyPos(tr, 7, st).week, 2);

// Skip-ahead: if user skipped weeks 1 & 2 on day 0 (offset 0), studyPos jumps to week 3!
st.pass["ma:2"] = "2026-10-12";
const skippedPos = E.studyPos(tr, 0, st);
assert.strictEqual(skippedPos.week, 3);
assert.strictEqual(skippedPos.day, 0);
assert.strictEqual(skippedPos.repair, false);
assert.strictEqual(skippedPos.skippedAhead, true);

// All weeks passed -> completed
st.pass["ma:3"] = "2026-10-12";
st.pass["ma:4"] = "2026-10-12";
assert.strictEqual(E.studyPos(tr, 0, st).completed, true);

// Migration & streak & validation
const migrated = E.migrateV1({ start: "2026-10-01", done: { "en:1:0": "2026-10-01" }, pass: { "en:1": "2026-10-01" }, track: "en", week: 2, view: "track" }, today);
assert.strictEqual(migrated.done["en:1:0"], "2026-10-01");
assert.strictEqual(migrated.cards["en:w:1"].due, today);
assert.strictEqual(migrated.cards["en:w:1"].step, 1);

const future = E.migrateV1({ start: today, pass: { "al:2": "2026-10-20" } }, today);
assert.strictEqual(future.cards["al:w:2"].due, "2026-10-23");

st.activity = {};
st.done = { "ma:1:0": "2026-10-12" };
assert.strictEqual(E.streak(st, "2026-10-13"), 1);
st.activity["2026-10-13"] = true;
assert.strictEqual(E.streak(st, "2026-10-13"), 2);

const errors = E.validate({ tracks: [tr] });
assert.deepStrictEqual(errors, []);
const bad = E.validate({ tracks: [{ id: "x", color: "#111", phases: [{}], weeks: [{ check: "c", days: [{ title: "t", blocks: [{ m: 10, t: "a" }] }] }] }] });
assert.ok(bad.some((e) => e.indexOf("10") !== -1));

// Date validation guards
assert.strictEqual(E.isValidISO("2026-10-12"), true);
assert.strictEqual(E.isValidISO("2026-02-30"), false);
assert.strictEqual(E.isValidISO("not-a-date"), false);
assert.strictEqual(E.addDaysISO("invalid", 3), "");
{
  const s = E.blankState("2026-10-01");
  s.starts = { en: "2026-02-31", al: "2026-09-01" };
  assert.strictEqual(E.trackStart(s, "en"), "2026-10-01");
  assert.strictEqual(E.trackStart(s, "al"), "2026-09-01");
}

// Overtime studyPos (offset >= total days with unpassed weeks vs all passed)
{
  const ovState = E.blankState(today);
  ovState.pass["ma:1"] = today;
  ovState.done["ma:2:0"] = today;
  const ov = E.studyPos(tr, E.trackDayCount(tr) + 5, ovState);
  assert.strictEqual(ov.overtime, true);
  assert.strictEqual(ov.repair, true);
  assert.strictEqual(ov.week, 2);
  assert.strictEqual(ov.day, 1);
  assert.strictEqual(ov.calendar, null);
  ovState.pass["ma:2"] = today;
  ovState.pass["ma:3"] = today;
  ovState.pass["ma:4"] = today;
  assert.strictEqual(E.studyPos(tr, E.trackDayCount(tr) + 5, ovState).completed, true);
}

// deferCards preserves origDue ordering and retry phase
{
  const cOldRetry = { id: "ma:w:1", kind: "week", track: "ma", week: 1, step: 1, due: "2026-10-10", phase: "retryReveal" };
  const cMid = { id: "ma:w:2", kind: "week", track: "ma", week: 2, step: 1, due: "2026-10-11", phase: "prompt" };
  const cNew = { id: "ma:w:3", kind: "week", track: "ma", week: 3, step: 1, due: "2026-10-12", phase: "prompt" };
  const q1 = E.takeQueue([cNew, cMid, cOldRetry]);
  assert.strictEqual(q1.shown.length, 2);
  assert.deepStrictEqual(q1.defer.map((c) => c.id), ["ma:w:3"]);
  E.deferCards([cOldRetry], "2026-10-12");
  assert.strictEqual(cOldRetry.origDue, "2026-10-10");
  assert.strictEqual(cOldRetry.due, "2026-10-13");
  assert.strictEqual(cOldRetry.phase, "retry");
  const q2 = E.takeQueue([cMid, cOldRetry]);
  assert.strictEqual(q2.shown[0].id, "ma:w:1");
  E.commitAnswer(cOldRetry);
  assert.strictEqual(cOldRetry.phase, "retryReveal");
  E.grade(cOldRetry, true, "2026-10-13");
  assert.strictEqual(cOldRetry.origDue, undefined);
}

// scheduleStuck caps future fromISO to today + 1 and clamps past fromISO to today
{
  const s = E.blankState(today);
  const fut = E.scheduleStuck(s, "ma", 4, 0, "skipped ahead line", "2027-08-01", "2026-10-12");
  assert.strictEqual(fut.due, "2026-10-13");
  const past = E.scheduleStuck(s, "ma", 1, 0, "old stuck line", "2026-10-01", "2026-10-12");
  assert.strictEqual(past.due, "2026-10-12");
}

// streak honors track-specific starts earlier than global start
{
  const s = E.blankState("2026-10-12");
  s.starts = { al: "2026-10-10" };
  s.activity = { "2026-10-10": true, "2026-10-11": true, "2026-10-12": true };
  assert.strictEqual(E.streak(s, "2026-10-12"), 3);
}

// takeQueue keeps active revealed week card ahead of newly added same-week day prompt card
{
  const activeWeek = { id: "ma:w:4", kind: "week", track: "ma", week: 4, step: 1, due: "2026-10-14", phase: "reveal" };
  const freshDay = { id: "ma:d:4:0", kind: "day", track: "ma", week: 4, day: 0, step: 0, due: "2026-10-13", phase: "prompt" };
  const otherWeek = { id: "ma:w:2", kind: "week", track: "ma", week: 2, step: 2, due: "2026-10-12", phase: "prompt" };
  const q = E.takeQueue([freshDay, otherWeek, activeWeek]);
  assert.strictEqual(q.shown[0].id, "ma:w:4");
  assert.strictEqual(q.shown[1].id, "ma:w:2");
  assert.deepStrictEqual(q.defer.map((c) => c.id), ["ma:d:4:0"]);
  assert.strictEqual(activeWeek.phase, "reveal");
}

// validate catches phase range gaps and multi-block days not starting with 10m recall
{
  const badPhase = track([7, 7]);
  badPhase.phases = [{ name: "p1", start: 1, end: 1 }, { name: "p2", start: 3, end: 3 }];
  const phaseErrs = E.validate({ tracks: [badPhase] });
  assert.ok(phaseErrs.some((e) => e.indexOf("phase") !== -1));

  const badFirstBlock = track([7]);
  badFirstBlock.weeks[0].days[0].blocks = [{ m: 15, t: "wrong" }, { m: 45, t: "rest" }];
  const blockErrs = E.validate({ tracks: [badFirstBlock] });
  assert.ok(blockErrs.some((e) => e.indexOf("first 15") !== -1));
}

// validate verifies optional units hierarchy (valid contiguous vs missing phase / gap / mismatch)
{
  const goodUnits = track([7, 7]);
  goodUnits.phases = [
    { name: "p1", start: 1, end: 1 },
    { name: "p2", start: 2, end: 2 },
  ];
  goodUnits.units = [
    { id: "u1", title: "단원1", summary: "요약1", start: 1, end: 1, phases: [0] },
    { id: "u2", title: "단원2", summary: "요약2", start: 2, end: 2, phases: [1] },
  ];
  assert.deepStrictEqual(E.validate({ tracks: [goodUnits] }), []);

  const badUnitGap = track([7, 7]);
  badUnitGap.phases = [
    { name: "p1", start: 1, end: 1 },
    { name: "p2", start: 2, end: 2 },
  ];
  badUnitGap.units = [
    { id: "u1", title: "단원1", start: 1, end: 1, phases: [0] },
    { id: "u2", title: "단원2", start: 2, end: 2, phases: [0] },
  ];
  const gapErrs = E.validate({ tracks: [badUnitGap] });
  assert.ok(gapErrs.some((e) => e.indexOf("unit 2 phases range") !== -1));

  const badUnitRange = track([7, 7]);
  badUnitRange.phases = [
    { name: "p1", start: 1, end: 1 },
    { name: "p2", start: 2, end: 2 },
  ];
  badUnitRange.units = [
    { id: "u1", title: "단원1", start: 1, end: 2, phases: [0, 1] },
  ];
  assert.deepStrictEqual(E.validate({ tracks: [badUnitRange] }), []);

  badUnitRange.units = [
    { id: "u1", title: "단원1", start: 1, end: 2, phases: [0] },
  ];
  const rangeErrs = E.validate({ tracks: [badUnitRange] });
  assert.ok(rangeErrs.some((e) => e.indexOf("unit 1 range") !== -1));
  assert.ok(rangeErrs.some((e) => e.indexOf("units coverage 1!=2") !== -1));
}

console.log("engine ok");
