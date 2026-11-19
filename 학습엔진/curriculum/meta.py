# -*- coding: utf-8 -*-
"""Top-level track metadata: destinations, scope limits, institutional standards, prerequisites, benchmarks, and daily hour templates."""

DEST = {
    "ma": (
        "5년(260주) 끝에 MAA CUPM(2015) · MIT OCW 학부·석사 기초 표준(18.01→18.02→18.06→18.100→18.102→18.600→18.701)에 따라 "
        "선형대수·실해석학·측도론·르베그 적분·확률공간·함수해석학 기초까지 도달한다. "
        "직관적 계산과 엄밀한 증명·반례를 함께 익히며, 선택공리가 개입하는 정리는 진술과 증명 스케치로 구분한다(Khan Academy → Axler/Strang → Abbott → Stein & Shakarchi → Kreyszig)."
    ),
    "al": (
        "7년(364주) 끝에 ACM/IEEE CS2023(Algorithmic Foundations) · MIT 6.006/6.046/6.854 · CLRS 4판 수준 알고리즘·계산복잡도의 핵심 정리를 증명하고 기술 노트로 남긴다. "
        "1년차 점근 표기·기본 정렬(병합·퀵·계수)과 자료구조에서 시작해 손 추적·구현과 불변식·정확성 증명을 나란히 훈련하며, 최악·분할상환·확률적·근사 보장의 트레이드오프를 비교한다."
    ),
    "en": (
        "7년(364주) 끝에 Council of Europe CEFR Companion Volume(2020: 수용·산출·상호작용·중재)과 Paul Nation의 Four Strands(입력·산출·언어학습·4/3/2 유창성)에 따라 "
        "일상·실무 소통(CEFR A1→B2)을 넘어 계약·협상 전문 목적 영어(ESP B2+→C1, 3단원 선택)와 논리적 명료 산문·장문 집필(C1+)에 도달한다."
    ),
    "sw": (
        "5년(260주) 끝에 IEEE SWEBOK v4(2024, 18개 지식영역) · MIT 6.031(명세·불변식) · Clean Code vs A Philosophy of Software Design · OWASP ASVS/STRIDE 보안 경계를 대조한 설계 노트를 완성하고, "
        "7년(364주) 끝에는 ISO/IEC 25010 품질 속성 · CMU SEI ATAM · DDIA · Google SRE(SLI/SLO·에러 버짓) · 진화적 아키텍처를 집대성한 ADR과 설계 핸드북을 남긴다."
    ),
}

LIMIT = {
    "ma": (
        "전일제 대학원 학위 논문 연구 이전까지의 표준 학부·석사 기초 교과 과정을 다룬다. "
        "계산 감각 없이 추상 공리부터 외우지 않도록 1~2년차에 고유값과 마스터 정리를 두지 않고, 3년차 첫 단계에 선형대수(벡터공간·고유값)를 두어 증명 다리를 놓은 뒤 실해석학과 측도론을 전개하며, 군·환·체는 함수해석 뒤에 배치한다."
    ),
    "al": (
        "단순 코딩 테스트 암기나 대회 순위가 아니라 CS2023 기준 알고리즘 설계 원리·엄밀한 복잡도 증명·사회적/자원 한계 인식을 목표로 한다. "
        "1년차에는 점근 표기 입문과 병합·퀵·계수 정렬을 손 추적으로 익히고, 마스터 정리는 수학(102주)에서 점화식을 배운 뒤(119주)에 연결하며, 고속 푸리에는 다항식 곱셈과 보간 원리까지 다룬다."
    ),
    "en": (
        "변호사 자격을 대체하는 법률 자문이 아니라, CEFR 2020 4대 소통 모드(수용·산출·상호작용·중재)를 훈련하는 언어·논증 과정이다. "
        "1년차에는 계약 영어를 다루지 않고 기초 발음·A2 소통을 다지며, 3단원 계약 영어는 실무 계약 독해가 필요한 학습자를 위한 전문 목적(ESP) 선택 트랙으로 구성된다."
    ),
    "sw": (
        "단일 프레임워크 문법 암기나 IDE 사용법 수업이 아니다. "
        "IEEE SWEBOK v4와 ACM/IEEE CS2023 SE 기준을 바탕으로 특정 설계 서적 하나를 교리처럼 외우지 않고, 명세·보안·테스트·SRE·아키텍처의 상반된 원칙과 품질 속성 트레이드오프를 기각 근거와 함께 판단하는 과정이다."
    ),
}

