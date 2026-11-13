# -*- coding: utf-8 -*-
"""Phase 20: 장면과 사례 묘사 (weeks 248–260)."""
from curriculum.common import phase
from curriculum.en.resources import LONG
from curriculum.en.templates import bind_writer

W = bind_writer("장면과 사례 묘사")

PHASE = phase("장면과 사례 묘사", 248, 260, "단락 전개", "구체 사례", "딱딱한 일반론에 생명력을 불어넣는 구체적 관찰 사례·사건 장면·현장 디테일을 정확하고 간결하게 쓴다.", LONG, [
W("관찰 가능한 사실 선택", "관찰", "디테일", "Instead of 'the rollout was chaotic', write 'six engineers crowded around one monitor at 2 a.m.'", "추상적 평가('혼란스러웠다', '성공적이었다') 대신 카메라에 찍히는 구체적 행동·사물·시각·수치로 장면을 세운다.", "형용사 5개를 나열해 분위기를 꾸미려다 정작 독자 머리에 아무 그림도 못 그리지 않는다."),
W("사건의 한 자리와 시간 고정", "좌표", "초점", "Anchor the opening scene in one specific time and room before zooming out to the broader trend.", "칼럼이나 보고서 도입부(Anecdotal Lead)에서 시간·장소·인물 한 점을 먼저 고정한 뒤 전체 주제로 넓힌다.", "도입 사례 한 문단 안에서 어제 사무실과 작년 컨퍼런스와 내년 계획을 섞어 시선을 분산시키지 않는다."),
W("감각과 사물의 선별적 사용", "감각", "절제", "Pick one telling detail—the blinking red queue alert—rather than cataloging every object in the room.", "모든 소품과 감각을 다 적는 대신 주제를 압축해서 보여 주는 결정적 디테일(Telling Detail) 하나만 남긴다.", "관련 없는 옷차림이나 날씨 묘사를 길게 넣어 본론 진입을 300단어 늦추지 않는다."),
W("구체적 인물과 대사 한 줄", "인물", "대사", "Quote the exact question the warehouse lead asked: 'Which barcode wins when both scan?'", "사례 속 실무자·고객이 던진 결정적 한 마디(직접 인용 또는 간접 화법)로 현장의 병목을 즉시 이해시킨다.", "긴 연극 대본처럼 대사를 10줄씩 늘어놓아 논픽션 사례의 속도를 죽이지 않는다."),
W("현장 절차의 생생한 동사", "동작", "동사", "Use vivid, exact verbs ('throttled, queued, bypassed, flagged') over generic 'did, had, made'.", "현장의 작업과 사건을 묘사할 때 만능 동사(went, got, made, happened)를 정확한 행동 동사로 바꾼다.", "동작을 전부 'was + 형용사' 상태 묘사로 써서 장면이 정지 사진처럼 멈추게 하지 않는다."),
W("사례에서 일반 논점으로 도약(Nut Graf)", "전환", "통찰", "Bridge the opening vignette to the thesis: 'That Tuesday outage exposed a flaw in every regional node.'", "구체적 장면·사례를 1~2단락 보여 준 직후, 그 사례가 왜 더 큰 보편적 문제인지 선언하는 중심 문단(Nut Graf)을 쓴다.", "재미있는 일화만 끝까지 쓰다가 그래서 독자가 무엇을 배워야 하는지 빠뜨리지 않는다."),
W("명품 논픽션 사례 도입 읽기", "모델", "분석", "Study how a New Yorker or Atlantic feature opens with a concrete micro-scene before stating its claim.", "영미권 일류 논픽션 기사(New Yorker, Economist, MIT Tech Review)의 도입 사례(Lead → Nut Graf) 2편을 정밀 분석한다.", "한국어 수필식 감상문처럼 막연한 계절 인사로 글을 열지 않는다.", mode="read"),
W("대조되는 두 사례 병치", "병치", "대비", "Juxtapose the 2021 manual audit with the 2026 automated check to make the shift visible.", "변화를 설명할 때 과거 장면과 현재 장면, 또는 성공 현장과 실패 현장을 짧게 나란히 배치해 차이를 드러낸다.", "두 사례 사이에 설명을 너무 길게 넣어 대비 효과가 사라지게 하지 않는다."),
W("과장 수식어 솎아내기(Kill Your Darlings)", "삭제", "절제", "Cut redundant adverbs ('extremely, literally, very') so concrete nouns and verbs carry the weight.", "쓴 사례 글에서 부사(-ly)와 과장 형용사를 지우고 명사와 동사 자체의 힘만으로 장면을 세운다.", "화려한 미사여구가 좋은 문장이라는 착각으로 형용사를 명사마다 두 개씩 붙이지 않는다."),
W("듣기: 스토리텔링·팟캐스트 사례", "청취", "장면", "Listen to a 4-minute NPR/Planet Money story and note the exact moment the host pivots from story to analysis.", "원어민 내러티브 저널리즘(Planet Money, 99% Invisible 등) 4분 오디오에서 사례 도입과 논점 전환 문장을 받아쓴다.", "스토리만 듣다 재미있었다고 끝내지 않고 사례-주제 연결 구조를 뽑는다.", mode="listen"),
W("사례 중심 도입+본론 400단어", "작성", "통합", "Write a 400-word piece opening with a 120-word concrete scene and pivoting cleanly to a 280-word analysis.", "120단어 구체 사례 장면(Lead) + 50단어 핵심 질문/논점(Nut Graf) + 230단어 원인·대안 분석을 하나로 잇는다.", "도입 장면과 본론 분석이 서로 다른 주제를 말하거나 톤이 갑자기 끊기지 않게 한다."),
W("현장 사례 퇴고와 낭독", "퇴고", "속도", "Read the 400-word draft aloud; tighten any scene sentence where concrete action stalls.", "초고를 낭독하며 장면 묘사에서 멈칫거리는 수식어나 추상적 요약 문장을 찾아 즉시 구체 행동으로 고친다.", "사례 문단 안에 성급한 교훈이나 요약 문장을 미리 섞어 김새게 만들지 않는다."),
W("장면과 사례 점검", "현장", "도약", "One telling detail, one concrete scene, and a crisp Nut Graf connecting story to system insight.", "독립된 관찰 장면 1개와 그 장면에서 끌어낸 일반 통찰이 매끄럽게 이어진 400단어 에세이와 2분 구두 요약으로 점검을 마친다.", "장면이 모호한 일반론이거나 통찰과 무관한 장식이면 통과하지 못한다."),
])
