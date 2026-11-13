# -*- coding: utf-8 -*-
"""Scoped hierarchical verification and curriculum browser CLI (Domain -> Unit -> Phase -> Week)."""
import argparse
import json
import re
import sys

from curriculum.builder import TRACK_IDS, build_track
from curriculum.common import BANNED_LABELS


def _norm_unit_arg(val):
    val = str(val).strip().lower()
    if val.isdigit():
        return f"u{int(val)}"
    return val


def _match_phase(phase, phase_idx, target):
    t = str(target).strip().lower()
    if re.fullmatch(r"p?\d+", t):
        num = int(t.lstrip("p"))
        return phase_idx + 1 == num
    return t in phase["name"].lower()


def _unit_for_phase(track, phase_idx):
    for u in track["units"]:
        if phase_idx in u["phases"]:
            return u
    return None


def validate_units_structure(track):
    """Verify Major Unit (`units`) partition covers all phases contiguously without gaps or overlaps."""
    tid = track["id"]
    errors = []
    units = track.get("units") or []
    phases = track.get("phases") or []
    if not units:
        errors.append(f"[{tid}] missing units metadata")
        return errors
    seen = []
    prev_end = 0
    for ui, u in enumerate(units):
        if not u.get("id") or not u.get("title"):
            errors.append(f"[{tid} unit#{ui+1}] missing id or title")
        p_indices = u.get("phases") or []
        if not p_indices:
            errors.append(f"[{tid} {u.get('id')}] empty phase list")
            continue
        for pi in p_indices:
            if not (0 <= pi < len(phases)):
                errors.append(f"[{tid} {u.get('id')}] invalid phase index {pi}")
        expected_indices = list(range(len(seen), len(seen) + len(p_indices)))
        if p_indices != expected_indices:
            errors.append(f"[{tid} {u.get('id')}] non-contiguous phase indices {p_indices} != {expected_indices}")
        seen.extend(p_indices)
        first_p = phases[p_indices[0]]
        last_p = phases[p_indices[-1]]
        if u.get("start") != prev_end + 1 or u.get("start") != first_p["start"] or u.get("end") != last_p["end"]:
            errors.append(f"[{tid} {u.get('id')}] range {u.get('start')}-{u.get('end')} mismatches phases {first_p['start']}-{last_p['end']}")
        prev_end = u.get("end", prev_end)
        if u.get("phaseNames") and u["phaseNames"] != [phases[pi]["name"] for pi in p_indices]:
            errors.append(f"[{tid} {u.get('id')}] phaseNames mismatch")
    if seen != list(range(len(phases))):
        errors.append(f"[{tid}] units cover phases {seen} != 0..{len(phases)-1}")
    return errors


def _audit_week(track_id, unit_id, phase_idx, week_no, week):
    """Return `(errors, warnings)` for a single Minor Unit (Week)."""
    errors = []
    warnings = []
    loc = f"[{track_id} {unit_id} p{phase_idx+1:02d} w{week_no:03d} '{week['title']}']"

    for key in ("title", "goal", "outcome", "resource", "check"):
        if not str(week.get(key, "")).strip():
            errors.append(f"{loc} empty {key}")

    ideas = week.get("ideas") or []
    if len(ideas) != 3:
        errors.append(f"{loc} expected 3 ideas, got {len(ideas)}")
    for idx, pair in enumerate(ideas):
        if len(pair) != 2 or not str(pair[0]).strip() or not str(pair[1]).strip():
            errors.append(f"{loc} invalid idea#{idx+1}")
        elif str(pair[0]).strip() in BANNED_LABELS:
            warnings.append(f"{loc} banned idea label '{pair[0]}'")

    days = week.get("days") or []
    if len(days) != 7:
        errors.append(f"{loc} expected 7 days, got {len(days)}")
    day_titles = [d.get("title", "") for d in days]
    if len(day_titles) != len(set(day_titles)):
        errors.append(f"{loc} duplicate day titles: {day_titles}")

    for di, d in enumerate(days, 1):
        blocks = d.get("blocks") or []
        if not blocks:
            errors.append(f"{loc} d{di} has no blocks")
            continue
        total = sum(b["m"] for b in blocks)
        if total != 60:
            errors.append(f"{loc} d{di} '{d.get('title')}' sums to {total} != 60")
        if len(blocks) > 1 and blocks[0]["m"] != 10:
            errors.append(f"{loc} d{di} first block {blocks[0]['m']} != 10")
        for bi, b in enumerate(blocks, 1):
            text = b.get("t", "")
            if not text.strip():
                errors.append(f"{loc} d{di} b{bi} empty text")
            if "  " in text or "…" in text or "通し" in text:
                errors.append(f"{loc} d{di} b{bi} formatting artifact")
            if "\\(" in text or "\\)" in text or "$$" in text:
                errors.append(f"{loc} d{di} b{bi} raw LaTeX delimiter")

    blob = json.dumps(week, ensure_ascii=False)
    if re.search(r"지\s*않지\s*않", blob):
        errors.append(f"{loc} double negative")

    # Advisory content checks (surfaced clearly in per-unit/per-phase audits)
    if week["title"].count("(") != week["title"].count(")"):
        warnings.append(f"{loc} unbalanced parens in title")
    for field_name in ("goal", "outcome", "check"):
        val = week.get(field_name, "")
        if "  " in val:
            warnings.append(f"{loc} double space in {field_name}")
        if val.count("(") != val.count(")"):
            warnings.append(f"{loc} unbalanced parens in {field_name}")
    if re.search(r"(?:^|\s)(\S+)\s+\1(?=\s|$|[.,!?])", week.get("outcome", "")):
        warnings.append(f"{loc} repeated consecutive word in outcome")

    return errors, warnings


