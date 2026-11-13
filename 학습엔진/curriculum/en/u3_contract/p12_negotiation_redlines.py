# -*- coding: utf-8 -*-
"""Phase 12: 협상과 조항 수정 (weeks 144–156)."""
from curriculum.common import phase
from curriculum.en.resources import DRAFT
from curriculum.en.templates import bind_writer

W = bind_writer("협상과 조항 수정")

PHASE = phase("협상과 조항 수정", 144, 156, "책임", "협상", "단어 하나가 아니라 상업적 위험 균형을 두고 대체 문장(Redline)과 구두 협상 전략을 구사한다.", DRAFT, [
W("상업적 양보와 조항 교환", "give-get", "trade", "If we extend the warranty to 180 days, can we cap indemnity at 2x fees?", "한 조항만 일방적으로 깎지 않고 보증 기간·지급 조건·책임 상한·편의 해지 기간을 묶어 교환한다.", "아무 대가 없이 핵심 보호 조항을 먼저 내주거나 쟁점 5개를 동시에 열어 논점을 흐리지 않는다."),
W("합리적 노력의 계층", "efforts", "기준", "Replace 'best efforts' with 'commercially reasonable efforts' and an explicit response SLA.", "best efforts, reasonable efforts, commercially reasonable efforts의 강도 차이와 객관적 수치 보완법을 익힌다.", "모호한 노력 동사를 그대로 둔 채 실제 기대하는 응답 시간이나 예산을 적지 않는다."),
W("지식 한정과 공개 예외", "knowledge", "schedule", "To Provider's knowledge after reasonable inquiry, the software infringes no patents.", "to the best of knowledge(실제 인지 vs 합리적 조사 후 인지)와 Disclosure Schedule 예외 처리 문장을 작성한다.", "모든 제3자 특허까지 100% 무침해를 무조건 보장하는 조항을 그대로 서명하지 않는다."),
W("거절 뒤 3단 대안 제시", "pivot", "대안", "We cannot accept unlimited liability; however, we propose a 2x super-cap for data breaches.", "단순 삭제(No) 대신 거절 이유(위험) → 수용 가능 대안 → 상대 보호 장치 3단으로 수정 문장을 제시한다.", "이유나 대체 문장 없이 조항 전체에 취소선만 그어 보내지 않는다."),
W("상대 레드라인 해독", "의도", "독소", "Counterparty struck 'written notice' and inserted 'sole discretion' in Section 6.", "상대가 보낸 레드라인 수정본에서 단어 1~2개 변경(예: 'reasonable' → 'sole', 'and' → 'or')이 바꾸는 리스크를 포착한다.", "작은 전치사나 접속사 수정이라 가볍게 보고 의도를 추적하지 않고 넘기지 않는다.", mode="read"),
W("일방 변경·자동 갱신 방어", "auto-renew", "동의", "This Agreement renews only upon mutual written agreement, rather than automatically.", "자동 갱신(evergreen), 일방 약관/가격 변경권, 무제한 감사(audit) 권한을 사전 통지·거부권·연 1회 제한으로 고친다.", "해지 통지 마감일(60일 전)을 놓쳐 원치 않는 1년 계약이 자동 연장되는 함정을 그대로 두지 않는다."),
W("비밀유지 예외와 강제 공개", "compelled", "예외", "Recipient may disclose if required by law, provided it gives prompt prior notice if permitted.", "비밀유지 4대 예외와 법원/기관의 강제 공개 명령 시 사전 통지·최소 공개 의무 문장을 작성한다.", "예외 조건이 너무 넓거나 법적 공개 시 사전 통지 단서(if legally permitted)를 빠뜨리지 않는다."),
W("불가항력·하도급·양도 조율", "subcontract", "consent", "Provider may use vetted subcontractors, provided Provider remains fully liable for their performance.", "하도급 금지 vs 고객 사전 서면 동의 또는 책임 유지 하 허용, M&A 시 동의 없는 양도 예외를 조율한다.", "클라우드 호스팅이나 결제 대행사 이용까지 하도급 금지에 걸리는 모순 문장을 남기지 않는다."),
W("협상 이슈 리스트(Issues List)", "이슈 표", "우선순위", "Our Issues List prioritizes three deal-breakers and offers fallback wording for each.", "조항 전체를 빨갛게 고치기 전에 핵심 쟁점 3~5개를 표(조항·원문·우려·수정안·대안)로 요약하는 이슈 리스트를 만든다.", "사소한 문구 20개와 치명적 책임 한도 1개를 똑같은 중요도로 섞어 보내지 않는다."),
W("듣기: 협상 통화 시뮬레이션", "청취", "응답", "I hear your concern on timing; what if we set a 15-day cure period with daily updates?", "상대의 반론 녹음(2분)을 듣고 상대의 진짜 핵심 이해관계(지연 방지 vs 비용 통제)를 파악해 60초 대응을 녹음한다.", "상대 말을 끝까지 요약 확인하지 않고 내 수정안만 반복하지 않는다.", mode="listen"),
W("레드라인 묶음과 이메일", "bundle", "메일", "Attached is our redline v2; we accepted Section 4 and proposed a 2x cap in Section 9.", "수정 문서(v2)와 함께 수용 항목·수정 묶음·사유·남은 미결 쟁점을 깔끔한 협상 커버 메일로 작성한다.", "첨부만 달랑 보내거나 수정 이유 없이 'Please review' 한 줄만 쓰지 않는다."),
W("8분 협상 콜 리허설", "역할극", "합의", "Let's confirm: we agree on the 2x super-cap, and Section 11 remains open for tomorrow.", "이슈 3개를 놓고 수용·절충·거절·미결 정리를 8분 양방향 협상 롤플레이로 녹음하고 회의록을 쓴다.", "합의되지 않은 쟁점을 구두로 어물쩍 넘기지 않고 합의/미결 표로 남긴다."),
W("협상과 레드라인 점검", "묶음", "이유", "All five redlines state the hidden risk, the replacement text, and one fallback option.", "실제 계약 1건에서 5개 레드라인 + 이슈 리스트 + 커버 메일 + 8분 협상 녹음을 묶어 일관성을 최종 점검한다.", "대체 문장 자체가 새로운 모호함을 낳고 있으면 통과하지 못한다."),
])
