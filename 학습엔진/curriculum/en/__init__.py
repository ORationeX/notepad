# -*- coding: utf-8 -*-
"""Domain package `en` organized by Major Unit -> Phase -> Week."""
from curriculum.common import make_units
from curriculum.en.u1_foundation import PHASES as _U1_PHASES, UNIT_META as _U1_META
from curriculum.en.u2_business import PHASES as _U2_PHASES, UNIT_META as _U2_META
from curriculum.en.u3_contract import PHASES as _U3_PHASES, UNIT_META as _U3_META
from curriculum.en.u4_prose import PHASES as _U4_PHASES, UNIT_META as _U4_META
from curriculum.en.u5_portfolio import PHASES as _U5_PHASES, UNIT_META as _U5_META

TRACK_ID = "en"

UNITS, PHASES = make_units([
    (_U1_META, _U1_PHASES),
    (_U2_META, _U2_PHASES),
    (_U3_META, _U3_PHASES),
    (_U4_META, _U4_PHASES),
    (_U5_META, _U5_PHASES),
])
