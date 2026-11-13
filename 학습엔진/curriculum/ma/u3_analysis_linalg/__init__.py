# -*- coding: utf-8 -*-
"""Major unit u3: 실해석학 기초와 선형대수·거리공간."""
from curriculum.ma.u3_analysis_linalg.p09_real_completeness import PHASE as _P09_REAL_COMPLETENESS
from curriculum.ma.u3_analysis_linalg.p10_continuity_diff_proof import PHASE as _P10_CONTINUITY_DIFF_PROOF
from curriculum.ma.u3_analysis_linalg.p11_riemann_series import PHASE as _P11_RIEMANN_SERIES
from curriculum.ma.u3_analysis_linalg.p12_vector_spaces import PHASE as _P12_VECTOR_SPACES
from curriculum.ma.u3_analysis_linalg.p13_metric_compactness import PHASE as _P13_METRIC_COMPACTNESS

UNIT_META = {
    "id": "u3",
    "title": "실해석학 기초와 선형대수·거리공간",
    "summary": "실수의 완비성, 엡실론-델타 연속·미분·적분 증명, 벡터공간과 거리공간 컴팩트를 증명·스케치한다.",
}

PHASES = [_P09_REAL_COMPLETENESS, _P10_CONTINUITY_DIFF_PROOF, _P11_RIEMANN_SERIES, _P12_VECTOR_SPACES, _P13_METRIC_COMPACTNESS]
