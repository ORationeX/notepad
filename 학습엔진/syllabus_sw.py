# -*- coding: utf-8 -*-
"""Software design & architecture trade-off track."""
from pathlib import Path

from syllabus_util import phase

RES = (
    "Clean Code(로버트 마틴), A Philosophy of Software Design(존 아우스터하우트), "
    "Refactoring(마틴 파울러), Designing Data-Intensive Applications(마틴 클레프만). "
    "어느 한 책의 규칙을 정답으로 외우지 않고, 상반된 원칙이 각각 언제 맞고 언제 깨지는지 비교한다."
)


def S(title, job):
    parts = [p.strip() for p in job.split(" / ") if p.strip()]
    if len(parts) == 3:
        rule, lens, tradeoff = parts
    else:
        rule = job
        lens = "작게 나누어 흐름을 드러내는 관점과, 결정을 모듈 안에 숨겨 인터페이스를 단순하게 두는 관점을 나란히 놓고 비교한다."
        tradeoff = "이 선택으로 줄어드는 비용(읽기 시간, 수정할 파일 수, 누수되는 지식)과 늘어나는 비용을 함께 적는다."
    case = f"실제 코드나 대표 설계 사례에서 이번 주 주제가 드러나는 자리를 고른다. {lens}"
    mistake = f"한쪽 원칙만 절대 규칙처럼 적용하고 반대쪽 비용을 적지 않으면 설계 판단이 아니다. {tradeoff}"
    work = f"같은 요구사항을 두 관점으로 비교해 설계 노트 한 페이지 또는 리팩터링 커밋으로 남긴다. {rule}"
    why = f"나중에 새로운 시스템을 설계할 때 언제 이 규칙을 따르고 언제 거절할지 판단 근거를 남기기 위해서다. {tradeoff}"
    check = f"다른 사례 하나에 같은 비교 기준을 적용해 선택과 거절의 근거를 한 줄씩 남긴다. {rule}"
    return (title, "대비 관점", "트레이드오프", rule, case, mistake, work, why, check)


def load(text):
    phases = []
    meta = None
    weeks = []
    seen = set()

    def flush():
        if meta is None:
            return
        name, start, end, fr, to, result = meta
        phases.append(phase(name, start, end, fr, to, result, RES, [S(t, j) for t, j in weeks]))

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


def _body():
    here = Path(__file__).parent
    return "\n".join(
        (here / name).read_text(encoding="utf-8")
        for name in ("syllabus_sw_early.txt", "syllabus_sw_late.txt")
    )


PHASES = load(_body())
