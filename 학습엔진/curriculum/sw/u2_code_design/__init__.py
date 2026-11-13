# -*- coding: utf-8 -*-
"""Major unit u2: 코드 품질·모듈 깊이와 설계 원칙 대조."""
from curriculum.sw.u2_code_design.p05_complexity_diagnosis import PHASE as _P05_COMPLEXITY_DIAGNOSIS
from curriculum.sw.u2_code_design.p06_deep_modules import PHASE as _P06_DEEP_MODULES
from curriculum.sw.u2_code_design.p07_small_functions_debate import PHASE as _P07_SMALL_FUNCTIONS_DEBATE
from curriculum.sw.u2_code_design.p08_two_designs_comparison import PHASE as _P08_TWO_DESIGNS_COMPARISON
from curriculum.sw.u2_code_design.p09_names_and_comments import PHASE as _P09_NAMES_AND_COMMENTS
from curriculum.sw.u2_code_design.p10_error_boundaries import PHASE as _P10_ERROR_BOUNDARIES
from curriculum.sw.u2_code_design.p11_testing_code_review import PHASE as _P11_TESTING_CODE_REVIEW
from curriculum.sw.u2_code_design.p12_principle_limits import PHASE as _P12_PRINCIPLE_LIMITS

UNIT_META = {
    "id": "u2",
    "title": "코드 품질·모듈 깊이와 설계 원칙 대조",
    "summary": "복잡도 진단, 깊은 모듈 vs 작은 함수, 이름·주석, 오류 정의, 테스트 전략과 원칙 거절 기준을 비교한다.",
}

PHASES = [_P05_COMPLEXITY_DIAGNOSIS, _P06_DEEP_MODULES, _P07_SMALL_FUNCTIONS_DEBATE, _P08_TWO_DESIGNS_COMPARISON, _P09_NAMES_AND_COMMENTS, _P10_ERROR_BOUNDARIES, _P11_TESTING_CODE_REVIEW, _P12_PRINCIPLE_LIMITS]
