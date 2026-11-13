# -*- coding: utf-8 -*-
"""Software design & architecture DSL parser (`title :: rule / lens / tradeoff / scenario`)."""
import re

from curriculum.common import phase

RES_BY_STAGE = (
    (52, (
        "Pro Git(스코트 샤콘·벤 스트라우브), Conventional Commits / Semantic Versioning 명세. "
        "기초 문법이 아니라 변경 단위·브랜치·이력 호환성·릴리스 경계를 상반된 전략으로 대조한다."
    )),
    (104, (
        "A Philosophy of Software Design(존 아우스터하우트), Clean Code(로버트 마틴). "
        "복잡도, 깊은 모듈, 작은 함수 분할이라는 정면으로 충돌하는 두 설계 철학을 같은 코드 사례 위에서 비교한다."
    )),
    (156, (
        "A Philosophy of Software Design(주석·오류 정의), Clean Code(이름·테스트), Refactoring(마틴 파울러). "
        "규칙을 교리처럼 암기하지 않고 오류 경계·테스트 취약성·원칙의 거절 조건을 사례로 비교한다."
    )),
    (208, (
        "Refactoring(마틴 파울러), Clean Architecture(로버트 마틴), 디자인 패턴 핵심 장. "
        "패턴을 외워서 많이 쓰는 대신 변경 축과 결합 비용에 따라 채택하거나 제거하는 기준을 비교한다."
    )),
    (260, (
        "Clean Architecture(로버트 마틴), 파르나스(Parnas) 모듈 분할 기준, Fundamentals of Software Architecture(마크 리처즈·닐 포드). "
        "정보 은닉과 단방향 의존·상태 일관성 경계를 설계 노트로 묶는다."
    )),
    (312, (
        "Designing Data-Intensive Applications(마틴 클레프만), Domain-Driven Design 핵심 장(에릭 에반스·블라드 코노노프). "
        "도메인/데이터 모델, 비동기 흐름, 동시성 격리의 트레이드오프를 대조한다."
    )),
    (364, (
        "Designing Data-Intensive Applications(마틴 클레프만), Building Evolutionary Architectures(닐 포드 외), Michael Nygard ADR·Release It! 복원력 패턴. "
        "장애 격리와 진화적 설계를 아키텍처 의사결정 기록(ADR) 핸드북으로 종합한다."
    )),
)


def resource_for(start):
    """Select the stage resource description covering the given global start week."""
    for limit, res in RES_BY_STAGE:
        if start <= limit:
            return res
    return RES_BY_STAGE[-1][1]


def _end_dot(text):
    text = text.strip()
    if not text:
        return ""
    if text[-1] in ".!?":
        return text
    return text + "."


def _trim_parens(text):
    out = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return re.sub(r"\s{2,}", " ", "".join(out)).strip()


def _split_top(text, sep, maxsplit=None):
    """Split on top-level sep separators, ignoring separators inside parentheses or backticks."""
    parts = []
    cur = []
    depth = 0
    in_tick = False
    i = 0
    n = len(text)
    step = len(sep)
    while i < n:
        ch = text[i]
        if ch == "`":
            in_tick = not in_tick
            cur.append(ch)
            i += 1
            continue
        if not in_tick:
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
            elif depth == 0 and (maxsplit is None or len(parts) < maxsplit) and text.startswith(sep, i):
                parts.append("".join(cur).strip())
                cur = []
                i += step
                continue
        cur.append(ch)
        i += 1
    parts.append("".join(cur).strip())
    return parts


def _sw_labels(lens, tradeoff):
    parts = _split_top(lens, " vs ", 1)
    first = _trim_parens(parts[0])
    if len(parts) == 2:
        second = _trim_parens(parts[1])
        first_short = re.sub(r"\s*관점$", "", first).strip()
        second_short = re.sub(r"\s*관점$", "", second).strip()
        if len(first_short) + len(second_short) <= 28:
            lab2 = f"대비: {first_short} vs {second_short}"
        else:
            lab2 = f"대비: {first}"
    else:
        lab2 = f"대비: {first}"

    matched = re.search(r"줄어드는 비용:\s*(.+)$", tradeoff)
    if matched:
        reduced = _split_top(matched.group(1), ",", 1)[0]
        lab3 = f"비용: {_trim_parens(reduced)}"
    else:
        lab3 = "비용 균형"
    return lab2, lab3


def S(title, job):
    """Parse one `title :: rule / lens / tradeoff / scenario` week specification into a 9-tuple."""
    parts = _split_top(job, " / ", 3)
    if len(parts) != 4 or any(not p for p in parts):
        raise SystemExit(
            f"sw week '{title}' must have 4 ' / '-separated fields "
            f"(rule / lens / tradeoff / scenario), got {len([p for p in parts if p])}"
        )
    rule, lens, tradeoff, scenario = parts
    lab2, lab3 = _sw_labels(lens, tradeoff)
    scenario_short = _end_dot(scenario)
    scenario_raw = scenario.strip().rstrip(".!?")
    lens_pair = _split_top(lens, " vs ", 1)
    lens_short = (
        f"{_trim_parens(lens_pair[0])} 쪽과 {_trim_parens(lens_pair[1])} 쪽"
        if len(lens_pair) == 2
        else _trim_parens(lens)
    )
    case = f"사례: {scenario_short} 이 사례 위에서 두 관점을 대조한다. {_end_dot(lens)}"
    mistake = f"한쪽 원칙만 절대 규칙처럼 적용하고 반대쪽 비용을 계산하지 않으면 설계 판단이 아니다. {_end_dot(tradeoff)}"
    work = f"사례({scenario})를 두 관점으로 각각 설계·구현해 비교 노트 한 페이지 또는 리팩터링 커밋으로 남긴다. 핵심 기준: {_end_dot(rule)}"
    why = f"'{title}' 판단에서 {lens_short}의 변경 비용과 인지 부하를 대조해 채택·거절 근거를 남기기 위해서다. {_end_dot(tradeoff)}"
    check = f"'{title}' 기준을 이번 주 사례({scenario_raw}) 외의 다른 사례 하나에 적용해 {lens_short}의 득실과 채택·거절 근거를 한 줄씩 남긴다. 기준: {_end_dot(rule)}"
    return (title, lab2, lab3, rule, case, mistake, work, why, check)


def load(text):
    """Parse one or more phases from raw sw syllabus DSL text."""
    phases = []
    meta = None
    weeks = []
    seen = set()

    def flush():
        if meta is None:
            return
        name, start, end, fr, to, result = meta
        phases.append(phase(name, start, end, fr, to, result, resource_for(start), [S(t, j) for t, j in weeks]))

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if " :: " not in line:
            flush()
            name, start, end, fr, to, result = line.split("|")
            meta = (name, int(start), int(end), fr, to, result)
            weeks = []
            continue
        title, job = line.split(" :: ", 1)
        if title in seen:
            raise SystemExit(f"duplicate sw title {title}")
        seen.add(title)
        weeks.append((title, job))
    flush()
    return phases


def parse_phase(text):
    """Parse a standalone single-phase sw specification module."""
    phases = load(text)
    if len(phases) != 1:
        raise SystemExit(f"expected single sw phase, got {len(phases)}")
    return phases[0]

