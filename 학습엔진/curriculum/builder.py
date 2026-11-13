# -*- coding: utf-8 -*-
"""Modular roadmap compiler and global cross-domain ordering validator."""
import importlib
import json
import re
from pathlib import Path

from curriculum.common import BANNED_LABELS, focus_line
from curriculum.days import (
    algo_days,
    english_days,
    english_expand_minutes,
    math_days,
    sw_days,
    thicken_english_check,
    thicken_english_week,
    thicken_math_check,
)
from curriculum.en.templates import SPEAK as EN_SPEAK, WRITE as EN_WRITE
from curriculum.meta import HOUR, TRACK_BASE

ROOT = Path(__file__).resolve().parent.parent
ROADMAP_DIR = ROOT / "roadmap"
TRACK_IDS = ("en", "al", "ma", "sw")


def load_domain(track_id):
    """Load `(units, phases)` metadata from `curriculum.<track_id>`."""
    if track_id not in TRACK_IDS:
        raise SystemExit(f"unknown track: {track_id}")
    pkg = importlib.import_module(f"curriculum.{track_id}")
    return json.loads(json.dumps(pkg.UNITS, ensure_ascii=False)), pkg.PHASES


def parse_week(line, resource, kind, prev, week_no=0, practice="code", prev_line="", mode=None, prev_mode=None):
    """Expand one `§`-delimited curriculum specification tuple into a 7-day week object."""
    parts = [p.strip() for p in line.split("§")]
    if len(parts) == 10:
        *fields, mode = parts
        parts = fields
    if len(parts) != 9:
        raise SystemExit(f"{kind} week needs 9 fields, got {len(parts)}: {line[:80]}")
    title, lab2, lab3, definition, example, trap, drill, why, check = parts
    for label in (title, lab2, lab3):
        if label in BANNED_LABELS:
            raise SystemExit(f"banned label {label} in {title}")
    if len(check) < 12 or len(example) < 12:
        raise SystemExit(f"thin week: {title}")
    goal = definition
    ideas = [[title, definition], [lab2, example], [lab3, trap]]
    if kind == "ma":
        math_mode = mode or ("calc" if week_no <= 104 else "proof")
        days = math_days(
            prev, title, definition, example, trap, drill, why,
            thicken_math_check(week_no, check, math_mode), week_no, prev_line, math_mode, prev_mode,
        )
        if math_mode == "calc" or week_no <= 26:
            outcome = f"{title}의 뜻·계산 절차와 검산·주의할 실수를 백지에 정리한 한 장."
        elif math_mode == "sketch":
            outcome = f"{title}의 진술·가정·스케치와 적용 한계를 백지에 정리한 한 장."
        else:
            outcome = f"{title}의 정의·증명과 반례를 백지에 정리한 한 장."
    elif kind == "en":
        en_mode = mode or "core"
        check = thicken_english_check(week_no, check, english_expand_minutes(week_no), drill)
        goal = f"{example} (기준 문장: {definition})"
        days = english_days(prev, title, definition, example, trap, drill, why, check, prev_line, en_mode, week_no)
        outcome = f"{title} 파일 하나와 퇴고한 문장." if title.endswith("녹음") else f"{title} 녹음 하나와 퇴고한 문장."
    elif kind == "al":
        al_mode = mode or practice
        days = algo_days(prev, title, definition, example, drill, trap, why, check, al_mode, prev_line, prev_mode)
        if al_mode == "proof":
            outcome = f"{title} 증명과 반례 노트 한 장."
        elif al_mode == "sketch":
            outcome = f"{title} 진술·가정·스케치와 한계 노트 한 장."
        elif al_mode == "write":
            outcome = f"{title} 기술 노트 초고 또는 퇴고본 한 편."
        elif al_mode == "analysis":
            outcome = f"{title} 점화·복잡도 판정 노트 한 장."
        else:
            outcome = f"{title} 손 추적 표 한 장과 구현 코드."
    elif kind == "sw":
        days = sw_days(prev, title, definition, example, trap, drill, why, check, prev_line)
        contrast = lab2.replace("대비: ", "", 1)
        if week_no <= 104:
            outcome = f"{title}({contrast}) 비교 설계 노트 또는 커밋."
        else:
            outcome = f"{title}({contrast}) 비교 ADR 또는 리팩터링 커밋."
    else:
        raise SystemExit(kind)
    return {
        "title": title,
        "goal": goal,
        "outcome": outcome,
        "resource": resource,
        "check": check,
        "ideas": ideas,
        "days": days,
    }