STANDARDS = {
    "ma": [
        "MAA CUPM Curriculum Guide (2015)",
        "MIT OCW (18.01 · 18.02 · 18.06 · 18.100A · 18.102 · 18.600 · 18.701)",
        "Khan Academy → Axler / Strang → Abbott → Stein & Shakarchi → Kreyszig",
    ],
    "al": [
        "ACM/IEEE-CS/AAAI CS2023 (Algorithmic Foundations, AL)",
        "MIT OCW (6.006 · 6.046 · 6.854)",
        "CLRS 4th ed. (Introduction to Algorithms)",
    ],
    "en": [
        "Council of Europe CEFR Companion Volume (2020: Reception · Production · Interaction · Mediation)",
        "Cambridge English Guided Learning Hours Benchmark",
        "Paul Nation Four Strands (25% Input · 25% Output · 25% Language Study · 25% Fluency / 4-3-2)",
    ],
    "sw": [
        "IEEE SWEBOK v4 (2024, 18 Knowledge Areas incl. Architecture · Security · Operations)",
        "ACM/IEEE-CS/AAAI CS2023 (Software Engineering, SE) · MIT 6.031",
        "ISO/IEC 25010 · CMU SEI ATAM · DORA/Accelerate · OWASP ASVS/STRIDE · Google SRE",
    ],
}

METHODOLOGY = {
    "ma": [
        "인출 연습(Dunlosky 2013): 매일 첫 10분 노트를 덮고 직전 핵심 계산·정의를 먼저 인출",
        "예제→점진적 소거(Worked Example → Faded Practice): 2일차에 규칙 주석 후 기호 변형 연습",
        "교차 판별 연습(Rohrer Interleaving): 5일차에 3주 전 주제와 섞어 문제 유형·정리 선택 판별",
        "적응형 분산 복습(Cepeda 2008 / FSRS): 4단계 인출 난이도 자기 평가 및 재학습 절감(Savings) 적용",
    ],
    "al": [
        "손 추적 우선(Trace Before Code): 코드 작성 전 작은 입력 위에서 불변식과 변수 변화를 수기로 추적",
        "정교화 질문과 반례(Elaborative Interrogation): 가정을 뺀 반례 입력으로 실패 경계를 확인",
        "교차 알고리즘 선택(Interleaving): 6일차에 3주 전 주제와 입력을 섞어 제약 조건만으로 해법 판별",
        "적응형 분산 복습: 1·3·7·16·35·70·180일 기반 4단계 난이도 조절 및 리치(Leech) 탐지",
    ],
    "en": [
        "Paul Nation Four Strands: 의미 중심 다독·다청(98% 이해율), 산출, 언어 집중, 4/3/2 유창성 균형",
        "CEFR 2020 4대 모드: 수용(듣기·읽기), 산출(말하기·쓰기), 상호작용, 중재(요약·설명 전환) 통합",
        "Nation 4/3/2 기법: 4일차 말하기에서 동일 내용을 4분→3분→2분(기초 2분→90초→60초) 압축 반복",
        "능동 인출과 교차 복습: 녹음 기반 자가 교정 및 3주 전 상황과 섞은 즉석 응답 훈련",
    ],
    "sw": [
        "상반된 거장 대조(Contrastive Case Analysis): 단일 교조 암기 대신 두 대안의 비용·인지 부하 비교",
        "ISO/IEC 25010 · ATAM 트레이드오프 분석: 5일차에 개선된 품질 축과 양보한 품질 축을 정량 명시",
        "교차 설계 판별(Interleaving): 6일차에 3주 전 설계 원칙과 충돌할 때 지배적 제약 우선순위 판단",
        "명세·불변식·보안 우선(MIT 6.031 · SWEBOK v4): 표현 불변식(RI)·신뢰 경계·에러 버짓 검증",
    ],
}

