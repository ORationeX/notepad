# -*- coding: utf-8 -*-
"""Phase 18: 문장 호흡과 응집 (weeks 222–234)."""
from curriculum.common import phase
from curriculum.en.resources import STYLE
from curriculum.en.templates import bind_writer

W = bind_writer("문장 호흡과 응집")

PHASE = phase("문장 호흡과 응집", 222, 234, "설명문", "문장 호흡", "Joseph Williams <Style> 원리에 따라 주어 일치, Old-New 정보 흐름, 동사 중심 명료 문장을 체화한다.", STYLE, [
W("행위자 주어 맞추기", "주어", "동사", "When engineers bypass code review, defect rates rise—not 'Review bypassing causes increases'.", "추상 명사를 주어로 세우는 습관을 버리고, 실제 행동을 하는 사람이나 시스템을 문장의 주어로 둔다.", "문장 첫 다섯 단어 안에 누가 무슨 행동을 하는지 전혀 보이지 않는 문장을 쓰지 않는다."),
W("Old-to-New 정보 사슬", "연결", "흐름", "The server drops idle sockets after 60s. That timeout forces mobile clients to reconnect.", "앞 문장 끝에 등장한 새 정보를 다음 문장의 앞머리(주어/주제)로 받아 문장이 매끄럽게 물고 물리게 만든다.", "매 문장이 전혀 새로운 주어로 뚝뚝 끊기며 시작해 글 전체가 목록처럼 읽히지 않게 한다."),
W("Topic-Focus 응집(Cohesion)", "주제", "초점", "Consistent sentence topics across four lines help readers track one argument smoothly.", "단락 안 네다섯 문장의 문법적 주어(Topic String)가 같은 핵심 주제를 일관되게 가리키는지 점검한다.", "단락 한가운데 뜬금없는 주어(The policy → Users → Latency → Our budget)로 독자 시선을 흩뜨리지 않는다."),
W("명사화(Nominalization) 수술", "수술", "동사", "Change 'conduct an evaluation of' and 'make a recommendation' to 'evaluate' and 'recommend'.", "동사를 죽이는 허수 동사(conduct, perform, make, achieve + 명사)를 본동사로 복원해 문장 길이를 25% 줄인다.", "학술적·격식 있게 보인다는 착각으로 쉬운 동사를 긴 명사구로 부풀리지 않는다."),
W("수동태의 전략적 선택", "수동", "능동", "Use active voice to assign responsibility, and passive voice only to keep Old-New topic flow.", "무조건 수동태 금지 교조를 버리고, 1) 행위자 명시=능동, 2) 문맥상 앞 문장 대상 유지=수동 기준으로 고른다.", "주어 연결을 유지해야 할 자리에 억지로 능동태를 써서 오히려 문장 흐름을 깨지 않는다."),
W("전치사구 사슬 끊기", "전치사", "간결", "Trim 'the assessment of the impact of the change in schedule' to 'assessing the schedule change'.", "of, in, for, by 전치사구가 3개 이상 연달아 붙은 문장을 동사구와 소유·관계 구조로 해체한다.", "명사+of+명사+of+명사 사슬로 독자의 단기 기억을 소진시키지 않는다."),
W("군더더기 도입구(Metadiscourse)", "허사", "삭제", "Cut 'It is important to note that' and 'There are several factors that influence' cleanly.", "There is/are, It is worth noting that, In order to, As a matter of fact 같은 군더더기 서두를 과감히 지운다.", "본론으로 들어가기 전에 문장 4단어를 허사로 낭비하지 않는다."),
W("강조 끝자리(Stress Position)", "끝자리", "강조", "End the sentence with the most surprising or consequential fact, not a weak time phrase.", "독자의 기억에 가장 세게 남는 문장 끝자리에 덜 중요한 시간·장소 부사구나 단서를 두지 않고 핵심 논점을 배치한다.", "강한 단언을 문장 앞에 쓰고 뒤에 'in most cases yesterday'처럼 힘 빠진 꼬리를 달지 않는다."),
W("병렬 대칭으로 복합 문장 세우기", "대칭", "리듬", "Parallel clauses let a 35-word sentence read cleanly: 'not because X failed, but because Y scaled.'", "문장이 길어질수록 대칭 구조(not X, but Y / whether A or B / first..., second...)를 세워 길이를 지탱한다.", "긴 문장을 쉼표와 which 절만 계속 이어 붙여 호흡이 끊어지게 만들지 않는다."),
W("긴 문장과 짧은 문장의 완급", "리듬", "완급", "Follow a detailed 30-word analysis with a crisp 5-word verdict: 'The math failed.'", "비슷한 길이의 15단어 문장만 나열하는 단조로움을 깨고, 30단어 분석 뒤에 5~7단어 짧은 단언을 꽂는다.", "짧게 쓰라는 규칙을 오해해 6단어 단문만 기계적으로 나열하는 스타카토 문체를 쓰지 않는다."),
W("원문 에세이 문체 모방(Imitation)", "모방", "리듬", "Analyze a 200-word Orwell or Economist paragraph and mirror its sentence-length cadence.", "거장 산문가(Orwell, Zinsser, Economist)의 한 문단 구조를 분해하고, 완전히 다른 기술 주제로 같은 리듬의 문단을 쓴다.", "단어를 베끼는 것이 아니라 문장 길이 변화, 주어 연결, 전환 방식을 모방한다.", mode="read"),
W("듣기: 명료 산문 낭독 감각", "호흡", "청취", "Listen to a 3-minute essay reading and mark where pauses fall naturally at clause boundaries.", "수준 높은 에세이/오피니언 낭독 오디오를 듣고, 의미 덩어리(Thought Group)와 강조 끝자리의 강세 패턴을 따라 읽는다.", "무호흡으로 단어를 평평하게 훑어 읽어 핵심 대비가 귀에 들리지 않게 하지 않는다.", mode="listen"),
W("문장 호흡 점검", "리듬", "응집", "Every paragraph passes the Topic-Focus test and cuts empty nominalizations by sight and sound.", "어지러운 250단어 초고 1편을 주어-동사 복원, Old-New 연결, 강조 끝자리 재배치로 퇴고해 낭독 녹음과 함께 남긴다.", "문장들이 개별적으로는 맞지만 문단 전체의 주제 사슬이 끊어져 있으면 다시 다듬는다."),
])