def load_syllabus(phase_rows, kind, old_weeks=None):
    """Compile phase definitions into validated `(phases, weeks)` lists."""
    phases = []
    weeks = []
    prev = "시작"
    prev_line = ""
    prev_mode = None
    for row in phase_rows:
        phase = {
            "name": row["name"],
            "start": row["start"],
            "end": row["end"],
            "from": row["from"],
            "to": row["to"],
            "result": row["result"],
        }
        items = row["weeks"]
        expected = phase["end"] - phase["start"] + 1
        if len(items) != expected:
            raise SystemExit(f"{kind} {phase['name']} has {len(items)} weeks, expected {expected}")
        phases.append(phase)
        practice = "code"
        if kind == "al":
            start = phase["start"]
            if start >= 326:
                practice = "write"
            elif start == 118:
                practice = "analysis"
            elif start >= 157 and start != 183:
                practice = "proof"
        phase_mode = row.get("mode")
        if kind == "en" and not phase_mode:
            start = phase["start"]
            if 118 <= start <= 195:
                phase_mode = "contract"
            elif start == 92 or start >= 196:
                phase_mode = "prose"
        for item in items:
            if isinstance(item, dict):
                copied = thicken_english_week(item)
                weeks.append(copied)
                prev = copied["title"]
                prev_line = focus_line(copied.get("goal") or copied.get("check") or "")
                prev_mode = "kept"
            elif isinstance(item, int):
                if old_weeks is None:
                    raise SystemExit(f"copy in {kind}")
                copied = old_weeks[item - 1]
                weeks.append(copied)
                prev = copied["title"]
                prev_line = focus_line(copied.get("goal") or copied.get("check") or "")
                prev_mode = "kept"
            else:
                week_mode = None
                fields = list(item)
                if len(fields) >= 10 and fields[-1] in (
                    "calc", "proof", "sketch", "core", "listen", "pron", "read",
                    "contract", "prose", "code", "analysis", "write",
                ):
                    week_mode = fields[-1]
                mode = week_mode or phase_mode
                line = "§".join(fields)
                week_no = len(weeks) + 1
                weeks.append(parse_week(
                    line, row["resource"], kind, prev, week_no, practice, prev_line, mode, prev_mode,
                ))
                prev = weeks[-1]["title"]
                if kind in ("sw", "en"):
                    prev_line = focus_line(weeks[-1]["ideas"][0][1])
                else:
                    prev_line = focus_line(weeks[-1]["ideas"][1][1])
                if kind == "ma":
                    prev_mode = mode or ("calc" if week_no <= 104 else "proof")
                elif kind == "al":
                    prev_mode = mode or practice
                elif kind == "en":
                    prev_mode = mode or "core"
                else:
                    prev_mode = mode
    if phases[0]["start"] != 1:
        raise SystemExit(f"{kind} does not start at 1")
    for a, b in zip(phases, phases[1:]):
        if a["end"] + 1 != b["start"]:
            raise SystemExit(f"gap {a['name']} -> {b['name']}")
    if len(weeks) != phases[-1]["end"]:
        raise SystemExit(f"{kind} weeks {len(weeks)} != {phases[-1]['end']}")
    titles = [w["title"] for w in weeks]
    if len(titles) != len(set(titles)):
        dup = sorted({t for t in titles if titles.count(t) > 1})
        raise SystemExit(f"duplicate titles in {kind}: {dup}")
    return phases, weeks


def build_track(track_id):
    """Build one complete track JSON payload (including hierarchical `units`)."""
    units, phase_rows = load_domain(track_id)
    phases, weeks = load_syllabus(phase_rows, track_id)
    data = dict(TRACK_BASE[track_id])
    data["units"] = units
    data["phases"] = phases
    data["weeks"] = weeks
    return data


