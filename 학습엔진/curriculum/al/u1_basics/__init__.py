# -*- coding: utf-8 -*-
"""Major unit u1: 기초 탐색·정렬과 기본 자료구조."""
from curriculum.al.u1_basics.p01_binary_search import PHASE as _P01_BINARY_SEARCH
from curriculum.al.u1_basics.p02_sorting import PHASE as _P02_SORTING
from curriculum.al.u1_basics.p03_stack_queue import PHASE as _P03_STACK_QUEUE
from curriculum.al.u1_basics.p04_basic_trees import PHASE as _P04_BASIC_TREES
from curriculum.al.u1_basics.p05_hash_heap import PHASE as _P05_HASH_HEAP

UNIT_META = {
    "id": "u1",
    "title": "기초 탐색·정렬과 기본 자료구조",
    "summary": "이분 탐색, 기초 정렬, 스택·큐, 단순 트리와 해시·힙까지 손 추적 후 구현한다.",
}

PHASES = [_P01_BINARY_SEARCH, _P02_SORTING, _P03_STACK_QUEUE, _P04_BASIC_TREES, _P05_HASH_HEAP]
