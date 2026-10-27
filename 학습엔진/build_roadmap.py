# -*- coding: utf-8 -*-
"""Rebuild roadmap JSON from syllabus text. Source of the week sequence."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
ROADMAP = ROOT / "roadmap"
SRC = ROOT / "syllabus"

BANNED_LABELS = {"목표", "확인", "범위"}


def particle_eul(word):
    """을 after a batchim, 를 after a vowel."""
    last = word[-1] if word else ""
    code = ord(last) if last else 0
    if 0xAC00 <= code <= 0xD7A3 and (code - 0xAC00) % 28 == 0:
        return "를"
    return "을"


def focus_line(text, limit=110):
    """First sentence of a week's own material, so a 10-minute cue names that material."""
    text = " ".join(str(text).split())
    if not text:
        return ""
    matched = re.search(r".+?다\.", text)
    line = matched.group(0).strip() if matched else text
    if len(line) > limit:
        line = line[: limit - 1].rstrip() + "…"
    return line


def with_focus(lead, text):
    line = focus_line(text)
    if not line:
        return lead
    return lead + " " + line


def parse_week(line, resource, kind, prev, week_no=0, practice="code", prev_line=""):
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
        days = math_days(prev, title, definition, example, trap, drill, why, thicken_math_check(week_no, check), week_no, prev_line)
        outcome = f"{title} 정의와 예를 백지에 다시 쓴 한 장."
    elif kind == "en":
        days = english_days(prev, title, definition, example, trap, drill, why, check, prev_line)
        outcome = f"{title} 녹음 하나와 고친 문장."
    elif kind == "al":
        days = algo_days(prev, title, definition, example, example, trap, why, check, practice, prev_line)
        outcome = f"{title} 증명 한 장." if practice == "proof" else f"{title} 손 추적 한 장과 코드."
    elif kind == "sw":
        days = sw_days(prev, title, definition, example, trap, drill, why, check, prev_line)
        outcome = f"{title} 커밋 또는 한 페이지 노트."
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


def thicken_math_check(week_no, check):
    """Years 1–2 checks that name one or two calculations get a full set."""
    if week_no > 104:
        return check
    if any(word in check for word in ("증명", "귀납", "대우", "반례")):
        return check
    counts = [int(n) for n in re.findall(r"(\d+)\s*(?:개|문제|식|문항)", check)]
    if counts and max(counts) >= 3:
        return check
    return (
        check
        + " 위에 적힌 계산이 여덟 문제보다 적으면 숫자만 바꾼 문제를 만들어 여덟 문제를 채운다. "
        + "각 답을 검산하고, 여덟 문제를 끝내기 전에는 해설을 보지 않는다."
    )


def thicken_english_week(week):
    """Preserved weeks keep their own days. Long slots that only ask for a short take get repeats."""
    week = json.loads(json.dumps(week))
    for one in week["days"]:
        for block in one["blocks"]:
            if english_block_needs_fill(block["m"], block["t"]):
                block["t"] = block["t"] + (
                    f" 이 칸은 {block['m']}분이다. 한 번이 1분에서 3분이면 소재만 바꿔 같은 과제를 반복한다. "
                    "녹음은 최소 세 번이고, 각 녹음 뒤에 막힌 문장만 고쳐 다시 말한다. "
                    f"세 번으로 {block['m']}분을 채우지 못하면 새 소재로 두 번 더 해 그 칸의 분을 채운다. 마지막 녹음 전에는 대본을 보지 않는다."
                )
    return week


def english_block_needs_fill(minutes, text):
    if minutes < 15:
        return False
    if "분을 채운다" in text or "세 번과 고치기" in text:
        return False
    if re.search(r"(?:1[2-9]|[2-9]\d)\s*(?:개|문장|문제|쌍|단어|문항)", text):
        return False
    if re.search(r"60초|90초|1분|3분", text):
        return True
    counts = [int(n) for n in re.findall(r"(\d+)\s*(?:개|문장|질문)", text)]
    return bool(counts) and max(counts) <= 8 and minutes >= 30


