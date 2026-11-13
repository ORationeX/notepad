# -*- coding: utf-8 -*-
"""Major unit u5: 함수해석학과 대수 구조."""
from curriculum.ma.u5_functional_alg.p17_norms_banach import PHASE as _P17_NORMS_BANACH
from curriculum.ma.u5_functional_alg.p18_hilbert_spaces import PHASE as _P18_HILBERT_SPACES
from curriculum.ma.u5_functional_alg.p19_bounded_operators import PHASE as _P19_BOUNDED_OPERATORS
from curriculum.ma.u5_functional_alg.p20_algebraic_structures import PHASE as _P20_ALGEBRAIC_STRUCTURES

UNIT_META = {
    "id": "u5",
    "title": "함수해석학과 대수 구조",
    "summary": "노름·바나흐 공간, 힐베르트 공간과 유계 작용소 스펙트럼을 정리하고 군·환·체 구조를 스케치한다.",
}

PHASES = [_P17_NORMS_BANACH, _P18_HILBERT_SPACES, _P19_BOUNDED_OPERATORS, _P20_ALGEBRAIC_STRUCTURES]
