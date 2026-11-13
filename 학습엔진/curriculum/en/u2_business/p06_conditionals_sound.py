# -*- coding: utf-8 -*-
"""Phase 06: 가정과 소리 (weeks 66–78)."""
from curriculum.common import phase
from curriculum.en.resources import SOUND
from curriculum.en.templates import bind_writer

W = bind_writer("가정과 소리")

PHASE = phase("가정과 소리", 66, 78, "설명", "확장", "가정법, 과거완료, 분사구문, 동명사/부정사, 완료 조동사(B1–B2)를 말하기와 듣기에 통합한다.", SOUND, [
W("과거 가정", "if", "would", "If I had more time, I would audit the entire report.", "if 절은 과거형, 결과는 would다. 지금 사실과 반대다.", "If I would have time는 if 안에 would를 넣은 형태다."),
W("먼 과거 가정", "had", "would have", "If I had known earlier, I would have stayed until five.", "had p.p.와 would have p.p.는 이미 지난 일과 반대다.", "If I knew earlier, I would have stayed는 두 시제를 섞는다."),
W("과거완료와 순서", "had p.p.", "before", "By the time the client arrived, we had already fixed the draft.", "과거의 한 시점보다 먼저 끝난 사건은 had + 과거분사로 시간 순서를 고정한다.", "When the client arrived, we already fixed는 먼저 일어난 완료가 드러나지 않는다."),
W("조동사 과거 추측", "must have", "should have", "She must have missed the email; we should have called her.", "과거 일의 강한 추측은 must have p.p., 후회·미이행 조언은 should have p.p.로 구분한다.", "She must missed it처럼 조동사 뒤에 동사원형 없이 과거형을 바로 붙이지 않는다."),
W("동명사와 부정사", "-ing", "to V", "I stopped checking the log to answer the urgent call.", "enjoy/avoid/finish 뒤는 -ing, decide/agree/refuse 뒤는 to부정사이며 stop·remember·try는 둘의 뜻이 갈린다.", "I stopped to check it을 '확인하는 것을 멈췄다'로 오독하거나 avoid to meet처럼 동사 짝을 틀리지 않는다."),
W("분사구문 축약", "-ing", "-ed", "Reviewed by the lead, the memo was ready for release.", "주어가 같을 때 부사절을 능동(-ing)과 수동(-ed) 분사구문으로 압축하며 두 절의 주어를 일치시킨다.", "Walking into the room, the report fell on the desk처럼 분사의 주어가 문장 주어와 어긋나는 현수분사를 쓰지 않는다."),
W("unless와 even if", "조건", "양보", "Unless you confirm by noon, we will pause; even if it rains, we will ship.", "unless는 'if not'(예외 조건), even if는 '~하더라도'(비조건 양보)로 구분한다.", "Unless you will reply처럼 unless 안에 will을 넣거나 unless와 even if를 혼동하지 않는다."),
W("wish와 가정", "아쉬움", "과거", "I wish I had checked the attachment before sending the mail.", "현재 반대는 wish + 과거형, 지난 후회는 wish + had p.p.를 쓴다.", "I wish I have the file today는 현재형을 그대로 둔 것이다."),
W("대조와 양보 접속", "despite", "although", "Despite the delay, the team delivered on Friday.", "although/even though 뒤에는 절(주어+동사), despite/in spite of 뒤에는 명사구만 온다.", "Despite it rained처럼 despite 뒤에 주어+동사 절을 바로 붙이지 않는다."),
W("듣기: 뉴스·팟캐스트 요약", "받아쓰기", "요지", "Although costs rose sharply, the group maintained its target margin.", "3분 원어민 오디오(BBC 6 Minute English)에서 핵심 주장 1개와 근거 2개를 듣고 받아쓴다.", "모르는 단어 1개에서 멈춰 전체 논지 흐름을 놓치지 않는다.", mode="listen"),
W("정보 강세와 억양", "대조", "강세", "I sent the REVISED contract, not the original draft.", "대조되는 수식어나 핵심 동사에 강세를 얹고 문장 끝 억양으로 완료·미완료를 구분한다.", "모든 단어에 평평한 강세를 주면 상대가 정정 포인트를 듣지 못한다.", mode="pron"),
W("3분 상황극", "과거·가정", "연결", "If we had tested earlier, we would have caught the issue before launch.", "지난 사건(과거완료)과 대안(가정법·should have)을 2~3분 녹음 한 편으로 엮는다.", "단순과거만 나열해 시간 앞뒤와 후회·가정의 층위가 사라지지 않게 한다."),
W("중급 문법 점검", "변환", "일관", "Had I known the risk, I would have paused the release despite the pressure.", "가정법, 과거완료, 분사·전치사구를 섞어 2~3분 말하기와 10줄 글을 오류 없이 남긴다.", "조건절과 결과절의 시제가 어긋나거나 despite 뒤에 절이 남으면 통과하지 못한다."),
])