def thicken_math_blank(week_no, example):
    """Calculation weeks redo one example on the blank day. That one line does not fill 40 minutes."""
    base = "노트를 덮고 다음을 백지에 다시 한다. " + example
    if week_no > 104:
        return base
    if any(word in example for word in ("증명", "귀납", "대우", "반례")):
        return base
    counts = [int(n) for n in re.findall(r"(\d+)\s*(?:개|문제|식|문항)", example)]
    if counts and max(counts) >= 3:
        return base
    return (
        base
        + " 이 예만으로 40분이 차지 않으면 숫자만 바꾼 문제를 만들어 여덟 문제가 될 때까지 백지에서 푼다. "
        + "각 답을 검산하고, 여덟 문제를 끝내기 전에는 노트를 열지 않는다."
    )


def math_days(prev, title, definition, example, trap, drill, why, check, week_no=0, prev_line=""):
    if prev == "시작":
        opening = with_focus(
            f"오늘은 '{title}'{particle_eul(title)} 시작한다. 다음 예를 노트에 베끼지 않고, 첫 단계의 결과만 적는다.",
            example,
        )
    elif week_no <= 104:
        opening = with_focus(
            f"지난주 '{prev}'의 다음 계산을 노트를 덮고 다시 푼다. 숫자만 하나 바꿔 같은 계산을 한 번 더 하고 검산한다.",
            prev_line,
        )
    else:
        opening = with_focus(
            f"지난주 '{prev}'에서 적은 다음 문장을 노트를 덮고 다시 말하고, 그 문장의 첫 근거를 한 줄로 적는다.",
            prev_line,
        )
    return [
        day(f"{title}의 정의", [
            (10, opening),
            (20, definition + " 노트에 적고, 기호마다 한국어 이름을 붙인다."),
            (20, "정의에서 빠지면 안 되는 조건에 밑줄을 긋고, 그 조건이 없는 문장을 하나 써 본다."),
            (10, with_focus(f"노트를 덮고 '{title}'의 정의를 말한다.", definition)),
        ]),
        day(f"{title}의 예", [
            (10, with_focus(f"어제 노트에 적은 '{title}' 정의를 덮고 말한다.", definition)),
            (25, example),
            (15, "같은 유형으로 숫자나 대상만 바꾼 문제를 두 개 더 만들어 푼다."),
            (10, "각 예가 정의의 어느 조건을 쓰는지 번호를 붙인다."),
        ]),
        day(f"{title}이 깨지는 경우", [
            (10, with_focus(f"어제 푼 '{title}'의 다음 예를 검산한다.", example)),
            (20, trap),
            (20, "올바른 풀이를 옆에 적고, 두 풀이의 차이를 한 줄로 말한다."),
            (10, "이 실수에 짧은 이름을 붙인다."),
        ]),
        day(f"{title} 문제", [
            (10, with_focus(f"어제 '{title}'에 붙인 실수 이름을 말한다. 그 실수는 다음이다.", trap)),
            (20, drill),
            (20, "풀이를 가리고 다시 푼 뒤, 결과를 원래 식이나 정의에 넣어 확인한다."),
            (10, "틀린 항목을 개념, 계산, 읽기 중 하나로 표시한다."),
        ]),
        day(f"{title}의 이유", [
            (10, with_focus(f"어제 '{title}' 문제에서 틀렸다고 표시한 항목을 다시 푼다. 문제는 다음이다.", drill)),
            (20, why),
            (20, "그 이유를 오늘의 예 숫자에 대입해 맞는지 확인한다."),
            (10, "이유를 두 문장으로 줄여 적는다."),
        ]),
        day(f"{title} 백지", [
            (10, with_focus(f"어제 적은 '{title}'의 이유 두 문장을 소리 내어 말한다.", why)),
            (40, thicken_math_blank(week_no, example)),
            (10, "막힌 줄만 노트를 열어 고친다."),
        ]),
        day(f"{title} 점검", [
            (10, with_focus(f"이번 주 '{title}' 정의만 노트를 덮고 말한다.", definition)),
            (40, check),
            (10, "막힌 한 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 정의를 열지 않는다."),
        ]),
    ]


