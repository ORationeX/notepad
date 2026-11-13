# -*- coding: utf-8 -*-
"""Phase 10: 계약 초안과 구조 (weeks 118–130)."""
from curriculum.common import phase
from curriculum.en.resources import DRAFT
from curriculum.en.templates import bind_writer

W = bind_writer("계약 초안과 구조")

PHASE = phase("계약 초안과 구조", 118, 130, "조항", "구조", "고전적 계약서 구조(Title/Recitals/Definitions/Operative)와 현대적 평이 영어 작성(Ken Adams) 원리를 적용한다.", DRAFT, [
W("당사자와 전문 분리", "parties", "recitals", "This Services Agreement is between Acme Corp. and Hanbit Studio LLC.", "서두에서 법적 실명·관할·약칭을 고정하고, Recitals(Whereas)에는 배경 사실만 두어 의무를 섞지 않는다.", "전문(Whereas) 안에 대금 지급이나 비밀유지 의무를 슬쩍 끼워 넣지 않는다."),
W("조항 기능의 분류", "category", "동사", "Acme shall pay the Fee; Provider may terminate upon notice; Acme represents...", "계약의 모든 문장을 의무(shall), 재량(may), 금지(shall not), 진술(represents), 정책(will/is) 5가지로 분류한다.", "모든 조항에 무분별하게 shall이나 will을 섞어 누가 무엇을 강제받는지 흐리지 않는다."),
W("정의 조항의 설계", "means", "원칙", "\"Deliverables\" means the source code and test suite listed in Exhibit A.", "정의된 용어는 첫 글자를 대문자로 고정하고 정의 안에 실질적 의무 문장을 넣지 않으며 순환 정의를 막는다.", "정의 조항 안에 '갑은 이를 7일 내 검수해야 한다' 같은 본문 의무를 숨기지 않는다."),
W("기간·기한과 일수 계산", "calendar", "business", "Provider shall deliver the report within ten Business Days after the Effective Date.", "기간 시작 이벤트, 달력일(calendar day) vs 영업일(Business Day), 만료 시각과 시간대(KST/UTC)를 고정한다.", "within 10 days처럼 시작 시점과 영업일 여부가 빈 모호한 기간 표현을 쓰지 않는다."),
W("대금·세금·상계 금지", "fee", "invoice", "Client shall pay $12,000 within 30 days of receiving an undisputed invoice, excluding VAT.", "총액·단가, 통화, 세금 포함 여부, 송장(invoice) 도달 기준 기산, 분쟁 시 미지급/지급 범위를 명시한다.", "금액만 적고 통화, 부가세 부담 주체, 기산 시점(발행일 vs 수령일)을 비워 두지 않는다."),
W("검수와 수용 절차", "acceptance", "deemed", "Client has ten Business Days to inspect Deliverables and either accept or state defects in writing.", "인도 후 검수 기간, 거절 시 구체적 하자 통지 의무, 기간 도과 시 간주 승인(deemed acceptance) 여부를 적는다.", "to Client's satisfaction처럼 주관적 기분에 따라 무한히 거절할 수 있는 기준을 두지 않는다."),
W("일방 의무 vs 상호 의무", "each", "mutual", "Each party shall keep the other party's Confidential Information secure for three years.", "상호 의무(Each party shall)와 일방 의무(Provider shall)의 주어를 대칭·비대칭 목적에 맞게 정확히 선택한다.", "실제로는 한쪽만 정보를 주는데 기계적으로 상호 조항을 복사하거나 주어를 수동태로 숨기지 않는다."),
W("교차 참조와 첨부 우선순위", "precedence", "exhibit", "If Exhibit A conflicts with the Master Agreement, the Master Agreement controls.", "SOW/Exhibit와 본 계약(MSA)이 충돌할 때 어느 문서가 우선하는지 우선순위 조항(Order of Precedence)을 둔다.", "본문과 첨부 표에 서로 다른 기한과 단가를 적어 놓고 우선순위 규칙을 빠뜨리지 않는다."),
W("수동태 제거와 행위자", "active", "행위자", "Provider shall notify Client in writing, rather than 'notice shall be given'.", "행위자 없는 수동태('Notice shall be given')를 능동태('Provider shall notify')로 바꿔 책임 주체를 고정한다.", "수동태 때문에 누가 통지하고 누가 승인해야 하는지 불명확하게 남기지 않는다."),
W("통지와 효력 발생", "notice", "deemed", "Notices are effective upon confirmed email delivery or three days after courier dispatch.", "공식 통지 수단, 수신 주소, 도달 간주 시점(발송 시 vs 수신 시)과 일반 업무 이메일과의 구분을 적는다.", "단순 채팅이나 구두 통보로 계약 해지 통지가 효력을 갖는지 애매하게 두지 않는다."),
W("보일러플레이트 해독", "entire", "severability", "This Agreement constitutes the entire understanding and supersedes prior drafts.", "Entire Agreement(완전합의), Severability(일부무효), Assignment(양도금지), Waiver(권리불포기) 조항의 기능을 읽는다.", "뒷부분 일반 조항(Boilerplate)이라서 그냥 건너뛰었다가 구두 약속 무효·양도 제한에 걸리지 않는다.", mode="read"),
W("용역 SOW 1쪽 초안", "SOW", "완결", "Exhibit A specifies scope, three milestones, acceptance criteria, and total fee of $15,000.", "배웠던 정의·기간·대금·검수·우선순위 조항을 결합해 1쪽짜리 가상 SOW(Statement of Work) 초안을 쓴다.", "범위 제외 항목(Out of Scope)과 변경 관리 절차 없이 작업 목록만 나열하지 않는다."),
W("계약 초안 점검", "기능", "일관", "Every clause in the 1-page SOW uses consistent defined terms and unambiguous verbs.", "작성한 SOW/조항 초안에서 정의 용어 대소문자, shall/may 일관성, 기간 기산점, 수동태 여부를 감사한다.", "정의되지 않은 대문자 용어가 있거나 shall/will이 혼용되어 있으면 통과하지 못한다."),
])
