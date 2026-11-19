# -*- coding: utf-8 -*-
"""Major unit u3: 행동 분리·패턴과 의존성·상태·보안 경계."""
from curriculum.sw.u3_modularity.p13_varying_behavior import PHASE as _P12_VARYING_BEHAVIOR
from curriculum.sw.u3_modularity.p14_object_wiring import PHASE as _P13_OBJECT_WIRING
from curriculum.sw.u3_modularity.p15_calls_vs_events import PHASE as _P14_CALLS_VS_EVENTS
from curriculum.sw.u3_modularity.p16_pattern_adoption import PHASE as _P15_PATTERN_ADOPTION
from curriculum.sw.u3_modularity.p17_information_hiding import PHASE as _P16_INFORMATION_HIDING
from curriculum.sw.u3_modularity.p18_dependency_direction import PHASE as _P17_DEPENDENCY_DIRECTION
from curriculum.sw.u3_modularity.p19_state_consistency import PHASE as _P18_STATE_CONSISTENCY
from curriculum.sw.u3_modularity.p19b_security_boundaries import PHASE as _P19_SECURITY_BOUNDARIES
from curriculum.sw.u3_modularity.p20_design_notes import PHASE as _P20_DESIGN_NOTES

UNIT_META = {
    "id": "u3",
    "title": "행동 분리·패턴과 의존성·상태·보안 경계",
    "summary": "변하는 행동, 객체 조립, 이벤트, 패턴 채택·제거, 정보 은닉, 의존 방향, 상태 일관성, SWEBOK v4 보안 경계와 ATAM 설계 노트를 다룬다.",
}

PHASES = [_P12_VARYING_BEHAVIOR, _P13_OBJECT_WIRING, _P14_CALLS_VS_EVENTS, _P15_PATTERN_ADOPTION, _P16_INFORMATION_HIDING, _P17_DEPENDENCY_DIRECTION, _P18_STATE_CONSISTENCY, _P19_SECURITY_BOUNDARIES, _P20_DESIGN_NOTES]
