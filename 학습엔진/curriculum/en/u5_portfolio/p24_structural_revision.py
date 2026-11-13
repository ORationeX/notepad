# -*- coding: utf-8 -*-
"""Phase 24: 구조적 퇴고 (weeks 300–312)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("구조적 퇴고")

PHASE = phase("구조적 퇴고", 300, 312, "정밀 어휘", "퇴고", "Zinsser와 Orwell의 원칙에 따라 하루 지난 초고를 거시 구조(Macro)에서 미시 문장(Micro) 순으로 수술한다.", STYLE, [
W("냉각기와 진단 읽기(24h Gap)", "냉각", "진단", "Put yesterday's draft aside for 24 hours, then read it like a critical stranger marking confusion points.", "쓰자마자 고치지 않고 하루 이상 묵힌 뒤, 작성자의 의도를 모르는 낯선 독자처럼 막히는 지점부터 표시한다.", "자기 머릿속 의도로 빈 논리를 채워 읽으며 '분명한 글'이라고 착각하지 않는다."),
W("역개요 추출(Reverse Outline)", "역개요", "지도", "Write a 10-word summary of what each existing paragraph actually does—not what you meant it to do.", "이미 쓴 초고의 각 문단 옆에 '실제로 하고 있는 역할'을 한 줄로 적어 역개요를 뽑고 중복·결락을 발견한다.", "개요와 다르게 4문단이 2문단 말을 또 반복하고 있는데 못 보고 지나치지 않는다."),
W("거시 수술: 삭제·합치기·이동", "재배치", "삭제", "Cut off-topic sections, merge scattered fragments on the same point, and move the true thesis to page 1.", "단어·쉼표 교정 전에 문단 통째 삭제, 순서 이동, 쪼개기/합치기 등 거시 구조(Macro-Editing)부터 먼저 단행한다.", "결국 삭제할 문단의 맞춤법과 형용사를 20분 동안 다듬는 헛수고를 하지 않는다."),
W("도입부 절단(Cut the Throat-Clearing)", "도입", "절단", "Delete the first warm-up paragraph if your real point only starts in paragraph two.", "작가가 워밍업하려고 쓴 막연한 첫 문단(Throat-Clearing)을 잘라 내고 진짜 힘 있는 두 번째 문단으로 글을 연다.", "'현대 사회에서 기술은 빠르게 발전하고 있다' 식의 뻔한 첫 문단을 아까워서 남겨 두지 않는다."),
W("군더더기 30% 감량(Zinsser Cut)", "압축", "Zinsser", "Strip 30% of words from a 400-word draft by removing clutter, redundancies, and self-evident padding.", "윌리엄 진서(Zinsser)의 '잡초 뽑기' 원칙으로 400단어 초고에서 뜻의 손실 없이 120단어를 덜어 낸 280단어 본을 만든다.", "내용과 구체적 증거까지 쳐내서 뼈만 앙상한 요약문으로 만들지 않는다."),
W("결론과 마지막 문장의 힘", "결론", "마침표", "End when you have made your point—preferably on a concrete image or clear forward implication, not 'In conclusion'.", "'In conclusion, we can see that...'처럼 앞 내용을 힘없이 되풀이하지 않고 여운·행동·새로운 시각으로 닫는다.", "이미 다 끝난 글을 '앞으로 모두가 노력해야 한다' 같은 상투적 교훈으로 늘어뜨리지 않는다."),
W("논리 비약과 빈 다리 채우기", "비약", "연결", "Identify two logical jumps flagged in reverse outlining and write explicit bridge sentences.", "역개요 단계에서 발견한 논리 단절 구간 2곳에 원인과 조건, 연결 근거를 보충해 독자가 따라올 수 있게 잇는다.", "감량에만 치우쳐 독자가 '갑자기 왜 이 결론이 나왔지?' 하고 멈추는 구멍을 남기지 않는다."),
W("리뷰 피드백의 구조적 반영", "피드백", "우선순위", "Triage five conflicting reader notes into structural fixes versus surface polish.", "제3자(또는 AI/가상 리뷰어)의 비판 피드백을 받아 구조적 지적부터 우선 반영하고 반영 내역을 기록한다.", "가장 고치기 쉬운 오타 피드백만 고치고 '주장이 모호하다'는 핵심 지적을 건너뛰지 않는다."),
W("소리 내어 읽으며 리듬 교정", "낭독", "호흡", "Read the full revised draft aloud at normal speaking pace; fix every sentence where you stumble or run out of breath.", "전체 원고를 소리 내어 읽으면서 숨이 막히거나 혀가 꼬이거나 어조가 튀는 문장만 정확히 찾아 다듬는다.", "눈으로만 대충 훑고 '매끄럽다'고 착각한 긴 관계절 문장을 그대로 두지 않는다."),
W("버전 대조와 변경 로그", "v1-v2", "이유", "Compare v1 and v2 side-by-side and document why each major cut or move improved clarity.", "초고(v1)와 퇴고본(v2)을 나란히 두고 삭제·이동·문장 압축이 독자 이해도를 어떻게 높였는지 6줄 변경 로그를 적는다.", "옛 버전을 덮어써 버려 무엇이 왜 나아졌는지 학습 피드백을 날리지 않는다."),
W("듣기: 원고 편집자 피드백 분석", "편집", "청취", "Listen to a writing craft podcast/critique and apply one structural cut principle to your own draft.", "원어민 글쓰기/편집 강연(3~4분)에서 구조 편집 원칙 2가지를 받아 적고 내 초고에 즉시 적용한 뒤 90초 설명한다.", "교정 이론만 듣고 내 글 한 줄도 고치지 않고 끝내지 않는다."),
W("타임어택 30분 신속 퇴고", "시간제한", "신속", "Edit an unfamiliar 500-word cluttered business/technical draft down to 350 crisp words in 30 minutes.", "처음 보는 지저분한 500단어 샘플 문서를 30분 안에 역개요 추출 → 도입 절단 → 명사화 제거 → 350단어 정제까지 마친다.", "앞 두 문장만 붙잡고 20분을 다 써서 뒷부분을 못 고치지 않는다."),
W("퇴고 점검", "구조", "감량", "The final draft is shorter, sharper, logically unbroken, and passes both reverse-outline and read-aloud tests.", "역개요 표 + v1/v2 비교 + 25~30% 압축된 최종본 + 낭독 녹음이 모두 기준을 충족하면 통과한다.", "단순 맞춤법 수정에만 머무르고 단락 구조가 그대로라면 통과하지 못한다."),
])
