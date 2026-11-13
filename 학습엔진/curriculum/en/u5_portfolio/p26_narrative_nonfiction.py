# -*- coding: utf-8 -*-
"""Phase 26: 서사적 논픽션 (weeks 326–338)."""
from curriculum.common import phase
from curriculum.en.resources import LONG
from curriculum.en.templates import bind_writer

W = bind_writer("서사적 논픽션")

PHASE = phase("서사적 논픽션", 326, 338, "장문 설계", "서사 논픽션", "기술·역사·현업 사례를 다룰 때 인물, 갈등, 선택, 결과를 갖춘 생생한 서사적 논픽션(Narrative Nonfiction)으로 풀어낸다.", LONG, [
W("인물·목표·장애의 삼각형", "욕망", "장애", "Define the protagonist's concrete goal and the structural obstacle blocking it in two crisp sentences.", "서사 속 인물(개발팀, 창업자, 엔지니어)이 달성하려는 구체적 목표와 가로막는 구조적 장애를 두 문장으로 고정한다.", "장애를 막연한 '운이 나빴다'나 성격 탓으로 돌리지 않고 실제 제약 조건으로 세운다."),
W("갈등의 단계적 고조(Escalation)", "고조", "위기", "Show two failed attempts before the crisis peaks; never solve the problem on the first try.", "문제가 한 번에 쉽게 풀리지 않고 첫 번째·두 번째 시도가 빗나가며 긴장이 높아지는 단계를 구성한다.", "위기가 발생하자마자 다음 문장에서 아무 대가 없이 깔끔히 해결해 버리지 않는다."),
W("결정적 선택의 순간(Turning Point)", "선택", "대가", "Pause at the fork where the actor must trade away one value to save another.", "인물이 두 가지 모두 가질 수 없는 딜레마(속도 vs 안전, 단기 매출 vs 신뢰) 앞에서 한쪽을 고르는 순간을 포착한다.", "선택의 대가가 전혀 없는 공짜 승리처럼 서사를 쓰지 않는다."),
W("시간 압축과 전환(Scene vs Summary)", "압축", "요약", "Play crucial turning points in real-time scene, and compress routine weeks into two-line summary bridges.", "결정적 10분은 구체적 장면(Scene)으로 세밀히 쓰고, 지루한 3주간의 대기 기간은 두 줄 요약(Summary)으로 건너뛴다.", "사소한 이동 과정은 10줄 쓰면서 정작 핵심 결정 순간을 한 줄 요약으로 날리지 않는다."),
W("서사 속 기술·배경 녹이기(Exposition)", "배경", "통합", "Weave necessary technical context into the moment of conflict rather than pausing for a 3-paragraph lecture.", "독자가 사건을 이해하는 데 필요한 기술·제도 배경을 긴 강의 블록 대신 갈등이 터진 직후에 3~4줄로 자연스럽게 심는다.", "사건이 한창 급박한 순간에 이야기를 세우고 500단어 교과서 설명을 끼워 넣지 않는다."),
W("관찰자의 통찰과 절제된 교훈", "통찰", "절제", "Let the sequence of actions and consequences imply the lesson instead of preaching at the end.", "사건과 선택의 결과가 스스로 교훈을 말하게 두고, 끝에 '이 사건은 우리에게 ~을 가르쳐 준다'는 훈계를 길게 달지 않는다.", "이야기 전체의 30%를 뻔한 도덕적 교훈 설교로 채우지 않는다."),
W("Joan Didion / Tracy Kidder 모델 독해", "거장", "독해", "Read a narrative nonfiction excerpt (e.g., Kidder's Soul of a New Machine) for pacing and technical clarity.", "고전 서사 논픽션(예: Tracy Kidder, Michael Lewis, New Yorker 기술 르포) 1편을 읽고 장면-배경-긴장 전환 기법을 분석한다.", "단순 감상평만 적지 않고 작가가 어디서 요약에서 장면으로 줌인했는지 표시한다.", mode="read"),
W("대화·회의록의 서사적 재구성", "대화", "압축", "Distill a 20-minute meeting transcript into three sharp exchanges that reveal each side's stake.", "실제나 가상의 회의 발췌에서 군더더기 인사를 빼고 양측의 진짜 이해충돌이 드러나는 3마디 핵심 대화로 압축한다.", "회의록 전체를 그대로 받아 적어 지루한 속기록을 만들지 않는다."),
W("시간선과 원인의 뒤집기(In Medias Res)", "시간선", "도입", "Open in the middle of the crisis ('At 03:14, all replicas stalled'), then step back 48 hours to trace the cause.", "평범한 연대기('월요일에 시작해서...') 대신 위기의 한가운데(In Medias Res)로 열어 48시간 전으로 거슬러 올라가는 구성을 연습한다.", "시간 점프 표지('Two days earlier...') 없이 시점을 옮겨 독자가 지금 언제인지 혼란스럽게 하지 않는다."),
W("듣기: 장편 다큐/오디오북 서사 분석", "청취", "호흡", "Listen to a 6-minute narrative audio story (This American Life / Radiolab) and map its scene-vs-summary shifts.", "6분 내러티브 다큐 오디오를 듣고 화자가 언제 장면 묘사로 속도를 늦추고 언제 요약으로 건너뛰는지 받아 적는다.", "재미있는 사건만 듣다 오디오의 구조적 줌인/줌아웃 기법을 놓치지 않는다.", mode="listen"),
W("700단어 서사 논픽션 단편 집필", "초고", "단편", "Write a 700-word narrative nonfiction case study about a real or realistic engineering/business turning point.", "실제 또는 현실적 기술·사업 사건 1건을 인물·장애·시도·선택·여파가 담긴 700단어 서사 논픽션으로 집필한다.", "단순 보고서 요약문처럼 인물의 고민과 선택의 대가가 지워진 건조한 연표를 쓰지 않는다."),
W("서사 낭독과 속도 조절 교정", "낭독", "속도", "Read the 700-word story aloud; cut slow summary passages and sharpen the turning-point scene.", "700단어 초고를 소리 내어 읽으며 긴장이 식는 배경 설명 문단을 40% 덜어 내고 결정적 선택 장면을 선명하게 다듬는다.", "대화나 장면 속에 불필요한 해설을 끼워 넣어 리듬을 끊지 않는다."),
W("서사 논픽션 점검", "선택", "장면", "The 700-word narrative delivers a clear goal, escalating obstacle, costly choice, and earned insight.", "완성된 700단어 서사 논픽션과 3분 구두 스토리텔링 녹음을 놓고 장면-배경 비율과 선택의 명확성을 최종 점검한다.", "장애나 선택의 대가 없이 단순 사건 나열에 그쳤다면 다시 집필한다."),
])
