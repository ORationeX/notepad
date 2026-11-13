# -*- coding: utf-8 -*-
"""Per-domain 7-day plan builders and week-thickening helpers."""
from curriculum.days.al import algo_days
from curriculum.days.en import (
    english_block_needs_fill,
    english_days,
    english_expand_minutes,
    thicken_english_check,
    thicken_english_week,
)
from curriculum.days.ma import math_days, thicken_math_blank, thicken_math_check
from curriculum.days.sw import sw_days

__all__ = [
    "algo_days",
    "english_block_needs_fill",
    "english_days",
    "english_expand_minutes",
    "math_days",
    "sw_days",
    "thicken_english_check",
    "thicken_english_week",
    "thicken_math_blank",
    "thicken_math_check",
]

