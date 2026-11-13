# -*- coding: utf-8 -*-
"""Major unit u4: 정확성 증명과 네트워크 유량·상환 분석."""
from curriculum.al.u4_proof_flow.p13_loop_invariants import PHASE as _P13_LOOP_INVARIANTS
from curriculum.al.u4_proof_flow.p14_graph_proofs import PHASE as _P14_GRAPH_PROOFS
from curriculum.al.u4_proof_flow.p15_flow_impl import PHASE as _P15_FLOW_IMPL
from curriculum.al.u4_proof_flow.p16_flow_proofs import PHASE as _P16_FLOW_PROOFS
from curriculum.al.u4_proof_flow.p17_string_proofs import PHASE as _P17_STRING_PROOFS
from curriculum.al.u4_proof_flow.p18_amortized_lower_bounds import PHASE as _P18_AMORTIZED_LOWER_BOUNDS

UNIT_META = {
    "id": "u4",
    "title": "정확성 증명과 네트워크 유량·상환 분석",
    "summary": "루프 불변식, 그래프·최대유량·문자열 정확성 증명과 분할상환·하한 분석을 수행한다.",
}

PHASES = [_P13_LOOP_INVARIANTS, _P14_GRAPH_PROOFS, _P15_FLOW_IMPL, _P16_FLOW_PROOFS, _P17_STRING_PROOFS, _P18_AMORTIZED_LOWER_BOUNDS]
