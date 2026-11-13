# -*- coding: utf-8 -*-
"""Major unit u3: 행동 분리·패턴과 의존성·상태 경계."""
from curriculum.sw.u3_modularity.p13_varying_behavior import PHASE as _P13_VARYING_BEHAVIOR
from curriculum.sw.u3_modularity.p14_object_wiring import PHASE as _P14_OBJECT_WIRING
from curriculum.sw.u3_modularity.p15_calls_vs_events import PHASE as _P15_CALLS_VS_EVENTS
from curriculum.sw.u3_modularity.p16_pattern_adoption import PHASE as _P16_PATTERN_ADOPTION
from curriculum.sw.u3_modularity.p17_information_hiding import PHASE as _P17_INFORMATION_HIDING
from curriculum.sw.u3_modularity.p18_dependency_direction import PHASE as _P18_DEPENDENCY_DIRECTION
from curriculum.sw.u3_modularity.p19_state_consistency import PHASE as _P19_STATE_CONSISTENCY
from curriculum.sw.u3_modularity.p20_design_notes import PHASE as _P20_DESIGN_NOTES

UNIT_META = {
    "id": "u3",
    "title": "행동 분리·패턴과 의존성·상태 경계",
    "summary": "변하는 행동, 객체 조립, 이벤트 결합, 디자인 패턴 채택·제거, 정보 은닉, 의존성 방향과 상태 일관성을 다룬다.",
}

PHASES = [_P13_VARYING_BEHAVIOR, _P14_OBJECT_WIRING, _P15_CALLS_VS_EVENTS, _P16_PATTERN_ADOPTION, _P17_INFORMATION_HIDING, _P18_DEPENDENCY_DIRECTION, _P19_STATE_CONSISTENCY, _P20_DESIGN_NOTES]
