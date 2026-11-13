# -*- coding: utf-8 -*-
"""Phase 13: 복잡 조항과 정의 (weeks 157–169)."""
from curriculum.common import phase
from curriculum.en.resources import DRAFT
from curriculum.en.templates import bind_writer

W = bind_writer("복잡 조항과 정의")

PHASE = phase("복잡 조항과 정의", 157, 169, "협상", "정밀 독해", "실제 영문 계약의 다중 교차 참조, 중첩 예외(carve-out), 수식 범위 모호성을 정밀 해부한다.", DRAFT, [
W("긴 문장 구문 해부", "주어-동사", "핵심", "Subject to Section 4, Provider shall, upon written request, refund prepaid unused fees.", "50~100단어 문장에서 조건절·예외절·삽입구를 괄호로 걷어내고 핵심 주어+조동사+목적어 뼈대를 추출한다.", "삽입된 조건절 안의 명사를 문장의 진짜 주어나 주절 의무로 착각하지 않는다.", mode="read"),
W("단서·예외 계층(Notwithstanding)", "우선", "예외", "Notwithstanding Section 8.1, nothing limits liability for gross negligence.", "provided that(제한 조건), subject to(하위 종속), notwithstanding(상위 우선)이 겹칠 때 어느 조항이 이기는지 그래프를 그린다.", "두 조항이 서로를 notwithstanding으로 참조해 순환 충돌이 나는 함정을 놓치지 않는다."),
W("수식 모호성(Syntactic Ambiguity)", "수식", "분리", "Rewrite 'charitable institutions and schools that are exempt' into unambiguous bullets.", "A and B + 수식어(that ...), 형용사 + A and B, 또는 A or B가 여러 명사를 동시에 꾸밀 때 발생하는 중의성을 글머리 기호로 해체한다.", "문장 뜻이 두 가지로 읽히는데 관성적으로 한 뜻만 가정하고 넘어가지 않는다."),
W("and/or와 나열 모호성", "and/or", "열거", "Replace 'A and/or B' with 'A, B, or both'; specify whether lists are conjunctive or disjunctive.", "and, or, and/or, including without limitation, ejusdem generis(동종 제한 해석) 함정을 점검하고 목록을 정확히 고친다.", "세금이나 손해 목록 끝에 'or other fees'를 넣으면서 앞 항목과 성격이 다른 항목이 빠지지 않게 한다."),
W("시간과 숫자 수식 경계", "경계", "이상·이하", "Replace 'within 30 days' and 'less than $500' with exact inclusive/exclusive boundaries.", "more than vs at least, prior to vs on or before, between A and B의 경계값 포함 여부를 수학적 부등호로 검증한다.", "만료일 당일이 포함되는지 빠지는지(before vs on or before) 모호한 경계를 남기지 않는다."),
W("정의 연쇄와 숨은 역전", "연쇄", "치환", "Substitute every Capitalized Term with its Section 1 definition to test for hidden obligations.", "정의 A가 정의 B를, B가 다시 본문 예외를 가리킬 때 대문자 용어 자리에 원래 정의 문구를 대입(Substitution)해 숨은 효과를 확인한다.", "단어의 일상적 사전 뜻으로 조항을 읽다가 정의 조항의 'includes/excludes'에 당하지 않는다."),
W("긴 계약서 구조 지도(Map)", "교차", "추적", "Map all cross-references across Payment, Termination, Liability, and IP in a 10-page MSA.", "10쪽 이상의 공개 MSA/라이선스 계약에서 정의·본문·첨부 간 교차 참조 화살표를 그려 누락·고아 참조를 찾는다.", "조항 번호 하나만 읽고 그 조항이 참조하는 다른 섹션이나 예외 표를 펼쳐 보지 않는다.", mode="read"),
W("불일치·누락 조항 감사", "감사", "모순", "Section 5.2 references Section 14.3, which does not exist; SOW says 15 days while MSA says 30.", "실제 또는 모의 복합 계약에서 조항 간 날짜 모순, 정의 누락, 미정의 대문자 용어, 죽은 교차 참조를 찾아낸다.", "표나 부록(Exhibit)의 숫자와 본문 텍스트의 숫자를 대조하지 않고 넘어가지 않는다."),
W("문어체·고어(Legalese) 평문화", "번역", "평이", "Replace 'heretofore, witnesseth, therein, same' with plain, precise English.", "hereinafter, thereof, witnesseth, aforesaid 같은 불필요한 법률 고어를 지시 대상 명사로 치환해 명료도를 높인다.", "명사 중복이 무서워 said, such, same으로 지칭하다가 도리어 지시 대상이 불분명해지지 않게 한다."),
W("단락 내 나열 표(Tabulation)", "목록", "들여쓰기", "Break a 90-word run-on obligation into an introductory stem and (a), (b), (c) clauses.", "세 가지 이상 조건이나 의무를 담은 긴 한 문장을 공통 도입부(stem)와 병렬 (a)(b)(c) 목록으로 재구성한다.", "목록 (a)는 동사로, (b)는 명사로 시작하는 병렬 구조 파괴(Parallelism fault)를 만들지 않는다."),
W("듣기: 복합 조항 구술 해부", "요약", "조건", "Section 10 applies only if notice is delivered within five days after discovery.", "복잡한 단서 조항과 예외 2개가 걸린 설명을 듣고, '원칙-조건-예외-우선순위' 네 칸으로 정확히 요약한다.", "예외의 예외(unless... except...)를 듣고 부정 방향을 반대로 뒤집어 이해하지 않는다.", mode="listen"),
W("모의 감사 질문서 작성", "질문", "공백", "Does 'Affiliate' in Section 3.1 include future subsidiaries acquired after the Effective Date?", "감사를 통해 발견한 모순·공백·중의성 6가지에 대해 법무/상대측에 보낼 정밀 확인 질문서를 작성한다.", "질문에 자신의 자의적 추측 답을 미리 적어 두지 않고 문서의 공백을 정확히 짚는다."),
W("복잡 조항 점검", "치환", "감사", "All ambiguous modifiers and conflicting cross-references are decomposed into unambiguous clauses.", "미지의 3쪽 발췌 계약에서 긴 문장 2개 구문 해부 + 정의 대입 + 모호성 4곳 수정 + 질문 5개를 40분 내 완수한다.", "예외 절 하나라도 빠뜨리거나 수식 범위가 둘로 남으면 점검 통과가 아니다."),
])
