# -*- coding: utf-8 -*-
"""Phase 15: 실전 계약 검토 (weeks 183–195)."""
from curriculum.common import phase
from curriculum.en.resources import DRAFT
from curriculum.en.templates import bind_writer

W = bind_writer("실전 계약 검토")

PHASE = phase("실전 계약 검토", 183, 195, "실전 교정", "계약 완료", "실제 공개 영문 계약(MSA/SaaS/NDA/DPA) 한 건을 처음부터 끝까지 검토·요약·협상 전략서로 완결한다.", DRAFT, [
W("계약 유형별 핵심 위험 지도", "MSA", "SaaS", "In SaaS agreements, focus on uptime SLA, data ownership, security breach notice, and auto-renewal.", "NDA, 용역(MSA/SOW), SaaS 구독, 소프트웨어 라이선스 4대 유형마다 가장 먼저 볼 핵심 조항 5개를 구분한다.", "NDA를 보면서 SaaS SLA를 찾거나 SaaS에서 소스코드 소유권을 요구하는 식의 유형 착오를 하지 않는다."),
W("공개 SaaS 약관 실전 독해 1", "가입", "데이터", "Section 4.1 grants the vendor a broad license to use aggregated Customer Data.", "실제 공개 SaaS/클라우드 약관(상반부)을 읽고 당사자·구독기간·갱신·데이터 권리·SLA 크레딧을 추출한다.", "SLA 미달 시 유일한 구제수단이 '요청 시에만 주는 소액 서비스 크레딧'이라는 단서를 놓치지 않는다.", mode="read"),
W("공개 SaaS 약관 실전 독해 2", "책임", "해지", "Liability is capped at fees paid in the preceding 6 months, with zero carve-out for data loss.", "같은 약관(하반부)의 면책·책임 상한·보증 부인·해지 시 데이터 반환·준거법을 추출해 전반부와 연결한다.", "해지 후 데이터 추출 유예기간(예: 30일 후 영구 삭제)이 있는지 확인하지 않고 넘어가지 않는다.", mode="read"),
W("데이터 처리 부록(DPA) 핵심", "DPA", "처리", "Processor shall notify Controller without undue delay, and within 48 hours, of a Security Incident.", "영문 DPA/보안 부록에서 위탁자·수탁자 역할, 하청(Subprocessor) 이의 제기 기간, 침해 통지 시한, 삭제 인증을 읽는다.", "하청업체 목록 변경 통지 후 이의 제기 기한(예: 10일)과 구제수단(해지권)이 연결되는지 놓치지 않는다.", mode="read"),
W("비대칭·불균형 조항 탐지", "비대칭", "균형", "Only Vendor may terminate for convenience on 30 days' notice, while Customer is locked for 3 years.", "양측에 똑같이 적용되어야 할 비밀유지·면책·해지·책임상한이 한쪽에만 유리하게 비대칭 작성된 지점을 찾아낸다.", "표면상 정중한 문장 뒤에 숨은 일방적 면책이나 일방적 가격 인상(CPI+10%) 권한을 놓치지 않는다."),
W("비즈니스 리스크 등급 분류", "Tier", "우선순위", "Classify Section 11 (uncapped data liability) as Deal-Breaker and Section 14 (venue) as Nice-to-Have.", "발견한 쟁점을 Deal-Breaker(필수 수정) / Negotiable(교환 가능) / Acceptable(수용) 3등급으로 분류한다.", "모든 수정 희망 사항을 Deal-Breaker로 올려 정작 꼭 바꿔야 할 조항의 협상력을 깎아먹지 않는다."),
W("경영진용 1쪽 계약 브리프", "요약", "결정", "Executive Brief: Recommend signing only if auto-renewal notice drops from 90 to 30 days.", "비법무 의사결정자(팀장/대표)를 위해 핵심 상업 조건, 주요 리스크 3개, 미결 질문 5개를 1쪽 영문 메모로 작성한다.", "조항 원문을 그대로 복붙해 비법무 독자가 읽지 못하게 만들지 않는다."),
W("협상 대안 패키지 설계", "패키지", "교환", "Package A trades a 2-year commitment for a 30-day termination notice and 2x data cap.", "독립적으로 쪼개 싸우는 대신 양보와 요구를 묶은 패키지 A/B 2개안을 설계해 협상 시나리오를 준비한다.", "상대가 1안을 거절했을 때 즉흥적으로 무너질 수 있으니 사전에 바닥선과 B안을 정해 둔다."),
W("듣기: 실전 계약 질의응답", "Q&A", "대응", "To clarify, our 2x super-cap covers only direct breach of Section 6 confidentiality.", "상대 법무·영업의 압박 질문 오디오 3분을 듣고, 즉각 방어·재확인·대안 제시 답변을 2분 내로 녹음한다.", "법률적 자문을 직접 내리는 표현 대신 계약 문구의 상업적 효과와 수정안으로 답한다.", mode="listen"),
W("실전 레드라인 풀 세트", "수정안", "사유", "All four critical clauses include surgical redline text, business rationale, and fallback language.", "실제 공개 계약서 발췌 4개 핵심 조항에 대해 원문-수정안-이유-절충안 4칸 레드라인을 완결한다.", "이유 칸에 '불공정하다' 같은 감정어만 적고 구체적 운영·금전 리스크를 쓰지 않는다."),
W("협상 후 최종 대조(Conform)", "대조", "정합", "Verify that Section 9's agreed 30-day payment term matches the SOW milestone table.", "협상으로 고친 조항들이 정의 조항, 다른 섹션의 교차 참조, SOW 표와 충돌하지 않는지 최종 정합성 검사를 수행한다.", "한 섹션의 숫자만 고치고 다른 섹션이나 첨부에 남은 옛 숫자를 못 보고 서명본으로 넘기지 않는다."),
W("10분 구술 최종 리뷰", "구술", "브리핑", "Deliver a 10-minute structured briefing covering contract map, top 3 risks, redlines, and open questions.", "검토한 실제 공개 계약 1건의 전체 구조, 상위 3개 리스크, 수정안, 서명 전 확인 질문을 10분 영어로 브리핑한다.", "메모를 줄줄 읽지 않고 키워드 지도만 보고 조리 있게 전달한다."),
W("계약 트랙 캡스톤 점검", "완결", "포트폴리오", "Complete 1-page Executive Brief, 4-clause Redline, Issue Matrix, and 5 pre-signature questions.", "계약 독해·수정·협상 트랙의 최종 산출물 세트(1쪽 경영진 브리프 + 이슈 표 + 레드라인 + 질문서)를 최종 감사한다.", "법률 자문을 대체하는 단정이 섞였거나 정의·참조 불일치가 남았으면 통과하지 못한다."),
])
