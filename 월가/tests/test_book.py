from __future__ import annotations

from src.book import decide_book
from src.score import Snapshot, compute_signal_frame, latest_row
from tests.panels import make_panel


def _snap(scenario: str) -> Snapshot:
    panel = make_panel(scenario)
    frame = compute_signal_frame(panel)
    row = latest_row(frame)
    return Snapshot(
        asof=row.name,
        regime=str(row["regime"]),
        stance=str(row["stance"]),
        score=float(row["score"]),
        daily_score=float(row["score"]),
        daily_stance=str(row["stance"]),
        overlay_note=None,
        features=row,
    )


def test_scare_book_prefers_cash_and_avoids_growth():
    book = decide_book(_snap("scare"))
    enlarge = {r.ticker for r in book.enlarge}
    avoid_reduce = {r.ticker for r in book.avoid + book.reduce}
    assert "BIL" in enlarge or "TLT" in enlarge
    assert "QQQ" in avoid_reduce or "IWM" in avoid_reduce


def test_bnign_book_buys_growth_or_duration():
    book = decide_book(_snap("bnign"))
    enlarge = {r.ticker for r in book.enlarge}
    assert enlarge & {"QQQ", "XLK", "TLT", "GLD", "SPY"}
    assert "BIL" not in enlarge


def test_book_caps_lists():
    book = decide_book(_snap("landing"))
    assert len(book.enlarge) <= 3
    assert len(book.avoid) + len(book.reduce) <= 3