PREREQUISITES = {
    "al": [
        {"week": 119, "reqTrack": "ma", "reqWeek": 102, "topic": "마스터 정리 및 점화식"},
        {"week": 126, "reqTrack": "ma", "reqWeek": 64, "topic": "복소수 극형식과 회전(FFT 기초)"},
        {"week": 128, "reqTrack": "ma", "reqWeek": 112, "topic": "행렬 표현과 행렬식"},
        {"week": 165, "reqTrack": "ma", "reqWeek": 44, "topic": "수학적 귀납법 형식"},
        {"week": 230, "reqTrack": "ma", "reqWeek": 173, "topic": "기댓값의 선형성"},
        {"week": 235, "reqTrack": "ma", "reqWeek": 117, "topic": "선형대수 벡터공간·행렬 종합"},
        {"week": 248, "reqTrack": "ma", "reqWeek": 173, "topic": "기댓값의 선형성과 분산"},
        {"week": 249, "reqTrack": "ma", "reqWeek": 175, "topic": "마르코프 부등식"},
        {"week": 250, "reqTrack": "ma", "reqWeek": 176, "topic": "체비쇼프 부등식·큰 수의 법칙"},
        {"week": 265, "reqTrack": "ma", "reqWeek": 255, "topic": "다항식 나눗셈·나머지 정리"},
        {"week": 266, "reqTrack": "ma", "reqWeek": 256, "topic": "체와 유한체"},
    ],
    "sw": [
        {"week": 209, "reqTrack": "al", "reqWeek": 72, "topic": "위상 정렬과 비순환 방향 그래프(DAG)"},
    ],
}