def english_days(prev, title, model, pattern, trap, speak, write, check, prev_line=""):
    if prev == "시작":
        opening = with_focus(
            f"오늘은 '{title}'{particle_eul(title)} 시작한다. 다음 모델 문장을 한 번 듣고 그대로 따라 말한다.",
            model,
        )
    else:
        opening = with_focus(
            f"지난주 '{prev}' 녹음에서 막힌 문장 둘만 다시 말한다. 그 주의 문장은 다음이다.",
            prev_line,
        )
    return [
        day(f"{title} 소리", [
            (10, opening),
            (20, pattern),
            (20, "그 소리를 최소 여섯 번 따라 말하고, 막힌 단어만 표시한다."),
            (10, "새로 익힌 단어 다섯 개만 카드에 적는다. 한국어 해설은 적지 않는다."),
        ]),
        day(f"{title} 모델", [
            (10, with_focus(f"어제 '{title}'에서 카드에 적은 단어 다섯 개를 보고 말한다. 오늘의 모델 문장은 다음이다.", model)),
            (20, model),
            (20, "모델의 고유명사와 숫자만 바꿔 문장 여섯 개를 만든다."),
            (10, "그중 세 문장을 녹음한다."),
        ]),
        day(f"{title} 함정", [
            (10, with_focus(f"어제 '{title}'에서 녹음한 세 문장을 다시 말한다. 모델 문장은 다음이다.", model)),
            (20, trap),
            (20, "틀린 문장을 올바른 문장 옆에 적고 차이를 한 단어로 표시한다."),
            (10, "고친 문장 셋을 녹음한다."),
        ]),
        day(f"{title} 말하기", [
            (10, with_focus(f"어제 '{title}'에서 고친 문장 셋을 노트 없이 말한다. 고친 함정은 다음이다.", trap)),
            (40, speak + " 준비 뒤에 녹음하고, 막힌 문장만 고쳐 다시 녹음한 다음, 소재를 바꿔 같은 과제를 한 번 더 한다. 한 번이 짧아도 세 번과 고치기로 40분을 채운다. 대본은 마지막 녹음 뒤에만 본다."),
            (10, "더듬은 곳만 한 줄로 적는다."),
        ]),
        day(f"{title} 쓰기", [
            (10, with_focus(f"어제 '{title}' 말하기에서 더듬은 문장을 다시 말한다. 말할 과제는 다음이다.", speak)),
            (25, write + " 같은 과제의 문단을 두 개 더 쓴다. 각 문단은 여섯 줄 이상이다. 시간이 남으면 소리 내어 읽고 문장마다 한 군데를 고친다."),
            (15, "쓴 글을 소리 내어 읽고, 말하지 못한 문장을 고친다."),
            (10, "고친 문장만 다시 적는다."),
        ]),
        day(f"{title} 늘리기", [
            (10, with_focus(f"어제 '{title}'에서 쓴 글의 첫 문장을 말한다. 쓰기 과제는 다음이다.", write)),
            (20, f"어제 '{title}' 글에서 다음 함정이 남은 문장을 고친다. " + trap),
            (20, "고친 글을 3분 이상 대본 없이 녹음한다. 막히면 그 문장만 적고 이어서 말한다."),
            (10, "녹음과 글을 비교해 다른 단어 세 개만 표시한다."),
        ]),
        day(f"{title} 점검", [
            (10, with_focus(f"이번 주 '{title}'의 모델 문장만 말한다.", model)),
            (40, check + " 한 번이 40분을 채우지 못하면 소재를 바꿔 같은 점검을 두 번 더 한다. 세 번 모두 고친 문장을 남긴다."),
            (10, "막힌 문장 하나를 다음 주 첫날 맨 위에 적는다. 오늘은 새 문법을 열지 않는다."),
        ]),
    ]


