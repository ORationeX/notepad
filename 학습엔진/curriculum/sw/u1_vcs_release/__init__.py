# -*- coding: utf-8 -*-
"""Major unit u1: 변경 응집도·이력과 릴리스 경계."""
from curriculum.sw.u1_vcs_release.p01_change_cohesion import PHASE as _P01_CHANGE_COHESION
from curriculum.sw.u1_vcs_release.p02_branch_integration import PHASE as _P02_BRANCH_INTEGRATION
from curriculum.sw.u1_vcs_release.p03_history_compatibility import PHASE as _P03_HISTORY_COMPATIBILITY
from curriculum.sw.u1_vcs_release.p04_regression_release import PHASE as _P04_REGRESSION_RELEASE

UNIT_META = {
    "id": "u1",
    "title": "변경 응집도·이력과 릴리스 경계",
    "summary": "커밋 응집도, 브랜치 통합 전략, 호환성·변경 이력 관리, 회귀 이분 탐색과 릴리스 경계를 대조한다.",
}

PHASES = [_P01_CHANGE_COHESION, _P02_BRANCH_INTEGRATION, _P03_HISTORY_COMPATIBILITY, _P04_REGRESSION_RELEASE]