UNIT_BENCHMARKS = {
    "en": {
        "u1": {
            "level": "CEFR A1 → A2+",
            "standard": "Cambridge A2 Key (약 180~200시간)",
            "bloom": "기억·이해·기초 적용",
            "diagnostic": [
                "한국어 모음·자음과 영어 음소·강세(schwa 포함)를 구분해 들을 수 있다.",
                "현재·과거·미래·현실 조건(if)으로 일상과 주간 계획을 90초~4분 말할 수 있다.",
                "목적과 기한이 분명한 정중한 요청·거절·일정 제안 이메일을 작성할 수 있다.",
            ],
        },
        "u2": {
            "level": "CEFR B1 → B2",
            "standard": "Cambridge B2 First (누적 약 500~600시간)",
            "bloom": "적용·분석",
            "diagnostic": [
                "현재완료·가정법·분사구문을 사용해 회의에서 즉석 2분 의견을 구조화해 말할 수 있다.",
                "차트 추세와 상관·인과를 구분하고 예상 반론을 수용해 1쪽 BLUF 보고서를 쓸 수 있다.",
                "회의·브리핑 오디오에서 핵심 수치와 결정 사항(Owner/Deadline)을 중재 요약할 수 있다.",
            ],
        },
        "u3": {
            "level": "ESP B2+ → C1 (전문 선택)",
            "standard": "SEC EDGAR · Ken Adams 계약 작성 규범",
            "bloom": "분석·평가",
            "diagnostic": [
                "영문 계약서에서 의무(shall/must)·재량(may)·조건·예외(notwithstanding)를 구분한다.",
                "진술·보장, 면책(Indemnity), 책임 상한(Cap), IP·해지 조항의 위험 분배를 분석한다.",
                "모호한 조항을 레드라인(Redline)으로 고치고 이슈 리스트 기반 8~10분 협상을 진행한다.",
            ],
        },
        "u4": {
            "level": "CEFR C1",
            "standard": "Cambridge C1 Advanced · Joseph Williams <Style>",
            "bloom": "평가·정교화",
            "diagnostic": [
                "행위자 주어와 Old-to-New 정보 흐름으로 명사화 남용과 모호한 수식을 교정한다.",
                "독자와 목적에 맞춰 화자 거리·레지스터(Register)와 구체적 사례 장면을 통제한다.",
                "주장·근거·연결고리(Warrant)·반론수용·한계명시의 5요소 600단어 논증을 구사한다.",
            ],
        },
        "u5": {
            "level": "CEFR C1+",
            "standard": "Zinsser · Orwell · C1+ 장문 포트폴리오",
            "bloom": "창조·비평",
            "diagnostic": [
                "역개요(Reverse Outline)로 24시간 지난 초고를 거시 구조부터 미시 리듬까지 수술한다.",
                "1,500~2,500단어 장문 설명문·논증문·서사 논픽션 3개 장르를 통합 설계·집필한다.",
                "대표작 3편 선집과 퇴고 전후 로그를 대본 없이 10분 구술 발표 및 Q&A로 방어한다.",
            ],
        },
    },
    "al": {
        "u1": {
            "level": "CS2023 AL 기초 · MIT 6.006 전반",
            "standard": "ACM/IEEE CS2023 Foundations",
            "bloom": "이해·적용(구현)",
            "diagnostic": [
                "이분 탐색(하한·상한·단조성)과 정렬(삽입·병합·퀵·계수)을 손 추적 후 구현할 수 있다.",
                "점근 표기(O, Ω, Θ)로 정렬·탐색의 성장 차수와 추가 메모리 차이를 판별할 수 있다.",
                "스택·큐·이진 검색 트리·해시(체이닝·개방주소법)·힙·AVL/B-트리 원리를 설명할 수 있다.",
            ],
        },
        "u2": {
            "level": "MIT 6.006 후반 · CLRS 중급",
            "standard": "CS2023 Graph & Optimization",
            "bloom": "적용·분석",
            "diagnostic": [
                "DFS·BFS·위상 정렬·백트래킹으로 그래프 연결성과 경로 복원을 구현할 수 있다.",
                "그리디 반례를 찾고 다익스트라·벨만-포드·플로이드-워셜·MST(크루스칼/프림)를 선택한다.",
                "동적 계획법(DP)의 상태와 점화식 의존 순서를 정의해 배낭·LCS·트리/구간 DP를 푼다.",
            ],
        },
        "u3": {
            "level": "CLRS 분할정복·구간·문자열",
            "standard": "MIT 6.006 / 6.046 교량",
            "bloom": "분석·구현",
            "diagnostic": [
                "마스터 정리 3가지 경우와 정규 조건, 적용 불가 점화식을 판정하고 FFT 계수-점값 왕복을 안다.",
                "세그먼트 트리·펜윅 트리·레이지 전파의 시간/공간과 적용 조건을 구분해 구현한다.",
                "트라이·KMP 실패 함수·라빈-카프 롤링 해시·Z 배열을 손 추적 후 구현할 수 있다.",
            ],
        },
        "u4": {
            "level": "MIT 6.046 정확성·유량·상환",
            "standard": "CS2023 Formal Analysis",
            "bloom": "분석·증명",
            "diagnostic": [
                "루프 불변식(초기·유지·종료)으로 삽입 정렬·이분 탐색·BFS·다익스트라 정확성을 증명한다.",
                "포드-풀커슨/에드몬즈-카프 최대 유량-최소 컷 정리와 이분 매칭 환원을 증명·구현한다.",
                "총계·회계·잠재 함수로 분할상환 비용을 분석하고 결정 나무 비교 정렬 하한을 증명한다.",
            ],
        },
        "u5": {
            "level": "대학원 기초 · MIT 6.854",
            "standard": "CS2023 Complexity & Randomized",
            "bloom": "평가·증명",
            "diagnostic": [
                "선형계획(LP)과 약한 쌍대성, 체르노프·호프딩 꼬리 부등식과 확률 증폭 원리를 설명한다.",
                "P, NP, NP-완전과 3SAT→독립집합/정점덮개 다항시간 환원 방향을 정확히 증명한다.",
                "정점 덮개·집합 덮개·배낭 FPTAS·원-쌍대 근사 비율 보장을 유도·비교할 수 있다.",
            ],
        },
        "u6": {
            "level": "CS2023 Synthesis & Society",
            "standard": "연구 독해·기술 노트 종합",
            "bloom": "창조·평가",
            "diagnostic": [
                "논문 정리 하나의 호출 가정·결론·생략 범위를 고정하고 빈칸 없는 증명 초고를 작성한다.",
                "최악 입력·공정성/편향·자원/에너지 비용 한계(Algorithms and Society)를 명시한다.",
                "독자 대상 기술 노트로 퇴고하고 대본 없이 10분 구술 설명과 가정 질문을 방어한다.",
            ],
        },
    },
    "ma": {
        "u1": {
            "level": "초중등 연산·대수·기초 논리·기하",
            "standard": "Khan Academy · Transition to Proof",
            "bloom": "기억·이해·기초 증명",
            "diagnostic": [
                "사칙·분수·소수·일차/연립/이차방정식과 지수·로그 계산을 검산하며 푼다.",
                "명제·대우·반례·직접 증명·귀류법·수학적 귀납법으로 짧은 수열/정수 명제를 증명한다.",
                "단위원 삼각비·호도법·평면벡터 내적(u·v=0 직교)·복소수 극형식 회전을 계산할 수 있다.",
            ],
        },
        "u2": {
            "level": "MIT 18.01 · 18.02 · 이산 기초",
            "standard": "MAA CUPM Lower-Division Calculus",
            "bloom": "적용·계산 직관",
            "diagnostic": [
                "도함수·치환/부분적분·리만 합·분리형 미분방정식 계산과 검산을 수행할 수 있다.",
                "편미분·그래디언트(∇f)·다중 반복적분·다변수 연쇄법칙의 기하적 의미를 계산한다.",
                "순열·조합·조건부 확률·베이즈·기댓값·분산과 빅오(O)·점화식·마스터 정리를 판정한다.",
            ],
        },
        "u3": {
            "level": "MIT 18.06 · 18.100A",
            "standard": "MAA CUPM Core (Axler · Abbott)",
            "bloom": "분석·증명",
            "diagnostic": [
                "벡터공간·가우스 소거법·기저·계수-퇴화차수·행렬식·고유값·대칭행렬 직교대각화를 증명/계산한다.",
                "실수 완비성·ε-N·ε-δ 연속·중간값·최대최소·평균값·리만 적분 기본정리를 증명한다.",
                "점별/균등수렴의 차이와 거리공간 열린/닫힌/완비/바나흐 고정점/컴팩트를 증명·스케치한다.",
            ],
        },
        "u4": {
            "level": "MIT 18.600 · Real Analysis 측도",
            "standard": "Stein & Shakarchi 측도·확률 통합",
            "bloom": "분석·증명",
            "diagnostic": [
                "확률 공리에서 기댓값 선형성·마르코프·체비쇼프·약한 법칙·보렐-칸텔리를 증명한다.",
                "σ-대수·외측도·카라테오도리·르베그 측도와 단순/음이 아닌 함수 적분을 구성한다.",
                "단조수렴·파투·지배수렴 정리 및 콜모고로프 확률공간·강한 법칙·CLT의 가정을 구분한다.",
            ],
        },
        "u5": {
            "level": "MIT 18.102 · 18.701 입문",
            "standard": "Kreyszig 함수해석 · 학부 대수",
            "bloom": "평가·종합",
            "diagnostic": [
                "노름·바나흐 공간과 균등유계·열린사상·한-바나흐 정리의 적용 조건과 한계를 구분한다.",
                "힐베르트 공간(내적·코시-슈바르츠·정사영·그람-슈미트·L2)과 작용소 스펙트럼을 이해한다.",
                "군·부분군·라그랑주·환·아이디얼·다항식 나눗셈·체 구조를 해석학과 분리해 설명한다.",
            ],
        },
    },
    "sw": {
        "u1": {
            "level": "SWEBOK KA 1 · 5 · 8 · MIT 6.031",
            "standard": "IEEE SWEBOK v4 기초 공학 & DORA",
            "bloom": "이해·적용",
            "diagnostic": [
                "변경 이유별 커밋 응집도와 Trunk-Based/브랜치 통합, API·스키마 하위 호환을 설계한다.",
                "사전·사후조건, ADT, 표현 불변식(RI), 추상화 함수(AF), ISO 25010 품질 시나리오를 명세한다.",
                "동치분할·경계값·변이 테스트, git bisect, CI 게이트, DORA 지표와 무중단 롤백을 적용한다.",
            ],
        },
        "u2": {
            "level": "Clean Code vs APOSD 코드 설계",
            "standard": "SWEBOK KA 3 · 12 (Construction & Quality)",
            "bloom": "분석·평가",
            "diagnostic": [
                "변경 증폭·인지 부하·미지의 미지로 복잡도를 진단하고 깊은 모듈로 정보를 은닉한다.",
                "작은 함수 분할 vs 깊은 모듈 통합의 Expression Problem 비용을 같은 요구사항에서 비교한다.",
                "인터페이스 주석, 오류 정의 제거 vs 경계 드러내기, 고전파/목파·계약 테스트로 리뷰한다.",
            ],
        },
        "u3": {
            "level": "SWEBOK KA 2 · 3 · 13 (보안·ATAM)",
            "standard": "OWASP ASVS · STRIDE · ATAM · Parnas",
            "bloom": "분석·설계·평가",
            "diagnostic": [
                "변하는 행동(조건문/전략/상태/테이블), 조립(DI), 이벤트, 패턴 채택·해체(Wrong Abstraction)를 판단한다.",
                "정보 은닉, 단방향 의존(DAG/DIP), 트랜잭션 vs 결과적 일관성(Outbox/보상) 경계를 설계한다.",
                "STRIDE 위협 모델링, 신뢰 경계, IDOR 인가, 키 순환과 ISO 25010/ATAM 설계 노트를 작성한다.",
            ],
        },
        "u4": {
            "level": "분산 시스템 · SRE · 진화적 아키텍처",
            "standard": "SWEBOK KA 2 · 6 (Architecture & Operations) · DDIA · SRE",
            "bloom": "평가·설계",
            "diagnostic": [
                "수평 계층 vs 수직 슬라이스, 풍부한 도메인 모델 vs 데이터 모델·샤딩 간극을 비교한다.",
                "비동기 멱등성·배압·사가, 공유 가변 vs 불변·낙관적/비관적 동시성 경계를 설계한다.",
                "타임아웃·지터·서킷 브레이커·벌크헤드·SLI/SLO 에러 버짓·꼬리 지연·진화적 아키텍처를 설계한다.",
            ],
        },
        "u5": {
            "level": "7년 종합 카타 · ADR 핸드북",
            "standard": "4거장 다관점 비평 · Michael Nygard ADR",
            "bloom": "창조·종합 평가",
            "diagnostic": [
                "6대 도메인 카타를 마틴·아우스터하우트·파울러/벡·클레프만 4관점으로 교차 비평한다.",
                "지배적 제약에 따라 충돌하는 원칙의 우선순위를 정하고 거절 목록과 반전 조건을 남긴다.",
                "표준 ADR 모음과 1페이지 개인 설계 핸드북을 백지 인출 및 10분 구술 설명으로 방어한다.",
            ],
        },
    },
}

