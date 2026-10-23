# -*- coding: utf-8 -*-
"""Rebuild roadmap JSON from syllabus text. Source of the week sequence."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
ROADMAP = ROOT / "roadmap"
SRC = ROOT / "syllabus"

BANNED_LABELS = {"목표", "확인", "범위"}


def parse_week(line, resource, kind, prev):
    parts = [p.strip() for p in line.split("§")]
    if len(parts) != 9:
        raise SystemExit(f"{kind} week needs 9 fields, got {len(parts)}: {line[:80]}")
    title, lab2, lab3, definition, example, trap, drill, why, check = parts
    for label in (title, lab2, lab3):
        if label in BANNED_LABELS:
            raise SystemExit(f"banned label {label} in {title}")
    if len(check) < 12 or len(example) < 12:
        raise SystemExit(f"thin week: {title}")
    goal = definition
    if kind == "ma":
        days = math_days(prev, title, definition, example, trap, drill, why, check)
        outcome = f"{title} 정의와 예를 백지에 다시 쓴 한 장."
    elif kind == "en":
        days = english_days(prev, title, definition, example, trap, drill, why, check)
        outcome = f"{title} 녹음 하나와 고친 문장."
    elif kind == "al":
        days = algo_days(prev, title, definition, example, trap, drill, why, check)
        outcome = f"{title} 손 추적 한 장과 코드."
    else:
        raise SystemExit(kind)
    return {
        "title": title,
        "goal": goal,
        "outcome": outcome,
        "resource": resource,
        "check": check,
        "ideas": [[title, definition], [lab2, example], [lab3, trap]],
        "days": days,
    }


def day(title, blocks):
    total = sum(m for m, _ in blocks)
    if total != 60:
        raise SystemExit(f"{title} sums to {total}")
    if blocks[0][0] != 10:
        raise SystemExit(f"{title} review block is {blocks[0][0]}")
    return {"title": title, "blocks": [{"m": m, "t": t} for m, t in blocks]}


def math_days(prev, title, definition, example, trap, drill, why, check):
    return [
        day(f"{title}의 정의", [
            (10, f"어제 {prev}에서 틀린 계산 하나를 숫자만 바꿔 다시 푼다."),
            (20, definition + " 노트에 적고, 기호마다 한국어 이름을 붙인다."),
            (20, "정의에서 빠지면 안 되는 조건에 밑줄을 긋고, 그 조건이 없는 문장을 하나 써 본다."),
            (10, "노트를 덮고 정의를 한 문장으로 말한다."),
        ]),
        day(f"{title}의 예", [
            (10, "정의를 한 문장으로 다시 말한다."),
            (25, example),
            (15, "같은 유형으로 숫자나 대상만 바꾼 문제를 두 개 더 만들어 푼다."),
            (10, "각 예가 정의의 어느 조건을 쓰는지 번호를 붙인다."),
        ]),
        day(f"{title}이 깨지는 경우", [
            (10, "어제 예 하나를 검산한다."),
            (20, trap),
            (20, "올바른 풀이를 옆에 적고, 두 풀이의 차이를 한 줄로 말한다."),
            (10, "이 실수에 짧은 이름을 붙인다."),
        ]),
        day(f"{title} 문제", [
            (10, "어제 붙인 실수 이름을 말한다."),
            (20, drill),
            (20, "풀이를 가리고 다시 푼 뒤, 결과를 원래 식이나 정의에 넣어 확인한다."),
            (10, "틀린 항목을 개념, 계산, 읽기 중 하나로 표시한다."),
        ]),
        day(f"{title}의 이유", [
            (10, "틀린 항목 하나를 다시 푼다."),
            (20, why),
            (20, "그 이유를 오늘의 예 숫자에 대입해 맞는지 확인한다."),
            (10, "이유를 두 문장으로 줄여 적는다."),
        ]),
        day(f"{title} 백지", [
            (10, "이유 두 문장을 소리 내어 말한다."),
            (40, "노트를 덮고 다음을 백지에 다시 한다. " + example),
            (10, "막힌 줄만 노트를 열어 고친다."),
        ]),
        day(f"{title} 점검", [
            (10, "이번 주 정의만 말한다."),
            (40, check),
            (10, "막힌 한 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 정의를 열지 않는다."),
        ]),
    ]


def english_days(prev, title, model, pattern, trap, speak, write, check):
    return [
        day(f"{title} 소리", [
            (10, f"어제 {prev} 녹음에서 막힌 문장 둘만 다시 말한다."),
            (20, pattern),
            (20, "그 소리를 최소 여섯 번 따라 말하고, 막힌 단어만 표시한다."),
            (10, "새로 익힌 단어 다섯 개만 카드에 적는다. 한국어 해설은 적지 않는다."),
        ]),
        day(f"{title} 모델", [
            (10, "카드 다섯 개를 보고 말한다."),
            (20, model),
            (20, "모델의 고유명사와 숫자만 바꿔 문장 여섯 개를 만든다."),
            (10, "그중 세 문장을 녹음한다."),
        ]),
        day(f"{title} 함정", [
            (10, "어제 녹음 세 문장을 다시 말한다."),
            (20, trap),
            (20, "틀린 문장을 올바른 문장 옆에 적고 차이를 한 단어로 표시한다."),
            (10, "고친 문장 셋을 녹음한다."),
        ]),
        day(f"{title} 말하기", [
            (10, "고친 문장 셋을 노트 없이 말한다."),
            (40, speak),
            (10, "더듬은 곳만 한 줄로 적는다."),
        ]),
        day(f"{title} 쓰기", [
            (10, "말하기에서 더듬은 문장을 다시 말한다."),
            (25, write),
            (15, "쓴 글을 소리 내어 읽고, 말하지 못한 문장을 고친다."),
            (10, "고친 문장만 다시 적는다."),
        ]),
        day(f"{title} 늘리기", [
            (10, "어제 글의 첫 문장을 말한다."),
            (20, "같은 내용으로 질문 두 개와 대답 두 개를 덧붙인다."),
            (20, "전체를 대본 없이 한 번 녹음한다."),
            (10, "녹음과 글을 비교해 다른 단어 세 개만 표시한다."),
        ]),
        day(f"{title} 점검", [
            (10, "이번 주 모델 문장만 말한다."),
            (40, check),
            (10, "막힌 문장 하나를 다음 주 첫날 맨 위에 적는다. 오늘은 새 문법을 열지 않는다."),
        ]),
    ]


def algo_days(prev, title, claim, trace, code, trap, cost, check):
    return [
        day(f"{title} 주장", [
            (10, f"어제 {prev}의 불변이나 연산 횟수를 코드 없이 말한다."),
            (20, claim),
            (20, "그 주장을 다섯 줄 이하의 입력에 대해 참인지 손으로 표시한다."),
            (10, "주장을 한 문장으로 줄인다."),
        ]),
        day(f"{title} 손 추적", [
            (10, "어제 주장 한 문장을 말한다."),
            (25, trace),
            (15, "입력을 하나 바꿔 같은 추적을 다시 한다."),
            (10, "추적이 주장과 어긋나면 그 칸에 표시한다."),
        ]),
        day(f"{title} 구현", [
            (10, "추적한 예 하나를 말한다."),
            (40, code),
            (10, "방금 추적한 예가 코드와 같은 결과를 내는지 확인한다."),
        ]),
        day(f"{title} 반례", [
            (10, "어제 코드를 예 하나로 다시 실행한다."),
            (20, trap),
            (20, "깨진 입력을 코드에 넣어 보고, 고친 뒤 같은 입력을 다시 넣는다."),
            (10, "무엇을 고쳤는지 한 줄로 적는다."),
        ]),
        day(f"{title} 시간", [
            (10, "고친 한 줄을 말한다."),
            (20, cost),
            (20, "입력 크기를 두 배로 하면 연산이 얼마나 늘지 표로 적는다."),
            (10, "그 결론을 한 문장으로 말한다."),
        ]),
        day(f"{title} 설명", [
            (10, "시간 결론을 말한다."),
            (20, "코드를 가리고 추적 과정을 다시 쓴다."),
            (20, "왜 맞는지 세 문장으로 적는다. 불변, 종료, 결과 순이다."),
            (10, "세 문장을 소리 내어 말한다."),
        ]),
        day(f"{title} 점검", [
            (10, "주장 한 문장을 말한다."),
            (40, check),
            (10, "막힌 입력을 다음 주 첫날 맨 위에 적는다. 오늘은 새 구조를 열지 않는다."),
        ]),
    ]


def load_syllabus(phase_rows, kind, old_weeks=None):
    phases = []
    weeks = []
    prev = "시작"
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
        for item in items:
            if isinstance(item, int):
                if old_weeks is None:
                    raise SystemExit(f"copy in {kind}")
                weeks.append(old_weeks[item - 1])
                prev = old_weeks[item - 1]["title"]
            else:
                line = "§".join(item)
                weeks.append(parse_week(line, row["resource"], kind, prev))
                prev = weeks[-1]["title"]
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


def main():
    old = {
        name: json.loads((ROADMAP / f"{name}.json").read_text(encoding="utf-8"))
        for name in ("en", "al", "ma")
    }
    from syllabus_ma import PHASES as MA
    from syllabus_al import PHASES as AL
    from syllabus_en import PHASES as EN
    built = {
        "ma": load_syllabus(MA, "ma"),
        "al": load_syllabus(AL, "al"),
        "en": load_syllabus(EN, "en", old["en"]["weeks"]),
    }
    # Week 13 used to preview present perfect. That unit now starts at week 53.
    built["en"][1][12] = replace_in(
        built["en"][1][12],
        "다음 주 현재완료를 위해",
        "다음 주 복습을 위해",
    )
    check_order(built)
    for name, (phases, weeks) in built.items():
        data = dict(old[name])
        data["phases"] = phases
        data["weeks"] = weeks
        data["destination"] = DEST[name]
        data["limit"] = LIMIT[name]
        path = ROADMAP / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(name, len(weeks), "weeks", len(phases), "phases")


DEST = {
    "ma": "5년 끝에 측도, 적분, 함수공간의 기초를 다루되, 핵심 정리는 증명하고 선택공리가 걸리는 정리는 진술과 스케치로 남긴다. 처음 2년은 연산에서 미적분 계산과 점화식까지이고, 군과 환은 함수해석 뒤에 둔다.",
    "al": "7년 끝에 대학원 알고리즘과 복잡도를 증명하고, 고른 정리 하나를 기술 노트로 남긴다. 1년차는 이분 탐색과 단순한 트리까지이고, 마스터 정리는 수학에서 점화식을 배운 뒤에 쓴다.",
    "en": "7년 끝에 긴 글을 읽고 문장을 고쳐 한 편의 글로 남긴다. 1년차에는 4분 말하기와 정중한 메일을 하고, 3년차에는 회의와 계약 초안을 혼자 다룬다.",
}
LIMIT = {
    "ma": "석사 학위는 이 준비 뒤의 전일제 과정이다. 이 5년은 그 수업 내용까지이고 학위 논문의 지도는 포함하지 않는다. 고유값과 마스터 정리는 1년차에 두지 않는다.",
    "al": "학위 논문은 이 노트 뒤의 전일 연구다. 이 트랙은 과목과 기술 노트까지이고, 대회 순위는 목표로 두지 않는다. 고속 푸리에 변환은 아이디어와 다항식 곱까지다.",
    "en": "변호사 자격은 학사 이후의 전일제 법학 과정이다. 이 트랙은 문장 훈련이며 법률 자문이 아니다. 포트폴리오는 책의 구조를 배운 뒤의 메모로 묶으며, 1년차에 계약을 다루지 않는다.",
}


def find(weeks, needle):
    hits = [i + 1 for i, w in enumerate(weeks) if needle in json.dumps(w, ensure_ascii=False)]
    if not hits:
        raise SystemExit(f"missing {needle}")
    return hits[0]


def find_title(weeks, needle):
    hits = [i + 1 for i, w in enumerate(weeks) if needle in w["title"]]
    if not hits:
        raise SystemExit(f"missing title {needle}")
    return hits[0]


def replace_in(node, old, new):
    if isinstance(node, dict):
        return {k: replace_in(v, old, new) for k, v in node.items()}
    if isinstance(node, list):
        return [replace_in(v, old, new) for v in node]
    if isinstance(node, str):
        return node.replace(old, new)
    return node


def check_order(built):
    ma = built["ma"][1]
    al = built["al"][1]
    en = built["en"][1]
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
    # Conversational "shall we" sits in the preserved business block (weeks 79–91).
    # Obligation shall, NDA, and redlines start with the contract block at week 105.
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


if __name__ == "__main__":
    main()