def verify_scope(track_ids=None, unit_filter=None, phase_filter=None, week_filter=None):
    """Run structural + advisory verification scoped by domain/unit/phase/week."""
    selected_tracks = track_ids or list(TRACK_IDS)
    all_errors = []
    all_warnings = []
    stats = {"tracks": 0, "units": 0, "phases": 0, "weeks": 0}

    norm_unit = _norm_unit_arg(unit_filter) if unit_filter else None

    for tid in selected_tracks:
        track = build_track(tid)
        stats["tracks"] += 1
        all_errors.extend(validate_units_structure(track))

        phases = track["phases"]
        weeks = track["weeks"]
        for a, b in zip(phases, phases[1:]):
            if a["end"] + 1 != b["start"]:
                all_errors.append(f"[{tid}] phase gap {a['name']}({a['end']}) -> {b['name']}({b['start']})")
            if a["to"] != b["from"]:
                all_errors.append(f"[{tid}] phase bridge mismatch {a['name']}({a['to']}) -> {b['name']}({b['from']})")

        matched_units = set()
        for pi, p in enumerate(phases):
            u = _unit_for_phase(track, pi)
            uid = u["id"] if u else "?"
            if norm_unit and uid != norm_unit:
                continue
            if phase_filter and not _match_phase(p, pi, phase_filter):
                continue
            if week_filter and not (p["start"] <= week_filter <= p["end"]):
                continue
            matched_units.add(uid)
            stats["phases"] += 1
            expected = p["end"] - p["start"] + 1
            actual = len(weeks[p["start"] - 1 : p["end"]])
            if actual != expected:
                all_errors.append(f"[{tid} {uid} p{pi+1:02d}] week slice {actual} != {expected}")
            for wi in range(p["start"], p["end"] + 1):
                if week_filter and wi != week_filter:
                    continue
                stats["weeks"] += 1
                errs, warns = _audit_week(tid, uid, pi, wi, weeks[wi - 1])
                all_errors.extend(errs)
                all_warnings.extend(warns)
        stats["units"] += len(matched_units)

    return stats, all_errors, all_warnings


def print_tree(track_ids=None, unit_filter=None, phase_filter=None):
    """Print hierarchical 도메인 -> 대단원 -> 중단원(주차) outline."""
    norm_unit = _norm_unit_arg(unit_filter) if unit_filter else None
    for tid in (track_ids or TRACK_IDS):
        track = build_track(tid)
        print(f"=== [{tid}] {track['name']} ({len(track['units'])} 대단원 / {len(track['phases'])} 중단원 / {len(track['weeks'])}주) ===")
        for u in track["units"]:
            if norm_unit and u["id"] != norm_unit:
                continue
            matching_pis = [
                pi for pi in u["phases"]
                if not phase_filter or _match_phase(track["phases"][pi], pi, phase_filter)
            ]
            if phase_filter and not matching_pis:
                continue
            print(f"  {u['id']}: {u['title']} ({u['start']}–{u['end']}주, {len(u['phases'])}개 중단원)")
            for pi in matching_pis:
                p = track["phases"][pi]
                w_count = p["end"] - p["start"] + 1
                print(f"    - P{pi+1:02d} {p['name']} ({p['start']}–{p['end']}주, {w_count}w) [{p['from']} → {p['to']}]")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify curriculum by Domain / Major Unit / Phase / Week.")
    parser.add_argument("--track", choices=TRACK_IDS, nargs="+", help="Domain(s) to inspect/verify")
    parser.add_argument("--unit", help="Major unit filter (e.g. u1, u3, or 3)")
    parser.add_argument("--phase", help="Middle phase filter (e.g. p14, 14, or substring of phase name)")
    parser.add_argument("--week", type=int, help="Specific 1-based week number")
    parser.add_argument("--tree", action="store_true", help="Print curriculum hierarchy tree")
    parser.add_argument("--strict", action="store_true", help="Fail with exit code 1 if advisory warnings exist")
    args = parser.parse_args(argv)

    if args.tree:
        print_tree(args.track, args.unit, args.phase)

    stats, errors, warnings = verify_scope(args.track, args.unit, args.phase, args.week)
    scope = (
        f"tracks={args.track or list(TRACK_IDS)} "
        f"unit={args.unit or '*'} phase={args.phase or '*'} week={args.week or '*'}"
    )
    print(
        f"[verify] {scope} -> checked {stats['tracks']} tracks, {stats['units']} units, "
        f"{stats['phases']} phases, {stats['weeks']} weeks | "
        f"errors={len(errors)}, warnings={len(warnings)}"
    )
    for err in errors:
        print("ERROR:", err)
    for warn in warnings:
        print("WARN:", warn)

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