HOUR = {
    "ma": [
        ["10분", "첫 주에는 오늘 예제의 첫 단계 결과만 적는다. 둘째 주부터는 지난주 핵심 계산·정의를 노트를 덮고 인출한다."],
        ["20분", "핵심 정의·직관을 읽고(2일차는 예제→점진적 소거 25분), 실패 조건과 반례를 확인한다."],
        ["20분", "해설을 가리고 풀며, 5일차에는 3주 전 주제와 섞은 교차 판별 연습(Interleaving)으로 정리 선택을 훈련한다."],
        ["10분", "핵심을 한 문장으로 말로 요약하고, 막힌 지점과 실수 유형을 기록해 다음 주 복습 카드로 잇는다."],
    ],
    "al": [
        ["10분", "첫 주에는 오늘 예제를 코드 없이 손으로 따라간다. 둘째 주부터는 지난주 가정·결론을 노트를 덮고 먼저 복기한다."],
        ["20분", "오늘의 주장·반례·비용 근거를 작은 입력 위에서 손으로 추적한다(2일차 25분, 3일차 구현/증명 40분 집중 블록)."],
        ["20분", "가정을 뺀 반례 입력을 실험하거나, 6일차에 3주 전 주제와 입력을 섞어 조건만으로 알고리즘을 판별(Interleaving)한다."],
        ["10분", "주장·고친 줄·시간·공간 복잡도 근거를 한 문장으로 줄여 말하고 다음 주 복기 칸을 남긴다."],
    ],
    "en": [
        ["10분", "이번 주 기준 문장을 소리 내어 말한다. 지난주 막혔던 문장 둘을 먼저 인출하며 복습한다."],
        ["20분", "언어 집중·수용(CEFR): 목표 표현과 문장 구조를 원문·오디오로 듣고 모호한 대조 문장과 비교한다."],
        ["20분", "산출·유창성(Four Strands): 대본 없이 4/3/2 압축 말하기나 중재 글쓰기·다독(98% 이해율)을 수행한다."],
        ["10분", "막혔던 문장을 고쳐 적고 새로 건진 핵심 표현 5개만 영어 예문 카드에 남긴다."],
    ],
    "sw": [
        ["10분", "첫 주에는 최근 변경에서 첫 대상 파일·줄을 적는다. 둘째 주부터는 지난주 설계 원칙과 트레이드오프를 노트를 덮고 말한다."],
        ["20분", "상반된 설계 관점이나 반례 실패 패턴을 사례 위에서 대조한다(2일차 25분, 3일차 설계·구현 40분 집중 블록)."],
        ["20분", "ISO/IEC 25010 품질 속성·변경 비용을 대입하고, 6일차에는 3주 전 원칙과 충돌할 때의 교차 판별(Interleaving)을 훈련한다."],
        ["10분", "핵심 기준과 채택·거절 근거를 한두 문장으로 요약해 말로 설명하고 다음 날에 잇는다."],
    ],
}