def algo_days(prev, title, claim, trace, code, trap, cost, check, practice="code", prev_line=""):
    if prev == "시작":
        opening = with_focus(
            f"오늘은 '{title}'{particle_eul(title)} 코드 없이 시작한다. 다음 예를 손으로 한 줄씩 따라가고, 각 줄의 결과만 적는다.",
            trace,
        )
    elif practice == "proof":
        opening = with_focus(
            f"지난주 '{prev}'의 가정과 결론을 코드 없이 말한다. 그 내용은 다음이다.",
            prev_line,
        )
    else:
        opening = with_focus(
            f"지난주 '{prev}'의 다음 예를 코드 없이 다시 따라간다.",
            prev_line,
        )
    if practice == "proof":
        return [
            day(f"{title} 주장", [
                (10, opening),
                (20, claim),
                (20, "그 주장을 다섯 줄 이하의 예로 참인지 손으로 표시한다."),
                (10, "주장을 한 문장으로 줄인다."),
            ]),
            day(f"{title} 전개", [
                (10, with_focus(f"어제 줄인 '{title}' 주장을 말한다.", claim)),
                (25, trace + " 각 문장이 앞 문장에서 나오는지 번호를 붙인다. 문장이 다섯 줄보다 짧으면 예 숫자를 옆에 전개해 한 줄을 더 만든다."),
                (15, "예 숫자를 하나 더 넣어 같은 전개를 다시 한다."),
                (10, "전개가 주장과 어긋나면 그 줄에 표시한다."),
            ]),
            day(f"{title} 증명", [
                (10, with_focus(f"어제 '{title}'에서 전개한 예를 말한다.", trace)),
                (40, "오늘 주장을 증명으로 적는다. " + code + " 첫 25분은 가정, 핵심, 결론의 세 단락을 쓴다. 이 문장을 코드로 실행하지 않는다. 남은 15분은 예 숫자를 단락 옆에 넣어 어긋나는 줄을 고친다. 해설은 25분이 지나기 전에는 열지 않는다."),
                (10, "세 단락이 예 숫자와 맞는지 한 줄로 말한다."),
            ]),
            day(f"{title} 반례", [
                (10, with_focus(f"어제 '{title}' 증명에서 핵심 문장을 말한다. 예는 다음이다.", code)),
                (20, trap),
                (20, "그 실패가 생기는 입력을 만들고, 어느 단락이 깨지는지 적는다. 가정을 되돌리면 그 입력이 사라지는지 확인한다."),
                (10, "무엇을 고쳤는지 한 줄로 적는다."),
            ]),
            day(f"{title} 이유", [
                (10, with_focus(f"어제 '{title}'에서 고친 한 줄을 말한다. 그 실패는 다음이다.", trap)),
                (20, cost),
                (20, "그 이유를 예 숫자에 대입해 세 줄로 확인한다."),
                (10, "그 결론을 한 문장으로 말한다."),
            ]),
            day(f"{title} 설명", [
                (10, with_focus(f"어제 적은 '{title}'의 이유 한 문장을 말한다.", cost)),
                (20, "증명을 가리고 가정, 핵심, 결론을 다시 쓴다."),
                (20, "왜 맞는지 세 문장으로 적는다. 가정, 핵심, 결론 순이다."),
                (10, "세 문장을 소리 내어 말한다."),
            ]),
            day(f"{title} 점검", [
                (10, with_focus(f"이번 주 '{title}' 주장을 말한다.", claim)),
                (40, check + " 백지에서 증명을 다시 쓰고 예 하나를 단락 옆에 붙인다. 코드를 새로 짜는 것으로 이 칸을 대신하지 않는다."),
                (10, "막힌 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 정리를 열지 않는다."),
            ]),
        ]
    return [
        day(f"{title} 주장", [
            (10, opening),
            (20, claim),
            (20, "그 주장을 다섯 줄 이하의 입력에 대해 참인지 손으로 표시한다."),
            (10, "주장을 한 문장으로 줄인다."),
        ]),
        day(f"{title} 손 추적", [
            (10, with_focus(f"어제 줄인 '{title}' 주장을 말한다.", claim)),
            (25, trace + " 변수 값을 줄마다 표로 적는다. 표가 짧으면 입력을 바꿔 표를 한 번 더 만든다."),
            (15, "입력을 하나 바꿔 같은 추적을 다시 한다."),
            (10, "추적이 주장과 어긋나면 그 칸에 표시한다."),
        ]),
        day(f"{title} 구현", [
            (10, with_focus(f"어제 '{title}'에서 추적한 예를 말한다.", trace)),
            (40, "오늘 예제를 코드로 작성해 실행한다. " + code + " 입력을 바꾼 경우를 두 개 더 같은 코드로 실행하고, 각 출력과 손 추적 표를 나란히 적는다. 25분이 지나기 전에는 해설을 보지 않는다."),
            (10, "방금 추적한 예가 코드와 같은 결과를 내는지 확인한다."),
        ]),
        day(f"{title} 반례", [
            (10, with_focus(f"어제 '{title}' 코드를 다음 예로 다시 실행한다.", trace)),
            (20, trap),
            (20, "깨진 입력을 코드에 넣어 보고, 고친 뒤 같은 입력을 다시 넣는다."),
            (10, "무엇을 고쳤는지 한 줄로 적는다."),
        ]),
        day(f"{title} 시간", [
            (10, with_focus(f"어제 '{title}'에서 고친 한 줄을 말한다. 그 실패는 다음이다.", trap)),
            (20, cost),
            (20, "입력 크기를 두 배로 하면 연산이 얼마나 늘지 표로 적는다."),
            (10, "그 결론을 한 문장으로 말한다."),
        ]),
        day(f"{title} 설명", [
            (10, with_focus(f"어제 적은 '{title}'의 시간 결론을 말한다.", cost)),
            (20, "코드를 가리고 추적 과정을 다시 쓴다."),
            (20, "왜 맞는지 세 문장으로 적는다. 불변, 종료, 결과 순이다."),
            (10, "세 문장을 소리 내어 말한다."),
        ]),
        day(f"{title} 점검", [
            (10, with_focus(f"이번 주 '{title}' 주장을 말한다.", claim)),
            (40, check + " 백지에서 코드를 다시 작성하고, 입력을 바꾼 한 경우를 더 실행한다."),
            (10, "막힌 입력을 다음 주 첫날 맨 위에 적는다. 오늘은 새 구조를 열지 않는다."),
        ]),
    ]


