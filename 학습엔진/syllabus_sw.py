# -*- coding: utf-8 -*-
"""Software design and project-record track. Practice is on code the learner already ships."""
from pathlib import Path

from syllabus_util import phase

RES = (
    "이미 유지하는 코드와 git. 언어 입문과 빌드 도구 수업은 없다. "
    "Clean Code와 A Philosophy of Software Design을 나란히 두고, 이긴 책을 정하지 않는다."
)


def S(title, job):
    rule = job
    case = "이미 아는 코드에서 이번 주 자리를 고른다. " + job
    mistake = "산출 없이 문장만 남기면 이 주는 끝나지 않는다. " + job
    work = "고른 자리에 적용해 커밋이나 한 페이지 노트를 남긴다. " + job
    why = "다음 변경자가 산출만 보고 이유를 말할 수 있어야 한다. " + job
    check = "다른 자리 하나에 같은 기준을 다시 적용하고 산출 제목을 남긴다. " + job
    return (title, "자리", "실패", rule, case, mistake, work, why, check)


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
