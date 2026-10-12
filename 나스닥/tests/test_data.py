"""캐시는 열어 둘 때 그대로 쓰고, 갱신 때는 최근 3영업일만 다시 받는다."""

import numpy as np
import pandas as pd

from src import data


def _series(values: list[float]) -> pd.Series:
    index = pd.bdate_range("2024-01-02", periods=len(values))
    return pd.Series(values, index=index, name="close")


def test_open_reads_the_cache_without_downloading(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "CACHE_DIR", tmp_path)
    cached = _series([1.0, 2.0, 3.0, 4.0, 5.0])
    data._write_cache("ixic", cached)

    def fail_download(*_args, **_kwargs):
        raise AssertionError("캐시가 있으면 받지 않습니다.")

    monkeypatch.setattr(data, "_download", fail_download)
    loaded = data.load_series("ixic", refresh=False)
    pd.testing.assert_series_equal(loaded, cached, check_names=False)


def test_refresh_replaces_only_the_last_three_sessions(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "CACHE_DIR", tmp_path)
    cached = _series([float(value) for value in range(10)])
    data._write_cache("ixic", cached)
    seen = {}

    def fake_download(_ticker, start=None):
        seen["start"] = pd.Timestamp(start)
        fresh_index = pd.bdate_range(cached.index[-3], periods=4)
        return pd.Series([100.0, 101.0, 102.0, 103.0], index=fresh_index, name="close")

    monkeypatch.setattr(data, "_download", fake_download)
    loaded = data.load_series("ixic", refresh=True)

    assert seen["start"] == cached.index[-3]
    assert loaded.iloc[:7].to_numpy().tolist() == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    assert loaded.iloc[-4:].to_numpy().tolist() == [100.0, 101.0, 102.0, 103.0]
    assert len(loaded) == 11
    stored = data._read_cache("ixic")
    pd.testing.assert_series_equal(stored, loaded, check_names=False)


def test_refresh_keeps_the_cache_when_the_latest_download_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "CACHE_DIR", tmp_path)
    cached = _series([1.0, 2.0, 3.0, 4.0, 5.0])
    data._write_cache("gspc", cached)
    monkeypatch.setattr(data, "_download", lambda *_args, **_kwargs: _series([]).iloc[0:0])

    try:
        data.load_series("gspc", refresh=True)
    except ValueError:
        pass
    else:
        raise AssertionError("빈 응답은 캐시를 바꾸면 안 됩니다.")

    stored = data._read_cache("gspc")
    pd.testing.assert_series_equal(stored, cached, check_names=False)