def sw_days(prev, title, rule, case, mistake, work, why, check, prev_line=""):
    if prev == "시작":
        opening = with_focus(
            f"오늘은 '{title}'{particle_eul(title)} 시작한다. 이미 아는 저장소에서 최근 커밋 하나를 고르고, 그 커밋의 첫 줄과 고친 파일 이름을 적는다. 오늘 기준의 첫 문장은 다음이다.",
            rule,
        )
    else:
        opening = with_focus(
            f"지난주 '{prev}'의 기준 문장을 노트를 덮고 말한다. 그 기준은 다음이다.",
            prev_line,
        )
    return [
        day(f"{title} 기준", [
            (10, opening),
            (20, rule + " 노트에 적고, 이미 아는 코드의 최근 변경 하나에 대어 본다."),
            (20, "지킨 점과 벗어난 점을 각 두 줄로 적는다. 해당 파일이 없으면 그 사실을 적고 다른 변경을 고른다."),
            (10, "기준을 한 문장으로 줄여 적는다."),
        ]),
        day(f"{title} 사례", [
            (10, with_focus(f"어제 '{title}'에서 한 문장으로 줄여 적은 기준을 노트를 덮고 말한다.", rule)),
            (25, case + " 고른 자리의 파일과 줄을 따라 적는다. 열 줄이 안 되면 같은 종류의 두 번째 자리를 더 따라간다."),
            (15, "기준에 맞는 줄과 어긋난 줄에 표시한다."),
            (10, "어긋난 줄의 파일 이름을 적는다."),
        ]),
        day(f"{title} 적용", [
            (10, with_focus(f"어제 '{title}' 사례에서 기준과 어긋난다고 표시한 파일 이름과 그 줄을 말한다. 그 기준은 다음이다.", rule)),
            (40, work + " 산출은 커밋 하나이거나 한 페이지 노트다. 첫 25분은 그 산출을 만들고, 남은 15분은 기준에 맞춰 고친다. 언어 문법과 빌드 설정은 이 시간에 다루지 않는다."),
            (10, "커밋 제목이나 노트 제목을 한 줄로 적는다."),
        ]),
        day(f"{title} 실패", [
            (10, with_focus(f"어제 '{title}'에서 남긴 커밋 제목이나 노트 제목을 한 줄로 말한다. 적용한 기준은 다음이다.", rule)),
            (20, mistake),
            (20, "그 실패를 한 번 만든 뒤 되돌리고, 되돌리기 전과 후의 차이를 다섯 줄로 적는다."),
            (10, "실패에 짧은 이름을 붙인다."),
        ]),
        day(f"{title} 이유", [
            (10, with_focus(f"어제 '{title}'에 붙인 실패 이름을 말한다. 그 주의 기준은 다음이다.", rule)),
            (20, why),
            (20, f"이유를 어제 '{title}' 산출의 두 곳에 대입해 맞는지 적는다. 산출은 커밋 하나이거나 한 페이지 노트다."),
            (10, "이유를 두 문장으로 줄인다."),
        ]),
        day(f"{title} 설명", [
            (10, with_focus(f"어제 적은 '{title}'의 이유 두 문장을 말한다. 기준은 다음이다.", rule)),
            (20, "산출을 가리고 무엇을 바꿨는지 다시 쓴다."),
            (20, "지킨 규칙과 거절한 규칙을 세 문장으로 적는다."),
            (10, "세 문장을 소리 내어 말한다."),
        ]),
        day(f"{title} 점검", [
            (10, with_focus(f"이번 주 '{title}' 기준을 한 문장으로 말한다.", rule)),
            (40, check + " 노트를 덮고 다른 자리 하나에 40분 안에 다시 적용한다. 커밋이나 노트 제목이 남아야 이 주가 끝난다."),
            (10, "막힌 한 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 기준을 열지 않는다."),
        ]),
    ]


