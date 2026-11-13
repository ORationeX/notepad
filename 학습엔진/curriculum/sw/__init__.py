# -*- coding: utf-8 -*-
"""Domain package `sw` organized by Major Unit -> Phase -> Week."""
from curriculum.common import make_units
from curriculum.sw.u1_vcs_release import PHASES as _U1_PHASES, UNIT_META as _U1_META
from curriculum.sw.u2_code_design import PHASES as _U2_PHASES, UNIT_META as _U2_META
from curriculum.sw.u3_modularity import PHASES as _U3_PHASES, UNIT_META as _U3_META
from curriculum.sw.u4_distributed import PHASES as _U4_PHASES, UNIT_META as _U4_META
from curriculum.sw.u5_handbook import PHASES as _U5_PHASES, UNIT_META as _U5_META

TRACK_ID = "sw"

UNITS, PHASES = make_units([
    (_U1_META, _U1_PHASES),
    (_U2_META, _U2_PHASES),
    (_U3_META, _U3_PHASES),
    (_U4_META, _U4_PHASES),
    (_U5_META, _U5_PHASES),
])
