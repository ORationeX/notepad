# -*- coding: utf-8 -*-
"""Phase 19: 단락 설계와 전개 (weeks 235–247)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("단락 설계와 전개")

PHASE = phase("단락 설계와 전개", 235, 247, "문장 호흡", "단락 전개", "주제-근거-전환-결론을 넘어 비교·인과·문제해결·분류 등 7가지 단락 아키텍처를 자유자재로 구사한다.", STYLE, [
W("단락의 단일 약속(Unity)", "단일", "약속", "Open with a Point sentence and test whether every subsequent sentence directly develops it.", "단락의 핵심 문장(Point)은 단락 처음이나 도입 직후에 두고, 나머지 모든 문장이 그 점 하나만 증명하게 만든다.", "한 단락 안에 문제 설명과 해결책과 예외 일화까지 세 가지 일을 다 넣지 않는다."),
W("Point-First vs Point-Last", "배치", "전개", "Use Point-First for business clarity, and Point-Last only when building up to a counterintuitive turn.", "결론 선행형(Point-First) 단락과 증거를 쌓은 뒤 마지막에 결론을 터뜨리는 귀납형(Point-Last) 단락의 용도를 구분한다.", "독자가 결론을 빨리 알아야 할 보고서에서 Point-Last를 써서 답답하게 만들지 않는다."),
W("추상 사다리(Ladder of Abstraction)", "구체", "일반", "Alternate between abstract claims ('latency hurt trust') and concrete facts ('42% abandoned checkout').", "추상적 주장 한 문장 바로 아래에 구체적 숫자·인명·장면 문장을 배치해 독자의 이해를 바닥에 딛게 한다.", "다섯 문장 연속으로 추상 개념어만 쌓아 공중에 뜬 문단을 쓰지 않는다."),
W("비교·대조 단락(Point-by-Point)", "비교", "대조", "Compare System A and System B attribute by attribute (cost, latency, complexity) instead of two blocks.", "A 전부 설명 후 B 전부 설명하는 블록 비교보다, 기준(속도·비용·위험)별로 A와 B를 번갈아 대조해 기억 부담을 줄인다.", "두 대상을 문장마다 무질서하게 오가며 독자가 어느 기준을 비교하는지 잃게 만들지 않는다."),
W("원인-결과 사슬과 2차 파급", "인과", "파급", "Trace first-order effects (lower latency) to second-order behavior (higher session depth).", "표면 원인에서 끝나지 않고 1차 결과와 2차 파급 효과로 이어지는 다단계 인과 단락을 구성한다.", "상관관계 두 개를 아무 연결 없이 붙여 인과 단락이라고 부르지 않는다."),
W("문제-해결-한계 단락", "해결", "한계", "State the problem, propose the fix, and candidly name what the fix still leaves unsolved.", "문제 정의 → 해결 메커니즘 → 이 해결책이 새로 낳는 비용·한계 3단으로 현실감 있는 기술·정책 단락을 쓴다.", "해결책을 완벽한 만병통치약처럼 묘사해 독자의 의심을 불러일으키지 않는다."),
W("양보와 전환 다리(Bridge)", "전환", "다리", "Bridge paragraphs with substantive links: 'Fixing latency helps retention, yet storage cost still doubles.'", "However, Moreover 같은 1단어 기계적 접속사 대신 앞 단락 핵심 명사를 받는 실질적 전환 문장(Substantive Transition)을 쓴다.", "단락 첫머리를 무조건 First, Second, Furthermore로만 열어 교과서 모범답안 티가 나게 하지 않는다."),
W("증거 통합과 인용문 녹이기", "인용", "해석", "Embed brief quotes inside your own grammatical frame rather than dropping standalone quote blocks.", "외부 기사나 데이터의 인용문을 한 문단 덩어리로 통째 던지지 않고, 핵심 구절만 내 문장 문법 속에 자연스럽게 녹여 해석을 붙인다.", "인용문 하나를 던져 놓고 그 인용이 왜 내 주장을 뒷받침하는지 설명 한 줄도 안 쓰지 않는다."),
W("단락 분량과 시선 호흡", "쪼개기", "합치기", "Split a 250-word wall of prose at its logical pivot; merge two 2-sentence fragments on one point.", "너무 뚱뚱해 논점이 둘이 된 단락은 논리 전환점에서 쪼개고, 한 생각만 담는데 괜히 줄바꿈한 파편 단락은 합친다.", "문장 수 규칙(무조건 4문장)에만 매달려 논리 단위가 중간에 쪼개지게 하지 않는다."),
W("모범 에세이 단락 연쇄 분석", "독해", "연쇄", "Trace how five consecutive Economist paragraphs hand off the argument from macro trend to local impact.", "유수 영문 잡지(Economist/New Yorker/AEON) 1편의 연속된 5개 단락이 서로 어떻게 바통을 넘기는지 전개 지도를 그린다.", "단락 개별의 문법만 보고 단락 간 논리적 도약 여부를 점검하지 않는다.", mode="read"),
W("듣기: 다단락 구두 강연 구조", "강연", "전개", "Listen to a 5-minute TED/podcast monologue and map the transitions between its four main sections.", "5분 원어민 강연·논평을 들으며 화자가 어떤 전환 신호로 앞 주제를 닫고 다음 논점으로 넘어가는지 받아 적는다.", "세부 사례에 정신이 팔려 전체 강연의 전환 이정표를 놓치지 않는다.", mode="listen"),
W("600단어 4단락 에세이 설계", "개요", "초고", "Draft a cohesive 4-paragraph analysis (Hook/Context, Mechanism, Counterpoint, Synthesis).", "도입-원리-대안/반론-종합 4개 단락(약 500~600단어)을 Point-First와 실질 전환 문장으로 연결해 작성한다.", "각 단락이 따로 노는 4개의 독립 150단어 글이 되지 않게 한다."),
W("단락 전개 점검", "바통", "통일", "Each paragraph's first sentence alone forms a coherent 4-sentence executive summary of the whole essay.", "작성한 4단락 글에서 각 단락 첫 문장(또는 핵심 문장)만 뽑아 읽었을 때 전체 글의 요약문이 되는지 검증한다.", "첫 문장 4개를 나열했을 때 논리 흐름이 끊기면 단락 순서나 첫 문장을 다시 고친다."),
])