def load_syllabus(phase_rows, kind, old_weeks=None):
    phases = []
    weeks = []
    prev = "시작"
    prev_line = ""
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
        if kind == "al" and phase["start"] >= 157 and phase["start"] != 183:
            practice = "proof"
        for item in items:
            if isinstance(item, int):
                if old_weeks is None:
                    raise SystemExit(f"copy in {kind}")
                copied = old_weeks[item - 1]
                weeks.append(copied)
                prev = copied["title"]
                prev_line = focus_line(copied.get("goal") or copied.get("check") or "")
            else:
                line = "§".join(item)
                weeks.append(parse_week(line, row["resource"], kind, prev, len(weeks) + 1, practice, prev_line))
                prev = weeks[-1]["title"]
                prev_line = focus_line(weeks[-1]["ideas"][1][1])
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


def kept_english():
    """Hand-written weeks, in the order syllabus_en.py indexes: 1–13, old 14–26, 27–39, 40–52."""
    path = ROADMAP / "en_kept.json"
    if not path.exists():
        raise SystemExit("missing roadmap/en_kept.json")
    weeks = json.loads(path.read_text(encoding="utf-8"))
    if len(weeks) != 52:
        raise SystemExit(f"en_kept has {len(weeks)} weeks")
    return [thicken_english_week(week) for week in weeks]


def main():
    old = {
        name: json.loads((ROADMAP / f"{name}.json").read_text(encoding="utf-8"))
        for name in ("en", "al", "ma")
    }
    from syllabus_ma import PHASES as MA
    from syllabus_al import PHASES as AL
    from syllabus_en import PHASES as EN
    from syllabus_sw import PHASES as SW
    built = {
        "ma": load_syllabus(MA, "ma"),
        "al": load_syllabus(AL, "al"),
        "en": load_syllabus(EN, "en", kept_english()),
        "sw": load_syllabus(SW, "sw"),
    }
    check_order(built)
    for name, (phases, weeks) in built.items():
        data = dict(SW_BASE if name == "sw" else old[name])
        data["phases"] = phases
        data["weeks"] = weeks
        data["destination"] = DEST[name]
        data["limit"] = LIMIT[name]
        data["hour"] = HOUR[name]
        path = ROADMAP / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(name, len(weeks), "weeks", len(phases), "phases")