TRACK_BASE = {
    "en": {
        "id": "en",
        "name": "영어",
        "color": "#0e5e56",
        "hourTitle": "수용·산출·유창성을 균형 있게 남긴다",
        "hour": HOUR["en"],
        "destination": DEST["en"],
        "limit": LIMIT["en"],
        "standards": STANDARDS["en"],
        "methodology": METHODOLOGY["en"],
        "after": "매주 98% 이해율 다독·청취 1편과 긴 글 퇴고·구술 요약 1편으로 CEFR C1+ 감각을 유지한다.",
        "soft": "#e3f2ef",
        "confirm": "record",
    },
    "al": {
        "id": "al",
        "name": "알고리즘",
        "color": "#8d3d16",
        "hourTitle": "손 추적과 불변식 뒤 코드",
        "hour": HOUR["al"],
        "destination": DEST["al"],
        "limit": LIMIT["al"],
        "standards": STANDARDS["al"],
        "methodology": METHODOLOGY["al"],
        "after": "매주 노트에 적은 정리 하나를 코드·반례 또는 증명으로 다시 확인한다.",
        "soft": "#f8ebe3",
        "confirm": "why",
    },
    "ma": {
        "id": "ma",
        "name": "수학",
        "color": "#2a3878",
        "hourTitle": "정의 인출 다음 교차 문제·증명",
        "hour": HOUR["ma"],
        "destination": DEST["ma"],
        "limit": LIMIT["ma"],
        "standards": STANDARDS["ma"],
        "methodology": METHODOLOGY["ma"],
        "after": "매주 정의 하나와 증명 하나를 백지에 다시 쓰고 반례를 대조한다.",
        "soft": "#e7e9f6",
        "confirm": "why",
    },
    "sw": {
        "id": "sw",
        "name": "소프트웨어",
        "color": "#245c3a",
        "hourTitle": "품질 속성·상반된 설계를 대조해 판단하다",
        "hour": HOUR["sw"],
        "destination": DEST["sw"],
        "limit": LIMIT["sw"],
        "standards": STANDARDS["sw"],
        "methodology": METHODOLOGY["sw"],
        "after": "새로운 시스템을 설계할 때마다 설계 핸드북과 ADR을 펼쳐 품질 속성과 대안을 비교하고 분기마다 갱신한다.",
        "soft": "#e7f0ea",
        "confirm": "why",
    },
}
