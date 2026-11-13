# -*- coding: utf-8 -*-
"""Phase 14: 문장 수정과 레드라인 (weeks 170–182)."""
from curriculum.common import phase
from curriculum.en.resources import DRAFT
from curriculum.en.templates import bind_writer

W = bind_writer("문장 수정과 레드라인")

PHASE = phase("문장 수정과 레드라인", 170, 182, "정밀 독해", "실전 교정", "계약서·정책문·기술약관의 실제 문장을 병렬 구조, 대명사, 모달, 정의 일관성 기준으로 대폭 리팩터링한다.", DRAFT, [
W("의무와 조건의 분리", "조건", "의무", "Move embedded conditions to the front: 'If Client requests..., Provider shall deliver...'", "문장 중간에 끼어든 조건·시점·예외를 문두나 별도 문장으로 빼서 핵심 의무를 한눈에 보이게 한다.", "한 문장 안에 주어·조건·예외·지급액·예외의 예외를 전부 욱여넣지 않는다."),
W("지시어·대명사 제거", "명사", "반복", "Replace ambiguous 'it' or 'such party' with the exact defined term 'Provider'.", "법률·기술 문서에서는 세련된 변주(Elegant Variation)나 대명사(it, they, the former)를 피해 동일 명사를 반복한다.", "같은 대상을 'Provider', 'Vendor', 'Consultant', 'it'로 번갈아 불러 다른 당사자처럼 오인시키지 않는다."),
W("병렬 구조(Parallelism) 교정", "나열", "형태", "Align list items grammatically: '(a) pay fees, (b) deliver code, and (c) notify Client.'", "목록이나 A and B 구조에서 품사·시제·조동사 범위가 모든 항목에 동일하게 걸리도록 맞춘다.", "목록 (a)에만 'shall'이 붙고 (b)에는 명사구만 남아 의무인지 아닌지 불분명해지지 않게 한다."),
W("조동사 남용 제거(Shall Scrub)", "shall", "정리", "Audit every 'shall' and convert non-obligations (e.g., 'This Agreement shall terminate') to 'terminates'.", "무생물 주어('The term shall begin', 'Notice shall be')에 잘못 쓰인 shall을 제거하고 행위자 의무에만 남긴다.", "사실 선언이나 정의, 자동 효과 문장에 관성적으로 shall을 붙여 두지 않는다."),
W("숨은 복수·단수 수일치 함정", "단복수", "각각", "Clarify whether an obligation applies to 'each Deliverable' individually or 'Deliverables' in aggregate.", "복수 명사 주어/목적어가 각자(individually)를 뜻하는지 전체 합계(in the aggregate)를 뜻하는지 명시한다.", "'The parties shall pay $1,000'가 각자 1,000달러인지 합쳐서 1,000달러인지 모호하게 두지 않는다."),
W("수치·공식 문장의 재작성", "공식", "검산", "Express tiered fee formulas as 'F = $500 + 0.05 * (R - $10,000)' alongside plain words.", "글로 길게 풀다 모호해지는 할인율·지연이자·비례 환불(pro-rata) 계산 규칙을 명확한 산식·표와 함께 쓴다.", "할인 기준이 총액인지 잔액인지, 반올림은 어느 자리에서 하는지 글 속에 빠뜨리지 않는다."),
W("불필요한 동의어 쌍 제거", "이중어", "단일", "Replace redundant doublets like 'null and void' or 'terms and conditions' with one precise word.", "null and void, indemnify and hold harmless 외에 습관적 동의어 중복(each and every, full and complete)을 정리한다.", "법적 특수 용어가 아닌 일반 중복어까지 관습이라며 그대로 쌓아 두지 않는다."),
W("부정의 범위(Scope of Negation)", "not", "스코프", "Clarify 'may not assign without consent' vs 'is not required to provide support'.", "must not(금지), need not/is not required to(의무 없음), may not(권한 없음 vs 가능성 부인)을 혼동 없이 고친다.", "'Provider may not deliver on Monday'가 '월요일에 못 낼 수도 있다'인지 '월요일 납품 금지'인지 애매하게 쓰지 않는다."),
W("정책 문서(Privacy/ToS) 해부", "ToS", "권리", "Distinguish broad data-license grants ('worldwide, perpetual, royalty-free') from narrow service use.", "실제 SaaS 이용약관·개인정보 처리방침에서 라이선스 범위, 데이터 보유·삭제 권리, 일방 변경 조항을 평문으로 요약한다.", "마케팅용 요약 문구만 읽고 본문의 광범위한 라이선스나 자동 동의 조항을 놓치지 않는다.", mode="read"),
W("원문 보존형 vs 전면 개작형", "수정폭", "선택", "Choose minimal surgical redlines for third-party paper, and structural rewrites for own templates.", "상대방 표준 계약서(수정 최소화 원칙)와 우리 측 표준 양식(전면 명확화)에 따라 수정 폭 전략을 구분한다.", "상대방 30쪽 계약서 전체 문체를 자기 스타일로 갈아엎어 협상을 마비시키지 않는다."),
W("듣기: 레드라인 리뷰 회의", "설명", "수정", "We narrowed Section 7.3 to direct damages only, matching the cap structure in 7.1.", "수정 전후 조항과 상대 법무 코멘트 2분을 듣고 핵심 쟁점 3가지의 수정 방향을 영어로 보고한다.", "기술적 문법 지적과 상업적 위험 변경을 같은 비중으로 뭉뚱그려 보고하지 않는다.", mode="listen"),
W("다중 조항 일괄 리팩터링", "정비", "통일", "Harmonize notice periods, currency formats, and capitalized terms across a 5-section extract.", "일부러 결함(불일치 용어·수동태·중의적 수식·과잉 shall) 10개를 심은 2쪽 계약 발췌문을 전면 리팩터링한다.", "고치기 전과 후의 의미가 의도치 않게 바뀌지 않았는지 조항별로 교차 확인한다."),
W("수정과 교정 점검", "정밀", "이유", "All 10 defects are resolved with change logs explaining the eliminated ambiguity.", "고친 2쪽 문서와 변경 이유 10줄, 2분 구두 수정 브리핑을 남긴다.", "새로운 지시 모호성이나 단복수 오류가 남아 있으면 점검을 통과하지 못한다."),
])
