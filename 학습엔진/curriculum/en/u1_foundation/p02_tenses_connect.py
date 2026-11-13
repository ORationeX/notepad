# -*- coding: utf-8 -*-
"""Phase 02: 시제 확장과 연결 (weeks 14–26)."""
from curriculum.common import E, phase
from curriculum.en.resources import R_Y1 as R

PHASE = phase("시제 확장과 연결", 14, 26, "일상", "연결", "과거진행, 빈도·수량, 비교·최상급, 현실 조건과 일상 질문으로 여섯 문장짜리 이야기를 말한다.", R, [
E("과거진행과 배경", "was -ing", "when", "I was walking home when it started to rain.", "배경이 되는 진행 중인 동작은 was/were -ing로, 그사이에 일어난 사건은 단순과거로 쓴다.", "I walked home when it was starting to rain처럼 배경과 사건 시제를 뒤집지 않는다.", "어제 사건 하나의 배경과 돌발 상황을 6문장으로 녹음한다.", "when으로 이어진 배경+사건 4문장을 쓴다.", "core"),
E("will vs going to 깊이", "계획", "즉흥", "I am going to visit Busan next week, so I will book the train now.", "이미 세운 계획은 be going to, 말하는 순간의 결정·약속·제안은 will로 구분한다.", "I will visit Busan next month처럼 오래전 잡은 일정을 즉석 결정처럼 말하지 않는다.", "다음 주 확정 계획 3개와 지금 떠오른 즉흥 결정 3개를 녹음한다.", "두 시제를 대조한 4문장을 쓴다.", "core"),
E("셀 수 없는 명사와 수량", "much", "many", "We do not have much time, but we have many questions.", "복수 명사는 many/a few, 불가산 명사는 much/a little과 함께 쓴다. information, advice는 복수형으로 쓰지 않는다.", "many informations나 an advice처럼 불가산 명사에 복수 -s나 부정관사 a를 붙이지 않는다.", "장보기·회의 준비물 8개를 수량 표현과 함께 말한다.", "가산·불가산 명사 6쌍을 바른 수량사와 함께 쓴다.", "core"),
E("부정대명사", "some", "any", "Do you have any questions? Yes, I have some notes.", "긍정문과 권유에는 some, 부정문과 일반 질문에는 any, 전체 부정에는 no를 구분한다.", "I don't have some time처럼 부정문 안에 긍정용 some을 그대로 쓰지 않는다.", "냉장고와 책상 위 물건의 유무를 묻고 답하는 6쌍을 녹음한다.", "some, any, no를 쓴 6문장을 쓴다.", "core"),
E("위치·이동 전치사", "into", "through", "She walked out of the station and across the bridge.", "정지 위치(in, on, at)와 이동 방향(into, out of, across, through)을 그림으로 구분한다.", "She walked in the room으로 '방 안으로 걸어 들어갔다'는 이동을 표현하지 않는다.", "출근·이동 경로 6단계를 이동 전치사로 말한다.", "같은 경로를 5문장으로 쓴다.", "core"),
E("시간의 전치사와 기간", "during", "for", "I stayed quiet during the meeting for twenty minutes.", "for 뒤에는 길이(20분), during 뒤에는 사건 명사(회의), while 뒤에는 주어+동사 절이 온다.", "during 20 minutes나 while the meeting처럼 뒤 형태가 어긋나지 않게 한다.", "지난주 일정 6문장을 for, during, while로 구분해 말한다.", "세 표현이 모두 들어간 4문장을 쓴다.", "core"),
E("이유와 양보", "because", "although", "Although it rained, we finished the walk on time.", "원인은 because/so, 예상과 다른 양보는 although/but으로 잇되 한 문장에 둘을 겹치지 않는다.", "Although it rained, but we walked처럼 한 문장에 종속과 등위 접속사를 동시에 쓰지 않는다.", "예상과 달랐던 어제의 일 4가지를 말한다.", "although 2문장과 because 2문장을 쓴다.", "core"),
E("현실 조건과 시간절", "if", "when", "If the bus is late, I will take the subway.", "실제로 일어날 수 있는 조건의 if절과 미래 시간절(when, before, after) 안에서는 현재시제로 미래를 대신한다.", "If the bus will be late처럼 조건·시간절 안에 will을 넣지 않는다.", "내일 날씨와 일정 변화에 따른 대안 6문장을 말한다.", "if 2문장과 when/before 2문장을 쓴다.", "core"),
E("동등 비교와 강조", "as...as", "much", "Today's meeting was much shorter than yesterday's.", "같은 정도는 as + 원급 + as, 비교급 강조는 very가 아니라 much/a lot/far를 쓴다.", "very shorter나 as shorter as처럼 강조 부사와 원급 형식을 섞지 않는다.", "두 도구나 두 도시를 비교급 강조와 as...as로 6문장 말한다.", "4문장 비교 메모를 쓴다.", "core"),
E("듣기: 일상 대화 핵심", "받아쓰기", "요지", "Yesterday I missed the early train, so I arrived ten minutes late.", "원어민 속도 1분 일상 대화를 듣고 핵심 사건(언제·무엇·왜)을 받아쓴 뒤 따라 말한다.", "모든 단어를 한 번에 다 적으려다 뒷문장을 통째로 놓치지 않는다.", "일상 오디오를 듣고 요지 6문장을 대본 없이 말한다.", "받아쓴 문장 중 놓친 덩어리 4개를 고쳐 적는다.", "listen"),
E("과거 경험 여섯 문장", "yesterday", "흐름", "Yesterday I woke up late, skipped breakfast, and caught the 8:15 train.", "과거 이야기는 시작-문제-해결-결과 순으로 연결하며 시제를 과거로 고정한다.", "Yesterday I wake up처럼 과거 시점 안에 현재형 동사를 섞지 않는다.", "어제 겪은 작은 문제 하나를 대본 없이 여섯 문장 이상 말한다.", "그 이야기를 6문장으로 쓰고 동사 시제를 점검한다.", "core"),
E("주간 계획 90초", "일정", "이유", "Next week I am going to finish the draft on Tuesday because Wednesday is busy.", "예정된 일정(going to), 이유(because), 조건 대안(if)을 엮어 말한다.", "할 일 목록만 단어처럼 나열하고 이유와 순서를 빼먹지 않는다.", "다음 주 핵심 일정 4가지를 이유·대안과 함께 녹음한다.", "일정 메모의 첫 문장과 마무리 문장을 쓴다.", "core"),
E("문장 연결 점검", "질문", "연결", "Why were you late? Because the train stopped while I was reading.", "질문, 부정, 과거진행, 접속사를 조합해 묻고 답할 수 있다.", "대답에서 동사 시제나 접속사 뒤 주어를 빠뜨리지 않는다.", "질문 4개에 각각 두 문장 이상으로 답해 녹음한다.", "오류가 있던 4문장을 바르게 고쳐 적는다.", "core"),
])