def build_all():
    """Build all tracks (`en`, `al`, `ma`, `sw`) as full JSON track payloads."""
    tracks = {tid: build_track(tid) for tid in TRACK_IDS}
    check_order({tid: (t["phases"], t["weeks"]) for tid, t in tracks.items()})
    return tracks


def write_roadmap(out_dir=None, tracks=None):
    """Write built track JSON files to `roadmap/` (default) and log summary counts."""
    target_dir = Path(out_dir) if out_dir else ROADMAP_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    if tracks is None:
        tracks = build_all()
    for tid, data in tracks.items():
        path = target_dir / f"{tid}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(tid, len(data["weeks"]), "weeks", len(data["phases"]), "phases", len(data["units"]), "units")
    return tracks


def find(weeks, needle):
    """Return the 1-based week number matching `needle` anywhere in JSON."""
    hits = [i + 1 for i, w in enumerate(weeks) if needle in json.dumps(w, ensure_ascii=False)]
    if not hits:
        raise SystemExit(f"missing {needle}")
    return hits[0]


def find_title(weeks, needle):
    """Return the 1-based week number matching `needle` in `week["title"]`."""
    hits = [i + 1 for i, w in enumerate(weeks) if needle in w["title"]]
    if not hits:
        raise SystemExit(f"missing title {needle}")
    return hits[0]


def _unwrap(entry):
    if isinstance(entry, tuple) and len(entry) == 2:
        return entry
    return entry["phases"], entry["weeks"]