DEST = {
    "ma": "5년 끝에 측도, 적분, 함수공간의 기초를 다루되, 핵심 정리는 증명하고 선택공리가 걸리는 정리는 진술과 스케치로 남긴다. 처음 2년은 연산에서 미적분 계산과 점화식까지이고, 군과 환은 함수해석 뒤에 둔다.",
    "al": "7년 끝에 대학원 알고리즘과 복잡도를 증명하고, 고른 정리 하나를 기술 노트로 남긴다. 1년차는 이분 탐색과 단순한 트리까지이고, 마스터 정리는 수학에서 점화식을 배운 뒤에 쓴다.",
    "en": "7년 끝에 긴 글을 읽고 문장을 고쳐 한 편의 글로 남긴다. 1년차에는 4분 말하기와 정중한 메일을 하고, 3년차에는 회의와 계약 초안을 혼자 다룬다.",
    "sw": "5년 끝에 한 페이지 설계 노트를 남긴다. 7년 끝에는 그 노트와 연결한 프로젝트 기록 한 페이지를 남긴다. 설계 노트는 260주, 프로젝트 기록은 364주다.",
}
LIMIT = {
    "ma": "석사 학위는 이 준비 뒤의 전일제 과정이다. 이 5년은 그 수업 내용까지이고 학위 논문의 지도는 포함하지 않는다. 고유값과 마스터 정리는 1년차에 두지 않는다.",
    "al": "학위 논문은 이 노트 뒤의 전일 연구다. 이 트랙은 과목과 기술 노트까지이고, 대회 순위는 목표로 두지 않는다. 고속 푸리에 변환은 아이디어와 다항식 곱까지다.",
    "en": "변호사 자격은 학사 이후의 전일제 법학 과정이다. 이 트랙은 문장 훈련이며 법률 자문이 아니다. 포트폴리오는 책의 구조를 배운 뒤의 메모로 묶으며, 1년차에 계약을 다루지 않는다.",
    "sw": "언어 문법, 첫 프로그램, 빌드 도구 사용법은 다루지 않는다. 직함, 여러 팀의 조직 운영, 자격시험, 배포 플랫폼 운영은 포함하지 않는다. 비밀은 커밋하지 않고, 입력은 경계에서 거절한다.",
}


HOUR = {
    "ma": [
        ["10분", "첫 주에는 오늘 예의 첫 단계 결과만 적는다. 그다음 주부터는 지난주 예의 첫 문장을 노트를 덮고 다시 푼다."],
        ["15분", "오늘 정의와 한 줄 직관을 적는다. 공식은 그 다음이다."],
        ["30분", "문제를 푼다. 풀이를 가리고 시작하고, 해는 원래 식에 넣는다."],
        ["5분", "오답을 개념, 계산, 읽기 중 하나로 표시한다."],
    ],
    "al": [
        ["10분", "첫 주에는 오늘 예를 코드 없이 한 줄씩 따라간다. 그다음 주부터는 지난주 예의 첫 문장을 코드 없이 말한다."],
        ["15분", "오늘 개념을 작은 예시로 종이 위에서 추적한다."],
        ["30분", "구현하거나 문제를 푼다. 25분이 지나기 전에는 해설을 보지 않는다."],
        ["5분", "막힌 지점과 복잡도, 또는 불변 한 줄을 적는다."],
    ],
    "en": [
        ["10분", "이번 주 모델 문장을 소리 내어 말한다. 지난주가 있으면 그 주에서 막힌 문장 둘을 먼저 말한다."],
        ["20분", "오늘 개념 하나만 예문으로 듣고 읽는다."],
        ["20분", "직접 말하거나 쓴다. 녹음이나 초고가 남아야 한다."],
        ["10분", "막힌 문장과 오늘 새로 쓴 단어 5개만 카드에 남긴다. 한국어 해설은 적지 않는다."],
    ],
    "sw": [
        ["10분", "이번 주 기준의 첫 문장을 최근 커밋의 첫 줄과 파일 이름에 댄다. 지난주가 있으면 그 주 기준의 첫 문장을 노트를 덮고 먼저 말한다."],
        ["20분", "오늘 기준 하나를 이미 아는 변경에 댄다."],
        ["25분", "커밋 하나 또는 한 페이지 노트를 남긴다."],
        ["5분", "지킨 규칙과 거절한 규칙을 한 문장으로 적는다."],
    ],
}


