# -*- coding: utf-8 -*-
"""Phase 17: 명료한 설명문 (weeks 209–221)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("명료한 설명문")

PHASE = phase("명료한 설명문", 209, 221, "C1 전환", "설명문", "복잡한 절차, 정책, 기술 원리를 비전문가 독자도 단번에 실행·이해하도록 쓰는 설명 산문을 익힌다.", STYLE, [
W("독자 모델과 목적 선언", "독자", "목적", "This guide shows new engineers how to rotate production keys without downtime.", "설명문의 첫 두 문장은 독자가 누구인지, 이 글을 읽고 무엇을 할 수 있는지 즉시 못 박는다.", "서론에서 회사의 10년 역사를 쓰느라 독자가 지금 무엇을 해야 하는지 두 번째 쪽에 숨기지 않는다."),
W("질문 기반 소제목 설계", "소제목", "지도", "Use action-focused headings like 'Step 2: Verify Staging Metrics' rather than 'Overview'.", "독자가 훑어보기(Skimming)만 해도 글의 뼈대를 알 수 있게 소제목을 구체적 질문이나 행동으로 쓴다.", "'Background', 'Details', 'Other Notes' 같은 모호한 제목으로 독자를 본문에 가두지 않는다."),
W("정의와 비유적 설명", "정의", "비유", "Idempotency ensures that repeating the same API call yields the same state as calling it once.", "낯선 개념을 정의할 때는 1문장 핵심 정의 뒤에 즉시 구체적 수치 사례나 일상 비유 하나를 붙인다.", "전문 용어를 또 다른 전문 용어로만 순환 정의하고 구체적 예를 건너뛰지 않는다."),
W("절차와 조건 분기 분리", "절차", "예외", "First, drain traffic from node A. If latency exceeds 200 ms, abort and alert on-call.", "정상 절차(Happy Path)는 번호 목록으로 쭉 잇고, 예외 조건과 경고는 분리된 주의 문장으로 뺀다.", "절차 한 문장 안에 괄호를 세 번 넣어 정상 흐름과 예외를 뒤섞지 않는다."),
W("인과와 메커니즘 설명", "원리", "메커니즘", "Because the cache lacks an upper bound, burst traffic exhausts heap memory within minutes.", "단순 사실 나열이 아니라 A가 왜 B를 일으키는지 중간 인과 고리를 빠뜨리지 않고 잇는다.", "'A happened, and B happened'만 나열해 독자가 왜 인과인지 짐작하게 두지 않는다."),
W("표와 예시의 본문 통합", "표", "맥락", "As Table 1 shows, batching cuts database round-trips from 400 to 12 per request.", "본문에서 표·수치·코드 예시를 그냥 던져 두지 않고, 독자가 그 표에서 무엇을 읽어야 할지 한 문장으로 이끌어 준다.", "'See below:' 한 줄만 적고 20줄짜리 표를 아무 해석 없이 던져 두지 않는다."),
W("사실·추정·권고의 격리", "분리", "근거", "Logs show a 4% spike (fact); this likely reflects retry storms (inference); we should cap retries (action).", "관찰된 사실, 원인에 대한 추정(likely/appears), 실행 권고를 문장과 문단 층위에서 명확히 가른다.", "사실 문장 속에 추측성 형용사를 섞어 검증된 사실까지 의견처럼 보이게 하지 않는다."),
W("모범 설명문 1편 해부", "원문", "모델", "Notice how the Stripe API guide states the rule in 14 words before showing the payload.", "검증된 기술 문서/설명문(Stripe Docs, MDN, Economist Explainer) 1편을 읽고 도입·정의·예시 전환 방식을 분석한다.", "한국어 번역투 문장 구조를 영어로 직역한 어색한 표현을 그대로 모방하지 않는다.", mode="read"),
W("경고와 제약 문장 작성", "제약", "이유", "Do not truncate the audit log manually; doing so breaks hash-chain verification.", "금지·경고 문장은 '하지 마라'에서 멈추지 않고 그 행동을 했을 때 일어나는 구체적 결과를 바로 붙인다.", "'Be careful when editing config'처럼 무엇이 왜 위험한지 말하지 않는 공허한 경고를 쓰지 않는다."),
W("1쪽 기술 메모(One-Pager)", "요약", "완결", "This one-pager explains why we migrated from polling to webhooks and lists two trade-offs.", "실제 업무나 기술 주제 1개를 골라 배경-원리-절차-제약을 담은 250단어 1쪽 설명 메모를 쓴다.", "1쪽 메모에 관련 없는 부수 역사를 넣어 두 쪽으로 넘치지 않게 한다."),
W("듣기: 기술·정책 해설 요약", "청취", "구조", "The speaker contrasts symmetric encryption's speed with asymmetric key distribution.", "5분 분량 원어민 설명 영상/팟캐스트를 듣고 핵심 개념 대비와 예시 두 개를 영어로 받아 적고 재설명한다.", "세부 숫자만 받아 적고 전체 비유와 개념 대비 구조를 놓치지 않는다.", mode="listen"),
W("비전문가 대상 낭독 시험", "낭독", "이해", "Read the 250-word guide aloud and mark every sentence that requires re-reading.", "쓴 설명문을 소리 내어 읽으며 한 번에 뜻이 잡히지 않거나 용어 점프가 생기는 문장을 찾아 쪼갠다.", "작성자 본인 머릿속 배경지식이 있어야만 이어지는 생략된 논리 단계를 남기지 않는다."),
W("설명문 점검", "독자", "명료", "A colleague outside the team can execute the three-step procedure without asking follow-up questions.", "명사화 제거, 독자 목적 첫 문장, 사실-추정 분리가 모두 지켜진 300단어 설명문과 2분 구두 설명을 완성한다.", "절차 단계가 하나라도 비거나 모호한 대명사가 남으면 통과하지 못한다."),
])
