# -*- coding: utf-8 -*-
"""Major unit u5: 선형계획·확률·계산복잡도와 근사."""
from curriculum.al.u5_complexity.p19_linear_programming import PHASE as _P19_LINEAR_PROGRAMMING
from curriculum.al.u5_complexity.p20_tail_bounds import PHASE as _P20_TAIL_BOUNDS
from curriculum.al.u5_complexity.p21_randomized_algos import PHASE as _P21_RANDOMIZED_ALGOS
from curriculum.al.u5_complexity.p22_p_and_np import PHASE as _P22_P_AND_NP
from curriculum.al.u5_complexity.p23_reductions import PHASE as _P23_REDUCTIONS
from curriculum.al.u5_complexity.p24_approximation import PHASE as _P24_APPROXIMATION
from curriculum.al.u5_complexity.p25_primal_dual import PHASE as _P25_PRIMAL_DUAL

UNIT_META = {
    "id": "u5",
    "title": "선형계획·확률·계산복잡도와 근사",
    "summary": "선형계획 쌍대성, 꼬리 부등식, 무작위 알고리즘, P/NP 환원, 근사 비율과 원-쌍대를 다룬다.",
}

PHASES = [_P19_LINEAR_PROGRAMMING, _P20_TAIL_BOUNDS, _P21_RANDOMIZED_ALGOS, _P22_P_AND_NP, _P23_REDUCTIONS, _P24_APPROXIMATION, _P25_PRIMAL_DUAL]
