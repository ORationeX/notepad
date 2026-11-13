# -*- coding: utf-8 -*-
"""Major unit u2: 미적분 계산 감각과 이산 세기."""
from curriculum.ma.u2_calculus_disc.p06_diff_calculus import PHASE as _P06_DIFF_CALCULUS
from curriculum.ma.u2_calculus_disc.p07_integral_multivar import PHASE as _P07_INTEGRAL_MULTIVAR
from curriculum.ma.u2_calculus_disc.p08_counting_recurrence import PHASE as _P08_COUNTING_RECURRENCE

UNIT_META = {
    "id": "u2",
    "title": "미적분 계산 감각과 이산 세기",
    "summary": "미분·적분·다변수 계산 감각을 익히고 경우의 수, 기댓값, 빅오와 점화식을 연결한다.",
}

PHASES = [_P06_DIFF_CALCULUS, _P07_INTEGRAL_MULTIVAR, _P08_COUNTING_RECURRENCE]
