# -*- coding: utf-8 -*-
"""Domain package `ma` organized by Major Unit -> Phase -> Week."""
from curriculum.common import make_units
from curriculum.ma.u1_algebra_logic import PHASES as _U1_PHASES, UNIT_META as _U1_META
from curriculum.ma.u2_calculus_disc import PHASES as _U2_PHASES, UNIT_META as _U2_META
from curriculum.ma.u3_analysis_linalg import PHASES as _U3_PHASES, UNIT_META as _U3_META
from curriculum.ma.u4_measure_prob import PHASES as _U4_PHASES, UNIT_META as _U4_META
from curriculum.ma.u5_functional_alg import PHASES as _U5_PHASES, UNIT_META as _U5_META

TRACK_ID = "ma"

UNITS, PHASES = make_units([
    (_U1_META, _U1_PHASES),
    (_U2_META, _U2_PHASES),
    (_U3_META, _U3_PHASES),
    (_U4_META, _U4_PHASES),
    (_U5_META, _U5_PHASES),
])
