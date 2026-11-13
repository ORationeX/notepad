# -*- coding: utf-8 -*-
"""Major unit u1: 기초 연산·대수와 논리·기하 입문."""
from curriculum.ma.u1_algebra_logic.p01_numbers_ops import PHASE as _P01_NUMBERS_OPS
from curriculum.ma.u1_algebra_logic.p02_equations_functions import PHASE as _P02_EQUATIONS_FUNCTIONS
from curriculum.ma.u1_algebra_logic.p03_quadratics_logic import PHASE as _P03_QUADRATICS_LOGIC
from curriculum.ma.u1_algebra_logic.p04_sequences_induction import PHASE as _P04_SEQUENCES_INDUCTION
from curriculum.ma.u1_algebra_logic.p05_trig_complex import PHASE as _P05_TRIG_COMPLEX

UNIT_META = {
    "id": "u1",
    "title": "기초 연산·대수와 논리·기하 입문",
    "summary": "수와 연산, 일차·이차식과 함수, 귀납 증명, 삼각비와 복소수 직관까지 1~5단계를 다진다.",
}

PHASES = [_P01_NUMBERS_OPS, _P02_EQUATIONS_FUNCTIONS, _P03_QUADRATICS_LOGIC, _P04_SEQUENCES_INDUCTION, _P05_TRIG_COMPLEX]
