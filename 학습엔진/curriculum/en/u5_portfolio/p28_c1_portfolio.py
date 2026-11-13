# -*- coding: utf-8 -*-
"""Phase 28: C1 글 포트폴리오 (weeks 352–364)."""
from curriculum.common import phase
from curriculum.en.resources import LONG
from curriculum.en.templates import bind_writer

W = bind_writer("C1 글 포트폴리오")

PHASE = phase("C1 글 포트폴리오", 352, 364, "장문 완성", "C1 포트폴리오", "7년 동안 쌓은 구어·실무·계약·장문 역량을 대표작 3편 선집, 개정 이력, 10분 구술 발표로 집대성한다.", LONG, [
W("선집 큐레이션과 공통 질문 고정", "선집", "기준", "Curate three pieces (Explainer, Contract/Policy Brief, Flagship Essay) unified by one overarching theme.", "대표작 1,450단어 에세이, 1편의 심층 설명문/논증문, 1편의 계약·정책 검토 브리프를 하나의 문제의식으로 묶는다.", "가장 최근에 쓴 글 아무거나 세 편을 연결 질문 없이 모아 두지 않는다."),
W("서문(Preface) 집필", "서문", "질문", "Write a 300-word preface framing the portfolio's central question, intended reader, and reading path.", "독자가 이 3편의 묶음을 왜 이 순서로 읽어야 하는지, 무엇을 얻어 갈지 밝히는 300단어 서문을 작성한다.", "서문을 자기 신세 한탄이나 공부 소감문으로 채우지 않는다."),
W("선집 연결 다리(Headnotes)", "다리", "맥락", "Add a 60-word headnote before each piece explaining its distinct job and where its perspective shifts.", "각 작품 앞에 60단어 안팎의 안내문(Headnote)을 붙여 이전 글과 다음 글이 어떻게 서로의 빈틈을 보완하는지 밝힌다.", "제목만 덜렁 두고 독자가 세 글 사이의 논리적 맥락을 알아서 추측하게 두지 않는다."),
W("계약·논증 정합성 교차 감사", "정밀감사", "일관", "Audit every piece for ambiguous modifiers, undefined acronyms, passive escapes, and unsupported absolutes.", "포함된 계약/정책 브리프와 논증문에 중의적 수식어, 미정의 약어, 근거 없는 절대 표현이 없는지 교차 감사한다.", "문학적 멋을 낸다고 정확성과 사실-추정 경계를 흐리는 문장을 남기지 않는다."),
W("퇴고 증거 아카이브(Before/After)", "아카이브", "증거", "Compile 10 pairs of original vs revised sentences showing concrete gains in clarity, cadence, and precision.", "7년 학습 과정(또는 대표작 초고 vs 최종본)에서 가장 크게 개선된 문장 전후 대조 10쌍과 교정 원리를 정리한다.", "고친 문장만 적고 원래 문장에서 무엇이 왜 문제였는지 원리를 빠뜨리지 않는다."),
W("외부 모델과의 벤치마크 리뷰", "벤치마크", "대조", "Set your flagship 1,450-word essay beside a published Economist/Atlantic piece and audit the remaining gap.", "내 대표작과 동종 주제의 영미권 대표 저널 기사 1편을 나란히 놓고 논지 전개 속도, 어휘 정밀도, 리듬의 잔여 격차를 진단한다.", "비교를 피하거나 추상적 자기만족으로 끝내지 않고 구체적 보완점 3개를 적는다.", mode="read"),
W("블라인드 피드백 기반 최종 개작", "피드백", "개작", "Identify the weakest 200-word section through a fresh blind read and rewrite it from scratch.", "가장 논리·서사 밀도가 떨어지는 200단어 구간 하나를 골라 부분 수정이 아니라 백지에서 완전히 새로 써서 교체한다.", "문장 몇 단어만 고쳐 쓰며 구조적 약점을 덮고 넘어가지 않는다."),
W("1쪽 C1 스타일 체크리스트 제작", "체크리스트", "규범", "Distill your personal 12-point English writing & contract-checking checklist for lifelong reuse.", "앞으로 어떤 영문 문서·계약서·보고서·에세이를 쓸 때도 첫날 펼쳐 볼 나만의 1쪽 영문 스타일·검증 체크리스트를 만든다.", "교과서 목차 50개를 그대로 베끼지 않고 내가 실제로 자주 틀리는 함정 중심으로 압축한다."),
W("선집 전체 통독 및 용어 통일", "통독", "통일", "Read the entire compiled portfolio end-to-end for consistent spelling, terminology, and voice transitions.", "서문부터 마지막 글까지 한 번에 통독하며 표기법(미국식/영국식 일관성), 약어 정의, 어조 전환을 통일한다.", "첫 글은 미국식 철자, 둘째 글은 영국식 철자로 섞어 놓는 사소한 흠결을 남기지 않는다."),
W("10분 포트폴리오 구술 발표 준비", "발표준비", "카드", "Condense the entire portfolio into a 10-keyword speaking outline for a 10-minute unscripted talk.", "대본 없이 서문 논지, 3편 핵심 요약, 대표 퇴고 사례 2개, 향후 적용 계획을 말할 키워드 카드 10개만 만든다.", "10분 전체 대본을 미리 써서 줄줄 읽는 암기 발표를 준비하지 않는다."),
W("듣기·말하기 통합 10분 발표 녹음", "10분녹음", "방어", "Record a 10-minute unscripted presentation and answer three impromptu critical questions aloud.", "키워드 카드만 보고 10분 영문 발표를 녹음한 뒤, 스스로 준비한 까다로운 영어 질문 3개에 즉흥 답변을 이어 녹음한다.", "발표 도중 10초 이상 멈추거나 한국어로 설명하고 넘어가면 그 구간을 다시 훈련한다.", mode="listen"),
W("7년 영어 회고 및 유지 루틴 확정", "회고", "유지", "Compare week-1 recordings with today's 10-minute talk and set a sustainable weekly post-graduation cadence.", "1주차 기초 발음·60초 자기소개와 오늘 10분 발표·1,450단어 대표작의 간극을 돌아보고, 과정 종료 후 주간 유지 루틴을 확정한다.", "과정이 끝났다고 영문 독해·낭독·퇴고 루틴을 완전히 끊는 계획을 세우지 않는다."),
W("7년 C1 포트폴리오 최종 점검", "졸업", "완결", "Portfolio passes readability, logical rigor, register control, and 10-minute unscripted oral defense.", "서문 + 3편 완성본 + 전후 퇴고 10쌍 + 1쪽 체크리스트 + 10분 구술 녹음으로 7년 영어 과정을 완결한다.", "체크리스트 기준 중 하나라도 빈칸이거나 구술 발표가 대본 낭독이면 최종 점검을 통과하지 못한다."),
])
