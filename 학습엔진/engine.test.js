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

const stuck = E.scheduleStuck(state, "ma", 1, 0, "첫 연산", today, today);
assert.strictEqual(stuck.due, "2026-10-14");
assert.strictEqual(stuck.step, 0);
assert.strictEqual(E.grade(stuck, true, today).ok, false);
assert.strictEqual(E.commitAnswer(stuck), true);
assert.strictEqual(E.grade(stuck, false, today).result, "retry");
assert.strictEqual(stuck.phase, "retry");
assert.strictEqual(E.commitAnswer(stuck), true);
assert.strictEqual(E.grade(stuck, true, today).result, "success");
assert.strictEqual(stuck.step, 1);
assert.strictEqual(stuck.due, "2026-10-16");

const again = E.scheduleStuck(state, "ma", 1, 2, "막힘", "2026-10-01", today);
assert.strictEqual(again.due, today);
assert.strictEqual(E.commitAnswer(again), true);
assert.strictEqual(E.grade(again, false, today).result, "retry");
assert.strictEqual(E.commitAnswer(again), true);
assert.strictEqual(E.grade(again, false, today).result, "fail");
assert.strictEqual(again.step, 0);
assert.strictEqual(again.due, "2026-10-14");

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

let cursor = today;
let card = { kind: "day", step: 0, phase: "prompt", due: today };
const gaps = [];
for (let i = 0; i < 7; i++) {
  assert.strictEqual(E.commitAnswer(card), true);
  E.grade(card, true, cursor);
  gaps.push(E.offsetOf(cursor, card.due));
  cursor = card.due;
}
assert.deepStrictEqual(gaps, [3, 7, 16, 35, 70, 70, 70]);

const cards = [
  { id: "a", track: "ma", week: 1, kind: "week", due: "2026-10-10" },
  { id: "b", track: "ma", week: 1, kind: "day", due: "2026-10-10" },
  { id: "c", track: "ma", week: 2, kind: "week", due: "2026-10-12" },
  { id: "d", track: "ma", week: 4, kind: "week", due: "2026-10-11" }
];
const queue = E.takeQueue(cards);
assert.deepStrictEqual(queue.shown.map((c) => c.id), ["b", "d"]);
assert.deepStrictEqual(queue.defer.map((c) => c.id), ["a", "c"]);

const tr = track([7, 7, 7]);
const st = E.blankState("2026-10-12");
assert.deepStrictEqual(E.studyPos(tr, 0, st), { week: 1, day: 0, repair: false, calendar: { week: 1, day: 0 } });
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

console.log("engine ok");