SW_BASE = {
    "id": "sw",
    "name": "소프트웨어",
    "color": "#245c3a",
    "hourTitle": "기준을 코드에 대다",
    "hour": HOUR["sw"],
    "after": "설계 노트와 프로젝트 기록을 분기마다 한 장씩 고친다.",
    "soft": "#e7f0ea",
    "confirm": "why",
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
    sw = built["sw"][1]
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
    al = built["al"][1]
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
    if "코드로 작성해 실행" in note or "증명으로 적는다" not in note:
        raise SystemExit("algo note week 364 still executes the sentence")
    flow = al[182]["days"][2]["blocks"][1]["t"]
    if al[182]["title"] != "용량과 유량" or "코드로 작성" not in flow:
        raise SystemExit("flow implementation lost its code hour")
    math_check = built["ma"][1][3]["days"][6]["blocks"][1]["t"]
    if "여덟 문제" not in math_check:
        raise SystemExit("math week 4 check was not thickened")
    if "여덟 문제" in built["ma"][1][104]["days"][6]["blocks"][1]["t"]:
        raise SystemExit("math analysis check was thickened")
    blank = built["ma"][1][1]["days"][5]["blocks"][1]["t"]
    if "48×21" not in blank or "여덟 문제" not in blank:
        raise SystemExit("math week 2 blank day was not thickened")
    if "여덟 문제" in built["ma"][1][104]["days"][5]["blocks"][1]["t"]:
        raise SystemExit("math analysis blank was thickened")
    kept_blob = json.dumps(built["en"][1][0], ensure_ascii=False)
    if "60초" not in kept_blob or "분을 채운다" not in kept_blob:
        raise SystemExit("kept english hour was not filled")
    speak = built["en"][1][13]["days"][3]["blocks"][1]["t"]
    if "세 번" not in speak:
        raise SystemExit("english speak hour was not expanded")
    short = [
        b["t"]
        for d in built["en"][1][1]["days"]
        for b in d["blocks"]
        if 15 <= b["m"] < 25 and "60초" in b["t"]
    ]
    if not short or any("분을 채운다" not in t for t in short):
        raise SystemExit("kept english 15-20 minute take was not filled")
    openings = {
        "ma": built["ma"][1][0]["days"][0]["blocks"][0]["t"],
        "al": built["al"][1][0]["days"][0]["blocks"][0]["t"],
        "sw": built["sw"][1][0]["days"][0]["blocks"][0]["t"],
    }
    expected = {"ma": "3+4×2", "al": "[1, 3, 5, 7, 9]", "sw": "한 커밋에는 한 이유"}
    for kind, text in openings.items():
        if "어제 시작" in text or expected[kind] not in text:
            raise SystemExit(f"{kind} week 1 opener is still vague")
    sw_days = built["sw"][1][0]["days"]
    if "한 커밋에는 한 이유" not in sw_days[1]["blocks"][0]["t"]:
        raise SystemExit("sw day 2 opener does not name the rule")
    if "파일 이름" not in sw_days[2]["blocks"][0]["t"]:
        raise SystemExit("sw day 3 opener does not name the line")
    second = built["ma"][1][1]["days"][0]["blocks"][0]["t"]
    if "계산 순서" not in second or "3+4×2" not in second:
        raise SystemExit("math week 2 opener does not name last week's example")
    vague = ("어제 한 문장을 말한다.", "어제 표시한 줄을 말한다.", "어제 시작에서")
    for kind in ("ma", "al", "en", "sw"):
        blob = json.dumps(built[kind][1], ensure_ascii=False)
        for phrase in vague:
            if phrase in blob:
                raise SystemExit(f"{kind} still has vague cue: {phrase}")


if __name__ == "__main__":
    main()
