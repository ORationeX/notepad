# -*- coding: utf-8 -*-
"""Phase 23: 어휘 정밀도와 뉘앙스 (weeks 287–299)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("어휘 정밀도와 뉘앙스")

PHASE = phase("어휘 정밀도와 뉘앙스", 287, 299, "논증", "정밀 어휘", "비슷해 보이는 동의어의 함의 차이, 연어(Collocation), 추상어 해체로 C1 수준의 어휘 정밀도를 기른다.", STYLE, [
W("의미가 겹치지 않는 동의어", "동의어", "뉘앙스", "Distinguish 'continuous vs continual', 'affect vs effect', 'imply vs infer', and 'comprise vs compose'.", "한국어로 번역하면 같아 보이지만 영어 문맥에서 방향·지속·주체가 갈리는 고급 혼동 어휘 12쌍을 문장으로 구분한다.", "번역 뜻만 외워 'The speaker inferred that...'처럼 화자와 청자의 방향을 반대로 쓰지 않는다."),
W("부정·긍정 함의(Connotation)", "함의", "편향", "Choose accurately among 'frugal / economical / stingy' or 'persistent / stubborn / resolute'.", "사전적 뜻(Denotation)은 같아도 화자의 평가와 태도(Connotation)가 갈리는 어휘 15그룹을 어조에 맞춰 고른다.", "긍정적 평가를 쓰려는 자리에 'cheap'이나 'notorious'처럼 부정적 함의가 박힌 단어를 쓰지 않는다."),
W("고급 동사-명사 연어(Collocation)", "연어", "조합", "Use authentic pairings: 'raise an objection', 'reach a consensus', 'alleviate a bottleneck'.", "원어민 고급 산문에서 자연스럽게 쓰이는 동사+목적어, 부사+형용사 연어 20쌍을 기사 예문에서 추출해 적용한다.", "사전 단어를 임의로 조합해 'do an objection'이나 'big possibility' 같은 부자연스러운 연어를 쓰지 않는다."),
W("추상 명사 껍질 벗기기", "추상어", "구체화", "Replace hollow nouns ('aspect, factor, situation, issue, thing') with exact concepts ('latency, fee, clause').", "뜻을 뭉뚱그리는 만능 추상어(aspect, factor, situation, area, case)를 문장에서 찾아 구체적 대상 명사로 치환한다.", "무엇을 말하려는지 모를 때 'there are many factors in this situation'으로 때우지 않는다."),
W("형용사 절약과 동사 승격", "동사", "정밀", "Swap 'walked very slowly and carefully' for 'crept' or 'edged'; 'very clear' for 'explicit'.", "약한 동사+부사 조합과 'very + 형용사'를 정확한 의미가 담긴 단일 정밀 동사·형용사로 교체한다.", "모든 강조를 very, really, extremely, significantly로 처리하지 않는다."),
W("고급 전치사·접속 부사 뉘앙스", "전환어", "정밀", "Distinguish 'nevertheless', 'conversely', 'consequently', 'meanwhile', and 'insofar as'.", "논리 관계를 세밀하게 가르는 고급 연결어(conversely vs in contrast, thereby, whereas, insofar as)의 정확한 쓰임을 익힌다.", "인과('therefore')와 시간('meanwhile')이나 대조('nevertheless' vs 'on the contrary')를 섞어 쓰지 않는다."),
W("상투적 비즈니스 버즈워드 제거", "클리셰", "평문", "Replace buzzwords ('synergy, leverage, paradigm shift, moving forward') with literal actions.", "의미를 마비시키는 상투적 유행어(leverage, utilize, streamline, bandwidth, circle back)를 투명한 실제 행동 동사로 바꾼다.", "멋있어 보이는 유행어로 문장을 채워 정작 구체적 의미가 0이 되지 않게 한다."),
W("고급 원문 어휘 채굴(Economist)", "독해", "채굴", "Extract 12 high-leverage verbs and collocations from an Economist/FT essay and reuse them in new contexts.", "Economist/FT/New Yorker 기사 1편(800단어)에서 정밀 동사와 연어 12개를 추출해 내 업무 문장으로 재창작한다.", "고급 희귀 단어(sesquipedalian)만 모으고 정작 글의 뼈대를 세우는 정밀 동사를 놓치지 않는다.", mode="read"),
W("확신도와 증거 강도 어휘", "강도", "수위", "Calibrate claim strength: 'demonstrates > indicates > suggests > is consistent with'.", "데이터와 증거의 수준에 맞춰 동사 강도(proves / shows / indicates / suggests / implies)를 정확히 계단화한다.", "표본 10개 관찰 결과를 두고 'conclusively proves'라고 과장하지 않는다."),
W("긴 어구 1~2단어로 압축", "압축", "경제성", "Trim wordy phrases: 'in the event that' → 'if', 'due to the fact that' → 'because', 'at this point in time' → 'now'.", "관성적으로 길게 늘어진 표현 15개('in light of the fact that', 'for the purpose of')를 1~2단어로 압축하는 훈련을 한다.", "분량을 늘리려고 일부러 4단어 전치사구를 쌓는 나쁜 습관을 남기지 않는다."),
W("듣기: 원어민 강연 정밀 어휘 포착", "청취", "연어", "Catch exact verb-noun collocations in a 4-minute NPR/TED talk and replay them in your own 60s summary.", "4분 원어민 강연·대담에서 화자가 쓴 정밀 동사·연어 8개를 받아쓰고, 즉시 내 주제 문장으로 변형해 녹음한다.", "들리는 쉬운 단어로만 머릿속 번역해 화자의 정밀한 단어 선택을 흘려듣지 않는다.", mode="listen"),
W("초고 어휘 리팩터링(Word Audit)", "교정", "어휘", "Audit a 300-word draft: eliminate buzzwords, upgrade 8 weak verbs, and replace all vague 'factors/aspects'.", "기존에 쓴 300단어 초고를 놓고 추상어·버즈워드·약한 동사+부사·장황한 연결구 12군데 이상을 정밀 교정한다.", "어려운 라틴어 단어로만 바꿔 문장이 오히려 부자연스럽고 현학적으로 변하지 않게 한다."),
W("정밀 어휘 점검", "정확", "자연", "Every word in the 250-word revised essay carries exact denotation, fitting connotation, and natural collocation.", "교정 전후 대조 목록 10쌍과 정밀 어휘가 녹아든 250단어 최종본, 90초 구두 해설을 남긴다.", "문법적 오류는 없지만 어색한 연어나 공허한 추상어가 남아 있으면 다시 다듬는다."),
])
