# -*- coding: utf-8 -*-
"""Phase 22: 논증과 반론 처리 (weeks 274–286)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("논증과 반론 처리")

PHASE = phase("논증과 반론 처리", 274, 286, "어조 통제", "논증", "주장(Claim)-근거(Evidence)-논리연결(Warrant)-반론수용(Concession)-한계명시(Qualification)의 5요소 논증을 구사한다.", STYLE, [
W("논점(Thesis)의 반박 가능성", "반박가능", "주장", "Sharpen 'AI is important' into a falsifiable claim: 'Code review bots cut lint nitpicks by 40% but miss design flaws.'", "누구나 고개 끄덕이는 당연한 사실이나 모호한 찬양 대신, 합리적 반론이 가능한 구체적 논지(Testable Thesis)를 세운다.", "찬성도 반대도 할 수 없는 공허한 문장('Communication matters')을 중심 주장으로 잡지 않는다."),
W("주장-근거-연결고리(Warrant)", "연결", "Warrant", "State why your evidence supports your claim; don't let data sit unconnected to your conclusion.", "주장(Claim)과 데이터(Evidence) 사이에 '왜 이 숫자가 이 결론을 지지하는가'라는 논리적 연결고리(Warrant)를 명시한다.", "숫자 1개만 던지고 당연히 내 주장이 맞지 않느냐며 설명을 건너뛰지 않는다."),
W("질적 근거와 양적 근거의 배합", "근거", "배합", "Pair macro metrics ('turnover fell 18%') with one micro mechanism ('new hires shipped in week 1').", "통계 수치(양적 근거) 하나와 그 수치가 작동하는 구체적 메커니즘·사례(질적 근거) 하나를 나란히 묶어 설득력을 배가한다.", "통계만 나열해 무미건조하거나 일화 하나만으로 전체 집단을 성급히 일반화하지 않는다."),
W("한정사(Qualifiers)로 과장 방어", "한정", "정확", "Replace vulnerable absolutes ('always, never, proves') with calibrated qualifiers ('typically, under load, indicates').", "반례 하나에 논증 전체가 무너지지 않도록 'all/always/proves' 대신 적용 조건과 범위(typically, when traffic exceeds...)를 명시한다.", "절대 표현을 남발해 독자에게 작은 반례 하나로 전체 글의 신뢰를 꺾일 빌미를 주지 않는다."),
W("강한 반론 정면 돌파", "반론", "수용", "Address the strongest counterargument directly: 'Critics rightly note higher memory usage...'", "내 주장을 공격할 가장 날카로운 반론을 스스로 꺼내어 조건부 인정(Concession)한 뒤, 내 대안이 여전히 우월한 이유를 밝힌다.", "반론을 회피하거나 대답하기 쉬운 약한 반대 의견만 골라 반박하지 않는다."),
W("논리적 오류(Fallacy) 진단", "오류", "교정", "Spot and fix false dichotomy, post hoc causal leaps, and anecdotal generalization in a sample op-ed.", "흑백 논리(False Dichotomy), 전후 인과 비약(Post Hoc), 성급한 일반화가 숨은 샘플 글에서 논리 결함을 찾아 고친다.", "대안이 A 아니면 B 두 개뿐인 것처럼 몰아가거나 우연한 시차로 인과를 단정하지 않는다."),
W("정책·기술 제안(RFC) 논증 구조", "RFC", "트레이드오프", "Structure an engineering RFC around Context, Decision, Alternatives Considered, and Risks.", "실무 엔지니어링·비즈니스 RFC 문서처럼 현황-결정-기각된 대안과 그 이유-리스크 순서로 설득 구조를 짠다.", "내가 미는 대안의 장점만 쓰고 기각한 대안이 언제 더 나은지 언급조차 안 하지 않는다."),
W("오피니언·사설 논증 해부", "사설", "독해", "Deconstruct a Financial Times or Economist leader into Claim, Evidence, Concession, and Call to Action.", "The Economist 사설이나 FT 오피니언 1편을 읽고 주장-근거-반론처리-결론 요청의 배치 비율과 연결 표현을 뽑는다.", "단어 뜻만 해석하고 필자가 어느 문단에서 반론을 꺾고 무게중심을 옮기는지 놓치지 않는다.", mode="read"),
W("질문과 반박에 대한 서면 답변", "응답", "반박", "Respond to three skeptical reviewer comments with data, concessions, and boundary conditions.", "자신의 주장에 대해 비판적 리뷰어가 던진 3가지 질문에 방어적이거나 감정적이지 않게 데이터·한계 인정으로 답변한다.", "질문의 핵심을 피하고 원래 했던 말을 표현만 바꿔 반복하지 않는다."),
W("듣기: 찬반 토론 논점 포착", "토론", "청취", "Listen to a 5-minute policy debate and map each speaker's core claim, evidence, and concession.", "찬반 양측이 대립하는 5분 토론/대담 오디오를 듣고 각 측의 핵심 근거와 상대 주장을 인정한 지점을 받아 적는다.", "한쪽 말에만 동의해 반대쪽 화자의 결정적 수치와 조건을 놓치지 않는다.", mode="listen"),
W("600단어 설득 논증 에세이 작성", "에세이", "완성", "Draft a 600-word argumentative essay with thesis, two evidence pillars, one strong concession, and call to action.", "기술·사회·업무 주제 하나를 골라 5요소 논증 구조를 모두 갖춘 600단어 설득 에세이 초고를 작성한다.", "반론 수용 없이 주장만 600단어 동안 반복하는 일방적 선언문이 되지 않게 한다."),
W("논증 구술 방어(3분 Q&A)", "구술", "방어", "Present the 600-word argument in 90 seconds, then answer two tough counter-questions aloud.", "작성한 600단어 에세이 논지를 90초로 요약 발표한 뒤, 스스로 만든 가장 아픈 반론 2개에 대본 없이 즉답 녹음한다.", "반론 질문 앞에서 당황해 본래 주장의 조건을 모순되게 뒤집지 않는다."),
W("논증 점검", "논리", "반증", "The thesis is falsifiable, every claim has a warrant, and the strongest objection is fairly answered.", "논증 에세이의 각 문단에 [Claim][Evidence][Warrant][Concession][Rebuttal] 태그를 붙여 빠진 고리가 없는지 최종 검증한다.", "근거 없는 단정이나 연결고리 없는 숫자 나열이 남으면 통과하지 못한다."),
])
