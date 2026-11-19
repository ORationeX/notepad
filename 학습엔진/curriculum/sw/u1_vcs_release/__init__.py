# -*- coding: utf-8 -*-
"""Major unit u1: 변경 응집도·이력과 릴리스 경계."""
from curriculum.sw.u1_vcs_release.p01_change_cohesion import PHASE as _P01_CHANGE_COHESION
from curriculum.sw.u1_vcs_release.p02_branch_integration import PHASE as _P02_BRANCH_INTEGRATION
from curriculum.sw.u1_vcs_release.p03_history_compatibility import PHASE as _P03_HISTORY_COMPATIBILITY
from curriculum.sw.u1_vcs_release.p04_regression_release import PHASE as _P04_REGRESSION_RELEASE

UNIT_META = {
    "id": "u1",
    "title": "형상·명세·검증과 배포 공학",
    "summary": "변경 응집도, 브랜치·호환성, MIT 6.031 명세·불변식(SWEBOK KA 1), 테스트 공학·CI/CD·DORA 배포 경계(KA 5·8)를 대조한다.",
}

PHASES = [_P01_CHANGE_COHESION, _P02_BRANCH_INTEGRATION, _P03_HISTORY_COMPATIBILITY, _P04_REGRESSION_RELEASE]
