# -*- coding: utf-8 -*-
"""Phase 03: 단락과 메일 (weeks 27–39)."""
from curriculum.common import E, phase
from curriculum.en.resources import R_Y1 as R

PHASE = phase("단락과 메일", 27, 39, "연결", "단락", "주제 문장과 예시 하나로 단락을 구성하고, 목적과 시점이 분명한 업무 메일과 답장을 작성한다.", R, [
E("주제 문장", "한 점", "단락", "Our team needs a quieter room.", "단락의 첫 문장에는 그 단락이 말하려는 핵심 생각 하나만 담는다.", "첫 문장에 서로 다른 주장을 두 개 넣으면 독자가 어디에 집중해야 할지 모른다.", "주제 문장 4개를 말한다.", "그중 하나를 골라 단락의 첫 줄로 쓴다.", "core"),
E("예시 하나", "for example", "구체", "We need a quieter room. For example, the calls echo.", "예시는 추상적인 주제 문장을 눈앞에 보이듯 구체화하는 사례 하나다.", "짧은 단락에 예시를 세 개씩 나열하면 초점이 흐려진다.", "예시 하나가 들어간 단락을 대본 없이 말한다.", "주제 문장과 예시 문장 두 줄을 쓴다.", "core"),
E("순서 말하기", "first", "then", "First I note the date. Then I write one request.", "절차는 first, then, after that으로 잇고 각 단계마다 명확한 동사를 둔다.", "Then만 반복하고 구체적인 동작 동사가 없으면 절차가 전달되지 않는다.", "세 단계 절차를 순서 표지와 함께 말한다.", "같은 절차를 4문장으로 쓴다.", "core"),
E("의견과 이유", "I think", "because", "I think the plan is late because the date is missing.", "의견을 말한 뒤에는 because로 가장 핵심적인 이유 하나를 붙여 뒷받침한다.", "한 문장에 이유를 세 개씩 이어 붙이면 주장이 산만해진다.", "의견 4개를 이유와 함께 말한다.", "가장 분명한 의견 하나를 두 문장으로 쓴다.", "core"),
E("메일 형식", "hello", "thanks", "Hello Ana, Could you send the file? Thanks, Min.", "짧은 업무 메일은 받는 사람, 용건, 구체적 요청, 보낸 사람 순으로 간결하게 쓴다.", "용건 없이 안부만 길게 쓰면 메일의 목적이 보이지 않는다.", "메일 한 통을 소리 내어 읽는다.", "같은 구조로 6줄 이내의 메일을 쓴다.", "core"),
E("부탁 메일", "could you", "by", "Could you send the notes by Friday?", "요청 메일에는 상대방이 해 줄 행동과 마감 시점(by + 시점)이 함께 들어가야 한다.", "Send the notes처럼 명령조로만 쓰면 시점도 불분명하고 어조도 거칠어진다.", "부탁 메일 한 통을 읽고 녹음한다.", "그 메일을 직접 쓴다.", "core"),
E("답장 메일", "thanks for", "next", "Thanks for the notes. I will read them today.", "답장 메일은 상대가 보내 준 내용을 확인한 한 줄과 내가 이어서 할 다음 행동 한 줄로 쓴다.", "상대 메일의 질문에 답하지 않고 새 주제만 꺼내면 답장이 아니다.", "받은 메일에 답하는 말을 녹음한다.", "답장 6줄을 쓴다.", "core"),
E("듣기: 안내와 일정", "받아쓰기", "핵심", "The review starts at 3 on Monday in Room 204.", "1~2분 업무 안내 오디오를 듣고 시각(at), 요일(on), 장소, 할 일을 받아쓴다.", "요일 앞에 at을 쓰거나 들은 시각·장소 중 하나를 빠뜨리지 않는다.", "오디오의 핵심 일정을 내 말로 다시 설명한다.", "받아쓴 안내 문장 4개를 정확히 고쳐 적는다.", "listen"),
E("강세 다시", "이름", "동사", "I need the FILE, not the link.", "새 정보나 대조되는 핵심 명사·동사에 강세를 두고 기능어는 약하게 발음한다.", "모든 단어에 똑같은 힘을 주어 읽으면 무엇을 강조하는지 들리지 않는다.", "문장 6개에서 강세 둘 단어를 정해 녹음한다.", "강세 둘 단어를 대문자로 표시해 적는다.", "pron"),
E("최소쌍", "r", "l", "I need light, not right.", "한국어에서 구분이 어려운 /r/과 /l/, /b/와 /v/, /θ/와 /s/를 최소대립쌍으로 정확히 구분해 발음한다.", "두 소리를 비슷하게 뭉개면 문맥에 따라 완전히 다른 단어로 들린다.", "최소대립쌍 10개를 녹음한다.", "헷갈린 쌍 4개를 골라 적는다.", "pron"),
E("2분으로 늘리기", "점", "예시", "The room is noisy. For example, the fan runs all day. So I close the door.", "2분 말하기는 핵심 주장, 구체적 예시, 그에 따른 결과·해결책의 세 덩어리로 구성한다.", "2분을 채우려고 도중에 주제를 바꾸면 1분짜리 이야기 두 개를 이어 붙인 것에 불과하다.", "소음이 심한 방 이야기를 2분 동안 녹음한다.", "세 덩어리의 첫 문장만 각각 쓴다.", "core"),
E("단락 고치기", "삭제", "한 점", "We need quiet. The fan runs all day.", "주제와 무관한 문장을 지운다.", "좋은 문장이라도 주제 밖이면 단락에 남기지 않는다.", "단락을 읽고 지운 문장을 말한다.", "지운 뒤의 단락을 다시 쓴다.", "core"),
E("메일과 단락", "메일", "단락", "Hello Ana, The room is noisy because the fan runs all day. Could you book another room? Thanks, Min.", "단락의 이유와 메일의 부탁이 같은 내용을 말한다.", "메일 부탁과 단락 이유가 다른 주제면 점검이 아니다.", "메일 한 통을 읽고 같은 내용을 대본 없이 말한다.", "그 메일을 8줄 이내로 쓴다.", "core"),
])
