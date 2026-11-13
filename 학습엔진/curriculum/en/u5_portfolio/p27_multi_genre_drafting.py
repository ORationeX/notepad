# -*- coding: utf-8 -*-
"""Phase 27: 세 장르 통합 집필 (weeks 339–351)."""
from curriculum.common import phase
from curriculum.en.resources import LONG
from curriculum.en.templates import bind_writer

W = bind_writer("세 장르 통합 집필")

PHASE = phase("세 장르 통합 집필", 339, 351, "서사 논픽션", "장문 완성", "설명문·논증 비평문·서사 논픽션 세 장르를 같은 핵심 질문 아래 집필·대조하여 C1 장문 역량을 완성한다.", LONG, [
W("공통 핵심 질문과 3장르 매트릭스", "3장르", "기획", "Frame one central question across three genres: an explainer, an argument, and a narrative case.", "하나의 중심 주제(예: 자동화와 신뢰, 레거시 교체, AI 검증)에 대해 설명문·논증문·서사문 3편이 각각 맡을 역할을 기획한다.", "세 편이 같은 결론과 예시만 형식 조금 바꿔 반복하게 기획하지 않는다."),
W("제1편: 심층 설명문 개요와 도입", "제1편", "개요", "Outline and draft the opening 350 words of a technical/domain explainer for a smart outsider.", "3편 중 첫째(심층 설명문, 목표 1,000단어)의 섹션 지도와 독자 약속이 담긴 도입 350단어를 집필한다.", "전문 용어를 설명 없이 쏟아내어 독자를 1문단에서 떨어뜨리지 않는다."),
W("제1편: 심층 설명문 완성과 자가진단", "제1편", "완성", "Complete the 1,000-word explainer with concrete tables/mechanisms and test its Topic-Focus flow.", "첫째 편 1,000단어를 완결하고 독자 모델·절차·원인 메커니즘·사실-추정 분리가 지켜졌는지 점검한다.", "분량을 채우려고 중복 예시를 두 번 늘리지 않는다."),
W("제2편: 논증 비평문 개요와 반론 설계", "제2편", "개요", "Outline a 1,000-word argumentative essay including two evidence pillars and the strongest counterargument.", "둘째 편(논증 비평문, 목표 1,000단어)의 반박 가능한 논지, 근거 배합, 정면 반론 수용 구간을 설계하고 350단어를 쓴다.", "반론을 1문장으로 대충 치우고 내 주장만 되풀이하게 설계하지 않는다."),
W("제2편: 논증 비평문 완성과 근거 검증", "제2편", "완성", "Finish the 1,000-word argument ensuring every numerical claim has an explicit warrant and qualifier.", "둘째 편 1,000단어를 완결하고 한정사(Qualifiers), 연결고리(Warrant), 반론 처리 균형을 검증한다.", "감정적 수식어나 검증 불가능한 절대 표현을 남기지 않는다."),
W("제3편: 서사 논픽션 개요와 장면 배치", "제3편", "개요", "Outline a 1,000-word narrative case with In Medias Res opening, two escalations, and a costly turning point.", "셋째 편(서사 논픽션, 목표 1,000단어)의 위기 도입, 갈등 고조, 선택의 순간, 배경 통합 지점을 설계하고 350단어를 쓴다.", "사건의 배경 설명으로 첫 400단어를 소비하지 않는다."),
W("제3편: 서사 논픽션 완성과 속도 교정", "제3편", "완성", "Complete the 1,000-word narrative case and balance real-time scenes with brisk summary bridges.", "셋째 편 1,000단어를 완결하고 장면 vs 요약의 완급과 과잉 부사 삭제를 마무리한다.", "결론부에 뻔한 도덕적 설교 문단을 덧붙이지 않는다."),
W("장르 교차 독해와 원문 대조", "교차", "비교", "Compare the opening 200 words across your three pieces against three published models in those genres.", "내가 쓴 세 편의 도입 200단어씩을 각각 해당 분야 모범 원문(Stripe Docs / Economist / New Yorker)과 나란히 놓고 격차를 진단한다.", "내 글을 읽고 막연히 '괜찮네' 하지 않고 어휘 밀도와 리듬 차이를 구체적으로 표시한다.", mode="read"),
W("듣기: 세 편의 3분 구두 요약 녹음", "청취", "구술", "Record three distinct 90-second oral pitches—one explanatory, one persuasive, one narrative.", "세 편의 글을 각각 듣는 청중의 목적에 맞게 90초씩 다른 어조(설명/설득/스토리텔링)로 녹음하고 자기 청취로 평가한다.", "세 편 모두 똑같은 단조로운 보고서 낭독 톤으로 읽지 않는다.", mode="listen"),
W("한 편 선택 및 1,800단어 심화 확장", "심화", "확장", "Select the strongest piece and expand it into an 1,800-word flagship draft with deeper evidence.", "세 편 중 중심 질문에 가장 깊게 답하는 1편을 대표작으로 고르고, 2차 근거와 세밀한 반론/장면을 더해 1,800단어로 확장한다.", "단순히 문장을 늘려 1,800단어를 채우지 않고 새로운 층위의 통찰과 증거를 더한다."),
W("대표작 1차 거시 퇴고(400단어 절단)", "거시퇴고", "압축", "Cut 350–400 redundant words from the 1,800-word flagship draft while preserving every structural pillar.", "1,800단어 대표작을 하루 묵힌 뒤 역개요를 뽑고 불필요한 서두·중복 문단·명사화를 쳐내 1,450단어 고밀도 본문으로 정제한다.", "단어 수 줄이기에 겁먹어 장황한 문단을 그대로 남기지 않는다."),
W("미시 스타일 및 낭독 폴리싱", "폴리싱", "낭독", "Read all 1,450 words aloud to polish cadence, collocations, stress positions, and register consistency.", "정제된 1,450단어 대표작 전체를 소리 내어 읽으며 연어·강조 끝자리·어조 충돌을 최종 폴리싱한다.", "초반 500단어만 정성껏 고치고 후반 900단어를 대충 넘기지 않는다."),
W("세 장르 점검", "완성", "대조", "Three distinct 1,000-word pieces plus one 1,450-word flagship essay, each true to its genre and audience.", "세 장르의 목적·구조·어조가 명확히 구분되고 1,450단어 대표작이 C1 스타일 기준을 통과하는지 최종 점검한다.", "세 글의 문체와 구조가 구분되지 않거나 논증 비약이 남았으면 점검을 마친 것이 아니다."),
])