def check_order(built):
    """Run global ordering, cross-domain prerequisite, and formatting invariants."""
    ma_phases, ma = _unwrap(built["ma"])
    al_phases, al = _unwrap(built["al"])
    en_phases, en = _unwrap(built["en"])
    sw_phases, sw = _unwrap(built["sw"])
    unwrapped = {"ma": (ma_phases, ma), "al": (al_phases, al), "en": (en_phases, en), "sw": (sw_phases, sw)}

    ma_master = find(ma, "마스터 정리")
    al_master = find(al, "마스터 정리")
    if not (ma_master < al_master):
        raise SystemExit(f"master {ma_master} vs {al_master}")
    if find(ma, "고유값") < 140:
        raise SystemExit("eigen early")
    if find(ma, "체비쇼프") > find(al, "체르노프"):
        raise SystemExit("chebyshev after chernoff")
    if find(ma, "다항식의 나눗셈") > find(al, "다항식 일치"):
        raise SystemExit("rings after PIT")
    if find(ma, "군의 공리") < find(ma, "유계 작용소"):
        raise SystemExit("groups before operators")
    if find(al, "마스터 정리") < 118:
        raise SystemExit("algo master in year 1-2")
    if find(en, "shall") < 53:
        raise SystemExit("shall in year 1")
    if find(en, "NDA") < 105:
        raise SystemExit("NDA before the contract block")
    if find(en, "레드라인") < 105:
        raise SystemExit("redline before the contract block")
    scene = find_title(en, "장면")
    bridge = find_title(en, "설명문")
    if scene < bridge:
        raise SystemExit(f"scene title {scene} before prose bridge {bridge}")
    blob_y1 = json.dumps(en[:52], ensure_ascii=False)
    for bad in ("shall", "NDA", "레드라인", "현재완료"):
        if bad in blob_y1:
            raise SystemExit(f"year-1 english has {bad}")
    y1_titles = [w["title"] for w in al[:52]]
    for bad in ("동적 계획", "세그먼트", "포드", "마스터"):
        if any(bad in t for t in y1_titles):
            raise SystemExit(f"algo year 1 has {bad}")
    cloned = "기준 문장을 넣어 60초 이상 말한다"
    if cloned in json.dumps(en, ensure_ascii=False):
        raise SystemExit("english speak task is still cloned")
    for i, week in enumerate(en, 1):
        if not (131 <= i <= 208):
            continue
        blob = json.dumps(week, ensure_ascii=False)
        for leaked in ("March Review", "500 dollars", "31 March", "Ana Kim"):
            if leaked in blob:
                raise SystemExit(f"week {i} still uses the report draft: {leaked}")
    if sw[259]["title"] != "설계 점검":
        raise SystemExit(f"sw week 260 is {sw[259]['title']}")
    if sw[363]["title"] != "기록 점검":
        raise SystemExit(f"sw week 364 is {sw[363]['title']}")
    if sw[0]["days"][2]["blocks"][1]["m"] != 40:
        raise SystemExit("sw apply block is not 40")
    titles = "\n".join(w["title"] for w in sw)
    for bad in ("첫 프로그램", "파이썬 입문", "변수 선언"):
        if bad in titles:
            raise SystemExit(f"sw title teaches {bad}")
    if "첫 프로그램" in sw[0]["days"][2]["blocks"][1]["t"]:
        raise SystemExit("sw week 1 teaches a first program")
    impl = al[0]["days"][2]["blocks"][1]["t"]
    if "코드로 작성" not in impl:
        raise SystemExit("algo implement day does not ask for code")
    if al[0]["title"] != "종이 위 이분 탐색":
        raise SystemExit(f"algo week 1 is {al[0]['title']}")
    if al[51]["title"] != "트리 점검":
        raise SystemExit(f"algo week 52 is {al[51]['title']}")
    if any("첫 프로그램" in w["title"] for w in al[:52]):
        raise SystemExit("algo year 1 still teaches a first program")
    proof = al[165]["days"][2]["blocks"][1]["t"]
    if al[165]["title"] != "증명 쓰기" or "코드로 작성해 실행" in proof or "증명으로 적는다" not in proof:
        raise SystemExit("algo proof week 166 was not switched to a proof")
    note = al[363]["days"][2]["blocks"][1]["t"]
    if "코드로 작성해 실행" in note:
        raise SystemExit("algo note week 364 still executes the sentence")
    if "초고를 쓴다" not in note and "증명으로 적는다" not in note:
        raise SystemExit("algo note week 364 lost its writing/proof hour")
    master_day = al[118]["days"][2]["blocks"][1]["t"]
    if al[118]["title"] != "마스터 정리" or "코드로 작성해 실행" in master_day or "판정 노트를 쓴다" not in master_day:
        raise SystemExit("algo master week was not switched to analysis")
    sw_case = sw[0]["days"][1]["blocks"][1]["t"]
    if "작게 나누어 흐름을 드러내는 관점" in sw_case or "사례:" not in sw_case:
        raise SystemExit("sw week 1 still uses generic lens boilerplate")
    flow = al[182]["days"][2]["blocks"][1]["t"]
    if al[182]["title"] != "용량과 유량" or "코드로 작성" not in flow:
        raise SystemExit("flow implementation lost its code hour")
    math_check = ma[3]["days"][6]["blocks"][1]["t"]
    if "여덟 문제" not in math_check:
        raise SystemExit("math week 4 check was not thickened")
    if "여덟 문제" in ma[104]["days"][6]["blocks"][1]["t"]:
        raise SystemExit("math analysis check was thickened")
    blank = ma[1]["days"][5]["blocks"][1]["t"]
    if "48×21" not in blank or "여덟 문제" not in blank:
        raise SystemExit("math week 2 blank day was not thickened")
    if "여덟 문제" in ma[104]["days"][5]["blocks"][1]["t"]:
        raise SystemExit("math analysis blank was thickened")
    kept_blob = json.dumps(en[0], ensure_ascii=False)
    if "60초" not in kept_blob or "분을 채운다" not in kept_blob:
        raise SystemExit("kept english hour was not filled")
    speak = en[13]["days"][3]["blocks"][1]["t"]
    if "세 번" not in speak:
        raise SystemExit("english speak hour was not expanded")
    short = [
        b["t"]
        for d in en[1]["days"]
        for b in d["blocks"]
        if 15 <= b["m"] < 25 and "60초" in b["t"]
    ]
    if not short or any("분을 채운다" not in t for t in short):
        raise SystemExit("kept english 15-20 minute take was not filled")
    openings = {
        "ma": ma[0]["days"][0]["blocks"][0]["t"],
        "al": al[0]["days"][0]["blocks"][0]["t"],
        "sw": sw[0]["days"][0]["blocks"][0]["t"],
    }
    expected = {"ma": "3+4×2", "al": "[1, 3, 5, 7, 9]", "sw": "한 커밋에는 한 이유"}
    for kind, text in openings.items():
        if "어제 시작" in text or expected[kind] not in text:
            raise SystemExit(f"{kind} week 1 opener is still vague")
    first_sw_days = sw[0]["days"]
    if "한 커밋에는 한 이유" not in first_sw_days[1]["blocks"][0]["t"]:
        raise SystemExit("sw day 2 opener does not name the rule")
    if "파일 이름" not in first_sw_days[2]["blocks"][0]["t"]:
        raise SystemExit("sw day 3 opener does not name the line")
    second = ma[1]["days"][0]["blocks"][0]["t"]
    if "계산 순서" not in second or "3+4×2" not in second:
        raise SystemExit("math week 2 opener does not name last week's example")
    vague = ("어제 한 문장을 말한다.", "어제 표시한 줄을 말한다.", "어제 시작에서")
    for kind in ("ma", "al", "en", "sw"):
        phases, track_weeks = unwrapped[kind]
        for wi, w in enumerate(track_weeks, 1):
            dtitles = [d["title"] for d in w["days"]]
            if len(dtitles) != len(set(dtitles)):
                raise SystemExit(f"{kind} week {wi} has duplicate day titles: {dtitles}")
            for d in w["days"]:
                for b in d["blocks"]:
                    bt = b["t"]
                    if "通し" in bt or "  " in bt or "…" in bt:
                        raise SystemExit(f"{kind} week {wi} artifact text issue: {bt[:80]}")
        blob = json.dumps(track_weeks, ensure_ascii=False)
        for phrase in vague:
            if phrase in blob:
                raise SystemExit(f"{kind} still has vague cue: {phrase}")
    if "다음 계산을" in ma[39]["days"][0]["blocks"][0]["t"]:
        raise SystemExit("ma week 40 opener still asks for calc review after proof week 39")
    if "의무 주체" not in en[117]["days"][0]["blocks"][2]["t"]:
        raise SystemExit("en week 118 did not switch to contract mode")
    if "3분 이상" not in en[117]["days"][6]["blocks"][1]["t"] or "3분 이상" not in en[117]["check"]:
        raise SystemExit("en week 118 check did not scale duration")
    if any(not it[1].endswith((".", "!", "?")) for w in sw for it in w["ideas"]):
        raise SystemExit("sw ideas has unterminated sentence")
    if "정밀 동사" not in en[208]["days"][0]["blocks"][3]["t"]:
        raise SystemExit("en week 209 did not switch to prose mode")
    if sw[0]["ideas"][1][0] == "대비 관점":
        raise SystemExit("sw week 1 still uses generic '대비 관점' label")
    for kind in ("ma", "al", "en", "sw"):
        phases, track_weeks = unwrapped[kind]
        pnames = [p["name"] for p in phases]
        if len(pnames) != len(set(pnames)):
            raise SystemExit(f"{kind} has duplicate phase names: {pnames}")
        for a, b in zip(phases, phases[1:]):
            if a["to"] != b["from"]:
                raise SystemExit(f"{kind} phase bridge mismatch: {a['name']}({a['to']}) -> {b['name']}({b['from']})")
        hour_mins = [int(h[0].rstrip("분")) for h in HOUR[kind]]
        if sum(hour_mins) != 60:
            raise SystemExit(f"{kind} HOUR sum {sum(hour_mins)} != 60")
        blob = json.dumps({"phases": phases, "weeks": track_weeks}, ensure_ascii=False)
        if re.search(r"지\s*않지\s*않", blob):
            raise SystemExit(f"{kind} has double negative")
        if "\\(" in blob or "\\)" in blob or "$$" in blob:
            raise SystemExit(f"{kind} has raw LaTeX delimiters")
        for wi, w in enumerate(track_weeks, 1):
            for di, d in enumerate(w["days"], 1):
                total = sum(b["m"] for b in d["blocks"])
                if total != 60:
                    raise SystemExit(f"{kind} w{wi} d{di} total {total} != 60")
                if len(d["blocks"]) > 1 and d["blocks"][0]["m"] != 10:
                    raise SystemExit(f"{kind} w{wi} d{di} block[0] is {d['blocks'][0]['m']} != 10")
    for wi in (175, 177, 181, 204, 218):
        day3 = al[wi - 1]["days"][2]["blocks"][1]["t"]
        if "코드로 작성해 실행" not in day3 or "실행하지 않는다" in day3:
            raise SystemExit(f"al w{wi} coding week is not in code mode")
    if "접미사 배열" in json.dumps(al[217], ensure_ascii=False) or "실패 함수 배열" not in json.dumps(al[217], ensure_ascii=False):
        raise SystemExit("al w218 KMP failure array terminology regression")
    for ma_wi in (112, 165, 166, 186, 201, 203, 214, 219, 230, 233, 240, 242, 243, 244, 247, 258, 259, 260):
        ma_d3 = ma[ma_wi - 1]["days"][2]["blocks"][2]["t"]
        if "스케치" not in ma_d3:
            raise SystemExit(f"ma w{ma_wi} expected sketch mode on Day 3")
    for wi in (214, 215, 228, 239, 240, 245, 251, 252, 256, 257, 263, 264, 266, 269, 273, 280, 281, 322):
        al_d3 = al[wi - 1]["days"][2]["blocks"][1]["t"]
        if "진술·가정·스케치 노트를 쓴다" not in al_d3 or "증명으로 적는다" in al_d3:
            raise SystemExit(f"al w{wi} expected sketch mode on Day 3")
    y1_ma = json.dumps(ma[:52], ensure_ascii=False)
    for req in ("완전제곱", "판별식", "귀류법", "자연로그"):
        if req not in y1_ma:
            raise SystemExit(f"ma year 1 missing {req}")
    for k, v in EN_WRITE.items():
        if re.search(r"\d+단어", v):
            raise SystemExit(f"en WRITE[{k}] hardcodes word count: {v}")
    for k, v in EN_SPEAK.items():
        if re.search(r"\d+(?:초|분)", v):
            raise SystemExit(f"en SPEAK[{k}] hardcodes duration: {v}")
    for wi, w in enumerate(en, 1):
        for target_str in (w["check"], *(b["t"] for d in w["days"] for b in d["blocks"])):
            mins = set(re.findall(r"(?:2~3분|[1-6]분|90초)\s*이상", target_str))
            if len(mins) > 1:
                raise SystemExit(f"en w{wi} conflicting speak mins in same unit: {mins}")
            cleaned = re.sub(r"\d[\d,]*단어[^.?!]*(?:→|에서)[^.?!]*?\d+단어", "", target_str)
            words = set(re.findall(r"(?<![\d,])(?:100|150|200|250|300|350|400|500)단어", cleaned))
            if len(words) > 1:
                raise SystemExit(f"en w{wi} conflicting word counts in same unit: {words}")
        chk_mins = set(re.findall(r"(?:2~3분|[1-6]분|90초)\s*이상", w["check"]))
        if chk_mins and wi >= 53:
            d4_mins = set(re.findall(r"(?:2~3분|[1-6]분|90초)\s*이상", w["days"][3]["blocks"][1]["t"]))
            if d4_mins and d4_mins != chk_mins:
                raise SystemExit(f"en w{wi} Day 4 vs check speak mins mismatch: {d4_mins} vs {chk_mins}")
        if re.search(r"(?:^|\s)(\S+)\s+\1(?=\s|$|[.,!?])", w["outcome"]):
            raise SystemExit(f"en w{wi} duplicate word in outcome: {w['outcome']}")
        if wi in (194, 362, 364) and "10분 이상" not in w["check"]:
            raise SystemExit(f"en w{wi} expected 10분 이상 in check: {w['check']}")
    for kind in ("ma", "al", "en", "sw"):
        _, track_weeks = unwrapped[kind]
        for wi, w in enumerate(track_weeks, 1):
            if re.search(r"[.!?]\s+외의", json.dumps(w, ensure_ascii=False)):
                raise SystemExit(f"{kind} w{wi} stray punctuation before 외의")
    for wi, w in enumerate(sw, 1):
        for s in (w["title"], w["goal"], w["outcome"], *(it[0] for it in w["ideas"])):
            if s.count("(") != s.count(")"):
                raise SystemExit(f"sw w{wi} unbalanced parens: {s}")

