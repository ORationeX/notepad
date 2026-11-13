# -*- coding: utf-8 -*-
"""Shared curriculum primitives, unit/phase/week helpers, and Korean particle utilities."""
import re

BANNED_LABELS = {"목표", "확인", "범위"}


def _has_batchim(word):
    w = str(word or "").strip().rstrip("'\".,!? ")
    if not w:
        return True
    matched = re.match(r"^(.*\S)\s*\(([^()]+)\)$", w)
    if matched:
        outer, inner = matched.group(1), matched.group(2)
        if re.search(r"[\uAC00-\uD7A3]", inner):
            return _has_batchim(inner)
        return _has_batchim(outer)
    last = w[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        return (code - 0xAC00) % 28 != 0
    if last.isdigit():
        return last in "013678"
    if re.search(r"(?:^|[^A-Za-z])[A-Za-z]$", w) or re.search(r"[A-Z]{2,}$", w):
        return last.upper() in "LMNR"
    return last.lower() in "lmn"


def particle_eul(word):
    """을 after a batchim, 를 after a vowel."""
    return "을" if _has_batchim(word) else "를"


def particle_i(word):
    """이 after a batchim, 가 after a vowel."""
    return "이" if _has_batchim(word) else "가"


def focus_line(text, limit=200):
    """First sentence of a week's own material, so a 10-minute cue names that material."""
    text = " ".join(str(text).split())
    if not text:
        return ""
    matched = re.search(r".+?다\.", text)
    line = matched.group(0).strip() if matched else text
    if len(line) <= limit:
        return line
    sentence = re.search(r"^.{20," + str(limit) + r"}?(?:다\.|[.!?](?=\s|$))", line)
    if sentence:
        return sentence.group(0).strip()
    cut = line[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return (cut or line[:limit]).strip()


def with_focus(lead, text):
    line = focus_line(text)
    lead = str(lead).rstrip()
    if not line:
        return lead
    return lead + " " + line


def day_title(base, suffix):
    """Append a day role cleanly without dropping roles or colliding with '점검'."""
    base = str(base).strip()
    suffix = str(suffix).strip()
    if not suffix:
        return base
    if suffix == "점검" and (base == suffix or base.endswith(" " + suffix) or base.endswith("점검")):
        return base
    if base == suffix or base.endswith(" " + suffix):
        return f"{base} · {suffix}"
    return f"{base} {suffix}"


def day(title, blocks):
    total = sum(m for m, _ in blocks)
    if total != 60:
        raise SystemExit(f"{title} sums to {total}")
    if blocks[0][0] != 10:
        raise SystemExit(f"{title} review block is {blocks[0][0]}")
    return {"title": title, "blocks": [{"m": m, "t": t} for m, t in blocks]}


def phase(name, start, end, fr, to, result, resource, weeks, mode=None):
    if len(weeks) != end - start + 1:
        raise SystemExit(f"{name}: {len(weeks)} != {end - start + 1}")
    out = {
        "name": name, "start": start, "end": end, "from": fr, "to": to,
        "result": result, "resource": resource, "weeks": weeks,
    }
    if mode is not None:
        out["mode"] = mode
    return out


def A(title, lab2, lab3, what, example, mistake, why, mode=None):
    drill = example + " 숫자나 입력만 바꾼 경우를 두 개 더 같은 절차로 처리한다."
    check = "노트를 덮고 다음을 다시 한다. " + example + " 이어서 다음 실수가 어느 줄을 깨는지 말한다. " + mistake
    if mode:
        return (title, lab2, lab3, what, example, mistake, drill, why, check, mode)
    return (title, lab2, lab3, what, example, mistake, drill, why, check)


def E(title, lab2, lab3, model, pattern, trap, speak, write, mode=None):
    check = "대본 없이 60초 이상 말하거나 고친 초고를 남기고, 수정한 문장 네 개를 기록한다. 기준: " + model
    if mode:
        return (title, lab2, lab3, model, pattern, trap, speak, write, check, mode)
    return (title, lab2, lab3, model, pattern, trap, speak, write, check)


def make_units(unit_specs):
    """Assemble contiguous Major Unit metadata and flattened phase list for a domain."""
    units = []
    phases = []
    for unit_meta, unit_phases in unit_specs:
        if not unit_phases:
            raise SystemExit(f"empty unit: {unit_meta.get('id')}")
        start_idx = len(phases)
        phases.extend(unit_phases)
        end_idx = len(phases)
        indices = list(range(start_idx, end_idx))
        units.append({
            "id": unit_meta["id"],
            "title": unit_meta["title"],
            "summary": unit_meta["summary"],
            "start": unit_phases[0]["start"],
            "end": unit_phases[-1]["end"],
            "phases": indices,
            "phaseNames": [p["name"] for p in unit_phases],
        })
    return units, phases

