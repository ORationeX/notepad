# -*- coding: utf-8 -*-
"""Major unit u2: 그래프·그리디와 동적 계획."""
from curriculum.al.u2_graph_dp.p06_graph_traversal import PHASE as _P06_GRAPH_TRAVERSAL
from curriculum.al.u2_graph_dp.p07_greedy_shortest_path import PHASE as _P07_GREEDY_SHORTEST_PATH
from curriculum.al.u2_graph_dp.p08_union_find_mst import PHASE as _P08_UNION_FIND_MST
from curriculum.al.u2_graph_dp.p09_dynamic_programming import PHASE as _P09_DYNAMIC_PROGRAMMING

UNIT_META = {
    "id": "u2",
    "title": "그래프·그리디와 동적 계획",
    "summary": "그래프 순회, 그리디 반례와 최단 경로, 서로소 집합·신장 트리, 동적 계획 상태를 다룬다.",
}

PHASES = [_P06_GRAPH_TRAVERSAL, _P07_GREEDY_SHORTEST_PATH, _P08_UNION_FIND_MST, _P09_DYNAMIC_PROGRAMMING]
