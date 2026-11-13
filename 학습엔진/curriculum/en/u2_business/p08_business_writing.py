# -*- coding: utf-8 -*-
"""Phase 08: 실무 글쓰기와 논증 (weeks 92–104)."""
from curriculum.common import phase
from curriculum.en.resources import REPORT
from curriculum.en.templates import bind_writer

W = bind_writer("실무 글쓰기와 논증")

PHASE = phase("실무 글쓰기와 논증", 92, 104, "회의", "보고서", "차트·데이터 해석과 비즈니스 기사 요약을 넘어 1쪽 논리 보고서와 후속 메일(B2)을 쓴다.", REPORT, [
W("차트 축과 추세", "축", "변곡점", "While sign-ups grew by 18% in Q2, churn rose slightly after June.", "축 단위·비교 기간·변곡점을 한 문장에 묶어 차트의 핵심 방향을 먼저 말한다.", "축과 단위를 빼고 숫자만 읽거나 표의 모든 행을 나열하지 않는다."),
W("비교와 비율 분석", "비율", "격차", "Mobile traffic accounted for 62% of visits, twice as high as desktop.", "단순 수치 대신 배수(twice as...as), 비율(accounted for), 증감폭(% vs %p)을 구분해 쓴다.", "퍼센트(%) 변화와 퍼센트포인트(%p) 차이를 혼동해 과장 보고하지 않는다."),
W("원인과 상관 구분", "원인", "상관", "Higher latency appears linked to dropouts rather than pricing changes.", "데이터가 보여 주는 상관관계와 확정된 인과관계를 동사(suggest/correlate vs cause)로 구분한다.", "단순 동시 발생을 단정적 인과(proved that)로 과장하지 않는다."),
W("기사 요약: 1단락 압축", "요약", "논지", "The Economist article argues that energy storage, not generation, is the bottleneck.", "Economist/HBR 짧은 글(400단어)을 읽고 필자의 핵심 주장과 근거 2개를 5문장으로 압축한다.", "원문 문장을 그대로 복사해 이어 붙이지 않는다.", mode="read"),
W("구조화된 1쪽 보고서", "BLUF", "결론 우선", "Bottom line: we should delay launch by one week to fix checkout errors.", "결론과 권고를 맨 첫 줄(BLUF)에 두고 배경·근거·리스크·요청 순으로 1쪽 보고서를 쓴다.", "배경 설명을 반 페이지 먼저 써서 바쁜 독자가 결론을 끝까지 찾게 만들지 않는다."),
W("강한 반론 수용", "concede", "refute", "Admittedly, delaying launch costs marketing momentum; however, broken checkout loses retention.", "예상 반론을 Admittedly/Granted로 인정한 뒤 however/nevertheless로 재반박해 설득력을 높인다.", "반대 의견을 아예 무시하거나 근거 없이 틀렸다고만 쓰지 않는다."),
W("대안 비교 표와 문장", "option", "trade-off", "Option A cuts cost by 15%, whereas Option B preserves delivery speed.", "두 대안의 비용·기간·리스크를 whereas/by contrast 구문으로 공정하게 대조한다.", "장점만 나열하고 선택한 대안이 감수해야 할 단점을 숨기지 않는다."),
W("의사결정 후속 메일", "owner", "deadline", "As agreed today, Mina will update the forecast by Thursday at 3 p.m.", "회의 결정 사항, 담당자(Owner), 마감 시한, 미결 쟁점을 번호 목록으로 확정해 보낸다.", "We will check soon처럼 담당자와 날짜가 빈 행동 항목을 남기지 않는다."),
W("듣기: 실적·브리핑 분석", "숫자", "전망", "Revenue grew 12% year-over-year, driven primarily by enterprise renewals.", "3분 기업 브리핑·강연 오디오를 듣고 실적 수치, 성장 요인, 리스크 전망을 받아 적는다.", "긍정 수치만 적고 가이던스 하향이나 위험 조건을 놓치지 않는다.", mode="listen"),
W("차트 2분 경영진 보고", "핵심", "요청", "Churn peaked at 4.2% in May, so we propose a 30-day onboarding check-in.", "차트 요약(30초) + 원인 분석(40초) + 권고안과 요청(50초)을 2분 안에 대본 없이 말한다.", "숫자 설명만 90초 하다가 정작 무엇을 결정해 달라는지 요청을 빠뜨리지 않는다."),
W("비판적 독해와 논평", "가정", "한계", "The report assumes flat churn, yet seasonal drops usually hit in August.", "외부 보고서나 기사에서 숨은 가정(assumption)과 표본 한계를 찾아 한 문단 논평을 쓴다.", "기사의 권위에 눌려 모든 수치와 결론을 무비판적으로 수용하지 않는다.", mode="read"),
W("다중 수신자 조율 메일", "이해관계", "어조", "While engineering prioritizes stability, sales needs the demo ready by Monday.", "서로 이해가 충돌하는 두 팀 사이에서 사실·제약·타협안을 중립적 어조로 정리한 메일을 쓴다.", "어느 한 팀의 불만이나 비난 어조를 그대로 이메일에 옮기지 않는다."),
W("보고서와 브리핑 점검", "보고", "대조", "The 1-page memo and 2-minute briefing align on both metrics and action owners.", "1쪽 분석 보고서, 차트 2분 구두 보고, 후속 메일이 같은 수치와 결론을 가리키는지 검증한다.", "보고서 수치와 구두 발표 수치가 다르거나 행동 기한이 빠지면 통과하지 못한다."),
])
