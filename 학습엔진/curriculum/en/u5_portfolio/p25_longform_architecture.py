# -*- coding: utf-8 -*-
"""Phase 25: 긴 글 아키텍처 (weeks 313–325)."""
from curriculum.common import phase
from curriculum.en.resources import LONG
from curriculum.en.templates import bind_writer

W = bind_writer("긴 글 아키텍처")

PHASE = phase("긴 글 아키텍처", 313, 325, "퇴고", "장문 설계", "1,500~2,500단어 규모의 장문 에세이·기술 백서·심층 분석 보고서를 설계하기 위한 질문·구조·아키텍처를 세운다.", LONG, [
W("장문 한 권의 중심 질문", "질문", "긴장", "Frame a 2,000-word essay around one durable tension—not a broad textbook topic.", "장문을 지탱하는 것은 '소개'가 아니라 긴장감 있는 단 하나의 중심 질문(Central Tension/Question)이다.", "'원격근무의 모든 것'처럼 백과사전식 넓이로 잡으면 2,000단어가 산만한 메모 모음이 된다."),
W("긴 글의 3가지 매크로 골격", "골격", "유형", "Choose among Problem-Solution, Dialectical (Thesis-Antithesis-Synthesis), or Chronological Investigation.", "문제-해결형, 변증법적 대조형, 시간순 탐구형 3가지 장문 골격 중 내 중심 질문에 가장 맞는 뼈대를 선택한다.", "목적과 맞지 않는 골격을 골라 중간에 구조가 무너지지 않게 한다."),
W("독자와의 서두 계약(Opening Contract)", "계약", "서두", "Promise the reader within the first 200 words what question you will answer and what you will exclude.", "도입 200단어 안에서 중심 질문, 왜 지금 중요한지, 그리고 이 글이 다루지 않을 범위 경계를 독자와 약속한다.", "독자가 500단어를 읽을 때까지 이 글이 무슨 얘기를 하려는 것인지 알 수 없게 끌지 않는다."),
W("섹션별 고유 역할과 소제목 지도", "섹션", "역할", "Assign each of 5 sections one non-overlapping job so the Table of Contents tells the story.", "5개 섹션의 제목과 핵심 질문만 나열해도 전체 논증의 기승전결이 읽히는 목차 지도(Section Blueprint)를 짠다.", "섹션 2와 섹션 3이 같은 논점을 다른 사례로 반복하게 설계하지 않는다."),
W("긴장 유지와 중간 전환(Pacing)", "긴장", "전환", "End each section by opening the sub-question that motivates the next section.", "각 장·섹션의 마지막 문단이 앞 섹션의 결론을 닫는 동시에 다음 섹션이 왜 필요한지 질문을 여는 연결 장치 역할을 하게 설계한다.", "섹션마다 독립된 작은 글처럼 끊어져 독자가 다음 섹션으로 넘어갈 동기를 잃지 않게 한다."),
W("사례와 분석의 교차 배치", "배치", "리듬", "Alternate heavy conceptual sections with concrete case studies to sustain reader attention.", "추상적 개념·원리 섹션만 1,000단어 연속 배치하지 않고 구체 사례·수치 섹션과 교차해 독자의 인지 호흡을 설계한다.", "사례를 전부 뒤 부록에 몰아 두고 앞 1,200단어를 건조한 추상 이론으로 채우지 않는다."),
W("복잡한 장문 모델 해부 1 (구조)", "장문독해", "구조", "Map the 5-section arc, Nut Graf, and section transitions of a 2,000-word Economist/Atlantic feature.", "2,000단어 이상의 영미권 명문 장문 피처 1편(1~2일차 정독)의 전체 아키텍처, 전환 문장, 근거 배치를 역설계한다.", "긴 글을 단어 하나하나 번역하느라 숲(장별 배치)을 놓치지 않는다.", mode="read"),
W("복잡한 장문 모델 해부 2 (반론·결론)", "장문독해", "결론", "Analyze how the same feature handles its sharpest counter-evidence in section 4 before synthesizing.", "같은 장문 모델의 후반부에서 필자가 반대 증거를 어떻게 다루고 서두의 약속을 어떻게 회수하는지 분석한다.", "서두의 질문에 답하지 않고 엉뚱한 미래 전망으로 슬그머니 끝내는지 비판적으로 점검한다.", mode="read"),
W("주석·참고와 본문 분리 전략", "주석", "수위", "Keep core argument crisp in the main flow; relegate technical caveats and edge citations to footnotes/asides.", "본문 흐름을 끊는 부가 수치·역사 배경·예외 주석을 각주나 짧은 괄호 주석으로 밀어내는 경계를 정한다.", "중요한 핵심 단서 조건까지 각주로 숨기거나, 반대로 사소한 TMI를 본문 한가운데 넣지 않는다."),
W("서론·결론의 대칭 회수(Bookending)", "회수", "대칭", "Return in the final section to the opening scene or question, transformed by the intervening analysis.", "서론에서 열었던 질문이나 사례 장면을 결론부에서 분석을 거친 새로운 시각으로 다시 비추어 닫는다(Bookending).", "서론의 사례와 전혀 무관한 결론 문단으로 글을 마무리하지 않는다."),
W("듣기: 15분 장문 강연 구조 추적", "장문청취", "지도", "Listen to a 15-minute lecture/podcast feature and reconstruct its 5-part outline from audio alone.", "15분 분량의 수준 높은 영어 강연·심층 다큐 오디오를 듣고 전체 목차, 전환 포인트, 핵심 사례를 받아 적는다.", "중간 5분에서 집중력을 잃지 않고 화자의 구조 표지(First/Now let's turn to...)를 따라간다.", mode="listen"),
W("2,000단어 장문 상세 청사진 완성", "청사진", "설계", "Produce a detailed 2,000-word article blueprint with section claims, evidence list, and transition bridges.", "실제 집필할 1,800~2,000단어 장문 에세이/기술 백서의 섹션별 주장, 배치할 사례·데이터, 전환 문장, 분량 배분 청사진을 쓴다.", "청사진에 막연한 주제 단어만 적지 않고 각 섹션의 핵심 문장을 완전한 영어 문장으로 쓴다."),
W("장문 설계 점검", "목차", "약속", "The 5-section outline answers one central tension cleanly and reconciles opening promise with conclusion.", "작성한 장문 청사진의 서두 약속, 섹션 논리 흐름, 반론 배치, 결론 회수를 3분 구두 브리핑으로 검증한다.", "섹션 간 순서 근거가 모호하거나 서두 질문과 결론이 어긋나면 청사진을 고친다."),
])
