# -*- coding: utf-8 -*-
"""Domain package `al` organized by Major Unit -> Phase -> Week."""
from curriculum.common import make_units
from curriculum.al.u1_basics import PHASES as _U1_PHASES, UNIT_META as _U1_META
from curriculum.al.u2_graph_dp import PHASES as _U2_PHASES, UNIT_META as _U2_META
from curriculum.al.u3_advanced_ds import PHASES as _U3_PHASES, UNIT_META as _U3_META
from curriculum.al.u4_proof_flow import PHASES as _U4_PHASES, UNIT_META as _U4_META
from curriculum.al.u5_complexity import PHASES as _U5_PHASES, UNIT_META as _U5_META
from curriculum.al.u6_notes import PHASES as _U6_PHASES, UNIT_META as _U6_META

TRACK_ID = "al"

UNITS, PHASES = make_units([
    (_U1_META, _U1_PHASES),
    (_U2_META, _U2_PHASES),
    (_U3_META, _U3_PHASES),
    (_U4_META, _U4_PHASES),
    (_U5_META, _U5_PHASES),
    (_U6_META, _U6_PHASES),
])
