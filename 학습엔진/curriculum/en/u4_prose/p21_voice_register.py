# -*- coding: utf-8 -*-
"""Phase 21: 화자와 레지스터 (weeks 261–273)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("화자와 레지스터")

PHASE = phase("화자와 레지스터", 261, 273, "구체 사례", "어조 통제", "기술 문서, 경영진 보고, 동료 설득, 공개 에세이 등 독자와 목적에 맞는 화자 거리와 격식(Register)을 통제한다.", STYLE, [
W("독자·화자 관계와 거리", "화자", "거리", "Choose 'we' for shared team ownership, 'you' for user guides, and third-person for neutral audits.", "글 전체에서 화자가 독자와 어떤 거리(동료 'we', 안내자 'you', 중립 관찰자 '3인칭')로 말하는지 고정하고 끝까지 유지한다.", "한 글 안에서 'we'로 쓰다 갑자기 'one should', 다시 'the developer must'로 화자를 바꾸지 않는다."),
W("격식 스펙트럼(Register)", "격식", "구어", "Distinguish conversational Slack/blog prose from formal board memos and contractual prose.", "친근한 구어체(contractions, phrasal verbs)와 격식 산문체(Latinate verbs, full forms), 법률 문어체의 차이를 대조한다.", "임원 보고서 한가운데 'kinda', 'a bunch of', 'super cool' 같은 구어 속어를 섞지 않는다."),
W("권위와 겸손의 균형(Confidence)", "확신", "겸손", "Avoid timid filler ('I kind of feel maybe...') and arrogant absolutes ('obviously everyone knows').", "과도한 자기비하('In my humble opinion, maybe...')와 오만한 단정('Clearly anyone can see...') 사이의 차분한 전문가 어조를 잡는다.", "확신이 부족해 모든 문장에 'I think maybe'를 붙이거나 반대로 근거 없는 'undoubtedly'를 남발하지 않는다."),
W("감정 절제와 사실의 힘", "절제", "사실", "Replace outraged adjectives ('catastrophic, irresponsible') with measured metrics ('4 hours down, $80K lost').", "장애 회고나 비판 글에서 격앙된 감정 형용사를 걷어 내고 측정된 사실과 영향만으로 묵직한 어조를 만든다.", "감정적 비난어를 써서 오히려 독자가 글의 객관성을 의심하게 만들지 않는다."),
W("비난 없는 기술 회고 어조", "회고", "시스템", "Write blameless post-mortems: 'The deployment lacked an automated check', not 'Kim forgot to test'.", "장애·실패 보고서에서 특정 개인을 비난하는 어조 대신 시스템·절차·안전장치 결함을 짚는 건설적 어조를 쓴다.", "누구의 실수인지 사람 이름을 앞세워 방어적 문화를 만드는 보고서를 쓰지 않는다."),
W("반대자 존중과 지적 정직성", "존중", "정직", "State the strongest version of the opposing view before pointing out where its assumptions break.", "반대 입장을 비판할 때 상대 주장을 우스꽝스럽게 축소(허수아비 공격)하지 않고 가장 탄탄한 버전으로 공정히 요약한다.", "상대 의견을 'naive'나 'absurd'라고 깎아내려 설득력을 스스로 무너뜨리지 않는다."),
W("유머·아이러니의 절제된 사용", "위트", "경계", "Allow at most one understated dry aside, and never let wit obscure key numbers or deadlines.", "산문에 긴장을 푸는 절제된 위트(dry understatement)가 허용되는 자리와 절대 넣으면 안 되는 자리(장애·계약·요청)를 구분한다.", "위트를 부리다 핵심 결론이나 마감 시한이 모호해지게 두지 않는다."),
W("원문 에세이 화자 비교 읽기", "독해", "목소리", "Compare how Paul Graham (conversational clarity) and The Economist (terse authority) establish voice.", "서로 다른 두 모범 저자(예: Paul Graham/Zinsser vs Economist 사설)의 문단을 비교하며 문장 길이·대명사·어휘 선택을 분석한다.", "두 문체를 뒤섞어 앞부분은 에세이, 뒷부분은 딱딱한 보고서 투로 쓰지 않는다.", mode="read"),
W("목소리 충돌 문장 교정", "충돌", "교정", "Find and rewrite three jarring sentences whose register clashes with the surrounding memo.", "일관된 어조의 300단어 메모 속에 섞여 들어간 어조 충돌 문장(지나친 속어, 과장된 논문 투, 공격적 반문)을 찾아 다듬는다.", "어조가 튀는 문장을 '개성'이라며 방치해 글 전체의 신뢰도를 깨지 않는다."),
W("동일 사건 2가지 목소리 재작성", "전환", "2버전", "Rewrite a product outage summary first as an internal Slack update, then as a formal client letter.", "동일한 사건 1건을 1) 팀 내부 공유용(간결·직설·행동 중심)과 2) 외부 고객 사과문(정중·책임·보상 중심) 두 목소리로 쓴다.", "단어 몇 개만 바꾸고 문장 구조와 독자 배려 관점을 그대로 두지 않는다."),
W("듣기: 강연자의 어조와 청중 거리", "청취", "어조", "Analyze how a speaker shifts tone from opening rapport to serious policy recommendations.", "3~4분 원어민 발표/인터뷰 오디오에서 화자가 어조를 가볍게 여는 구간과 단호하게 핵심을 짚는 구간의 속도·억양을 포착한다.", "모든 문장을 같은 톤과 속도로 읽어 청중이 중요한 경고를 놓치게 하지 않는다.", mode="listen"),
W("목소리 일관성 장문 연습", "장문", "통일", "Write a 350-word opinion essay maintaining a measured, authoritative voice from first word to last.", "하나의 논점을 주제로 350단어 칼럼을 쓰되, 처음부터 끝까지 단 하나의 일관된 화자 목소리를 유지한다.", "글 후반부에 힘이 빠져 갑자기 구어체나 명령조로 어조가 흐트러지지 않게 한다."),
W("화자와 레지스터 점검", "일관", "어조", "Every sentence in both the internal memo and external essay stays true to its intended audience and register.", "두 가지 다른 청자를 향한 글(내부 기술 제안 vs 외부 고객/독자 칼럼)과 각 90초 낭독 녹음에서 어조 이탈이 없는지 검증한다.", "한 문장이라도 청자와 맞지 않는 과도한 격식이나 부적절한 속어가 남으면 다시 고친다."),
])
