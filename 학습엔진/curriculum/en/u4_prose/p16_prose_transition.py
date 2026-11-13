# -*- coding: utf-8 -*-
"""Phase 16: 고급 독해와 문체 전환 (weeks 196–208)."""
from curriculum.common import phase
from curriculum.en.resources import REPORT
from curriculum.en.templates import bind_writer

W = bind_writer("고급 독해와 문체 전환")

PHASE = phase("고급 독해와 문체 전환", 196, 208, "계약 완료", "C1 전환", "계약 트랙 이후 고급 논증·논설 독해와 정교한 영문 스타일(C1 전환)을 위한 교량 단계를 다진다.", REPORT, [
W("긴 문장의 정보 흐름", "Old-New", "흐름", "Begin sentences with familiar context before introducing complex new claims.", "앞 문장의 끝(Old info)으로 다음 문장을 열고 새 정보(New info)를 문장 끝에 두는 정보 흐름 원리(Joseph Williams <Style>)를 익힌다.", "문장마다 주어가 갑자기 바뀌어 독자가 문장 간 연결 고리를 매번 다시 찾게 만들지 않는다.", mode="read"),
W("명사화 해체(Action Verbs)", "동사", "명확", "Instead of 'The implementation of the policy caused a delay', write 'Implementing the policy delayed release'.", "동사를 명사로 바꿔 문장을 무겁게 만드는 Nominalization(make an investigation → investigate)을 행동 동사와 행위자 주어로 되살린다.", "주어 자리에 8단어짜리 추상 명사구를 넣고 동사는 is/has/occurred만 쓰지 않는다."),
W("장문 기사 구조 해부", "논증", "지도", "The author opens with a concrete anomaly, frames the tension, and tests two explanations.", "1,000단어 수준의 고급 에세이·분석 기사(Economist/Atlantic/Aeon)의 문단별 역할(도입-긴장-전환-반론-결론)을 지도로 뽑는다.", "단어 뜻만 찾고 글 전체가 어느 지점에서 반론을 꺾고 결론으로 가는지 보지 않는다.", mode="read"),
W("문맥 속 고급 어휘와 연어", "연어", "Collocation", "Use natural collocations like 'pose a risk', 'mitigate exposure', and 'bridge the gap'.", "개별 단어 암기 대신 고급 기사와 보고서에서 쓰이는 동사+명사 연어(Collocation) 15쌍을 문맥 속에서 익힌다.", "한국어 직역으로 'do a risk'나 'solve a gap' 같은 부자연스러운 조합을 쓰지 않는다."),
W("문장 길이와 강조 제어", "리듬", "위치", "Place the point you want remembered at the stressed end of a concise final clause.", "문장의 가장 강한 자리(끝부분, Stress Position)에 핵심 판단을 배치하고, 긴 수식어 뒤에 짧은 단언 문장으로 리듬을 준다.", "핵심 결론을 문장 한가운데 괄호나 관계절 속에 파묻어 버리지 않는다."),
W("듣기: 원어민 토론과 강연", "속도", "뉘앙스", "While the first speaker prioritizes growth, the second warns of structural debt.", "원어민 속도 5분 토론·강연 오디오에서 두 화자의 입장 차이, 양보 신호, 핵심 수치와 은유를 받아 적는다.", "천천히 또박또박 읽는 교재 음성만 듣다 자연스러운 속도와 연음·끼어들기를 놓치지 않는다.", mode="listen"),
W("분사·관계절·도치의 절제", "강조", "도치", "Only after three failed audits did the committee revise the rule.", "부정어/제한어 문두 도치(Not only..., Rarely...)와 계속적 용법(, which...)을 강조가 필요할 때만 절제해 쓴다.", "아무 이유 없이 도치나 비제한 관계절을 남발해 글 전체를 부자연스럽게 만들지 않는다."),
W("복합 논증 요약(250단어)", "압축", "원문", "Summarize a 1,200-word analysis in 250 words without distorting the author's caveats.", "1,200단어 고급 기사 1편의 주장·근거·반론·유보 조건을 250단어 요약문으로 쓰고 원문 논지와 대조한다.", "원문 필자의 유보 조건(caveat)을 빠뜨려 과장된 단정으로 왜곡하지 않는다.", mode="read"),
W("뉘앙스와 레지스터 전환", "어조", "청자", "Shift the same core decision from an internal engineering post-mortem to an executive note.", "동일한 기술·사업 사건을 1) 팀 내부 기술 회고와 2) 대외/경영진 요약 두 가지 레지스터로 각각 작성한다.", "경영진 요약에 내부 구현 약어를 쏟아내거나 기술 회고에 모호한 홍보성 문구를 쓰지 않는다."),
W("비유와 추상의 구체화", "구체", "이미지", "Replace 'operational friction increased' with 'support tickets doubled to 400 a week'.", "추상적 명사구(efficiency, synergy, friction)를 관찰 가능한 동사와 측정 수치로 내려쓰는 훈련을 한다.", "추상어만 이어 붙여 멋있게 보이지만 무슨 뜻인지 검증할 수 없는 문장을 남기지 않는다."),
W("3분 비평 말하기", "논평", "반론", "The author's case holds for large hubs, yet overlooks rural grid constraints.", "읽은 고급 기사 1편에 대해 요약(60초) → 강점(40초) → 반론·한계(80초)를 대본 없이 3분 녹음한다.", "기사 내용을 내 의견인 것처럼 그대로 되풀이만 하지 않고 독립된 비평 한 점을 세운다."),
W("스타일 퇴고(Style Audit)", "퇴고", "명료", "Cut 30% of word count from yesterday's 300-word draft while keeping every claim intact.", "직접 쓴 300단어 논평 초고에서 명사화·허사(there is, it is ~ that)·중복 수식어를 쳐내 210단어로 압축한다.", "단어를 줄이면서 핵심 단서 조건이나 논리 연결어까지 같이 지워 버리지 않는다."),
W("C1 전환 점검", "독해", "스타일", "Read a 1,000-word article, summarize in 200 words, and deliver a 3-minute critique.", "고급 원문 독해 요약 + 30% 감량 스타일 퇴고 + 3분 구두 비평을 한 세트로 완결해 5~7년차 고급 집필로 넘어간다.", "문법은 맞지만 명사화와 긴 주어로 읽히지 않는 문장이 남으면 퇴고를 다시 한다."),
])
