# -*- coding: utf-8 -*-
from syllabus_util import E, phase

_KIND = None
SPEAK = {}
WRITE = {}

def kind(name):
    global _KIND
    _KIND = name
    return name

def fill(template, **kw):
    out = template
    for key, value in kw.items():
        out = out.replace("{" + key + "}", value)
    return out

def W(title, lab2, lab3, model, pattern, trap):
    if _KIND not in SPEAK or _KIND not in WRITE:
        raise SystemExit(f"no english task for {_KIND}")
    speak = fill(SPEAK[_KIND], title=title, model=model, pattern=pattern, trap=trap)
    write = fill(WRITE[_KIND], title=title, model=model, pattern=pattern, trap=trap)
    if speak == write or "기준 문장을 넣어 60초" in speak:
        raise SystemExit(f"cloned task: {title}")
    return E(title, lab2, lab3, model, pattern, trap, speak, write)

SPEAK["설명문"] = "{pattern} 새로 합류한 동료에게 절차를 60초 동안 설명한다. 첫 문장: {model}"
WRITE["설명문"] = "{trap} 독자가 그대로 따라 할 수 있는 단계만 여섯 줄로 쓴다. 남길 문장: {model}"
SPEAK["문장 길이"] = "{pattern} 한 문장에 한 가지 뜻만 담기도록 끊어 60초 동안 읽는다. 다듬을 문장: {model}"
WRITE["문장 길이"] = "{trap} 한 문장이 한 가지 역할만 하도록 네 문장으로 나누어 다시 쓴다. 재료: {model}"
SPEAK["단락 순서"] = "{pattern} 단락의 전개 순서를 60초 동안 설명한다. 이번 단락: {model}"
WRITE["단락 순서"] = "{trap} 개요의 논리적 순서에 맞춰 네 단락의 첫 문장만 쓴다. 기준: {model}"
SPEAK["장면 단락"] = "{pattern} 한 공간에서 일어나는 장면을 60초 동안 묘사한다. 장면 문장: {model}"
WRITE["장면 단락"] = "{trap} 그 장면의 공간과 행동이 보이는 네 줄만 남긴다. 남길 문장: {model}"
SPEAK["목소리"] = "{pattern} 서술자(Min)의 일관된 시점과 어조로 60초 동안 읽는다. 문장: {model}"
WRITE["목소리"] = "{trap} 어조가 튀는 문장을 서술자의 일관된 말투로 고쳐 네 줄을 쓴다. 기준: {model}"
SPEAK["주장 글"] = "{pattern} 핵심 주장과 근거를 60초 동안 명확히 말한다. 문장: {model}"
WRITE["주장 글"] = "{trap} 주장 하나, 이유 둘, 구체적 요청 하나를 여섯 줄로 쓴다. 주장: {model}"
SPEAK["구체와 어조"] = "{pattern} 독자에게 맞는 일관된 격식과 구체적 표현으로 60초 동안 말한다. 문장: {model}"
WRITE["구체와 어조"] = "{trap} 모호한 추상어를 구체적인 이름과 숫자로 바꾼 네 줄을 쓴다. 고칠 문장: {model}"
SPEAK["초고 고치기"] = "{pattern} 어제 쓴 초고에서 무엇을 왜 고쳤는지 60초 동안 설명한다. 문장: {model}"
WRITE["초고 고치기"] = "{trap} 고친 문장과 수정한 이유를 네 줄로 적는다. 대상: {model}"
SPEAK["책의 구조"] = "{pattern} 목차만 보고도 글 전체의 질문과 흐름이 보이도록 60초 동안 설명한다. 문장: {model}"
WRITE["책의 구조"] = "{trap} 장의 배열 이유를 구조 메모 여섯 줄로 쓴다. 기준: {model}"
SPEAK["인물과 산문"] = "{pattern} 인물이 원하는 것과 가로막는 장애물을 60초 동안 말한다. 문장: {model}"
WRITE["인물과 산문"] = "{trap} 인물의 선택에서 멈추는 한 페이지의 첫 여섯 줄을 쓴다. 재료: {model}"
SPEAK["세 편의 글"] = "{pattern} 설명문, 장면 묘사, 주장 글 세 편의 목적이 어떻게 다른지 60초 동안 비교해 말한다. 문장: {model}"
WRITE["세 편의 글"] = "{trap} 선택한 한 편의 개요를 여섯 줄로 쓴다. 기준: {model}"
SPEAK["글 포트폴리오"] = "{pattern} 구조 메모의 흐름에 따라 포트폴리오 구성을 60초 동안 설명한다. 문장: {model}"
WRITE["글 포트폴리오"] = "{trap} 핵심 질문 하나에 답하는 목차와 각 글의 역할을 여섯 줄로 쓴다. 기준: {model}"

NOTE = "녹음기. 자신이 쓴 초고. 카드에는 고친 문장만 남긴다."
BOOK = "녹음기. 자신이 정한 짧은 글. 구조 메모는 이 단계의 노트에 남긴다."

LATE = [
phase(kind("설명문"), 209, 221, "위험 문장", "설명", "절차와 사실을 설명문으로 쓴 뒤에야 이야기 단락으로 넘어간다.", NOTE, [
W("설명문의 일", "절차", "독자", "This note tells a new teammate how to send the file.", "설명문은 독자와 할 일이 있다.", "설명문 없이 감상만 쓰면 독자가 무엇을 하는지 모른다."),
W("독자와 목적", "who", "why", "The reader is Ana. The purpose is to show the step order.", "첫 두 문장은 독자와 목적이다.", "독자를 정하지 않으면 어느 말을 뺄지 모른다."),
W("절차 설명문", "step", "동사", "Open the file. Check the date. Send it to Ana.", "절차 설명문은 동사로 시작하는 단계다.", "단계를 형용사로만 쓰면 행동이 없다."),
W("순서 표지", "first", "then", "First check the date. Then send the file.", "First와 Then이 순서를 보여 준다.", "표지 없이 문장을 쌓으면 어느 쪽이 먼저인지 모른다."),
W("정의 다음 예시", "means", "example", "A draft means the file. For example, March Review.", "정의 다음에 예시 하나다.", "정의만 있고 예시가 없으면 설명문이 추상으로 끝난다."),
W("경고 문장", "do not", "이유", "Do not send the raw notes, because they are not the file.", "경고 문장은 하지 말아야 할 행동과 그 이유를 함께 적는다.", "Be careful처럼만 쓰면 구체적으로 무엇을 하지 말아야 하는지 알 수 없다."),
W("메모 형식", "날짜", "할일", "4 April. Sent the file to Ana. Next, wait five days.", "업무 메모는 날짜, 완료한 일, 다음 할 일 순으로 적는다.", "오늘 바빴다는 식의 감상은 업무 메모가 아니다."),
W("사실과 평가", "분리", "사실", "The file has 12 pages. I think it is clear.", "객관적 사실은 수량으로 적고, 주관적 평가는 I think 뒤에 분리해 둔다.", "사실과 평가를 한 문장에 섞으면 12페이지라는 사실까지 의견처럼 들린다."),
W("한 장 요약", "다섯", "문장", "Ana needs the file by 28 March. Min sends it by email.", "한 장 요약은 다섯 문장 이내의 핵심 사실로만 압축한다.", "요약을 두 페이지로 늘리면 요약의 역할을 잃는다."),
W("질문으로 열기", "how", "답", "How do you send the file? You email March Review.", "설명문을 질문으로 열었다면 바로 다음 문장에서 답을 제시한다.", "질문만 던지고 답을 뒤로 미루면 독자가 절차를 바로 파악할 수 없다."),
W("설명문 낭독", "소리", "단계", "First check the date. Then send the file.", "소리 내어 읽으며 절차의 단계가 빠지지 않았는지 확인한다.", "눈으로만 보면 단계 순서가 뒤집혀도 지나치기 쉽다."),
W("설명문 고치기", "삭제", "목적", "Delete the sentence that does not help Ana send the file.", "독자가 절차를 수행하는 데 도움이 되지 않는 문장은 지운다.", "표현이 좋은 문장이라도 설명 목적에서 벗어나면 남기지 않는다."),
W("설명문 점검", "독자", "단계", "Ana can send the file by following three steps.", "독자가 적힌 단계만 따라 해서 일을 마칠 수 있으면 점검 통과다.", "필수 단계가 하나라도 빠지면 설명문 점검을 통과하지 못한다."),
]),
phase(kind("문장 길이"), 222, 234, "설명문", "문장", "한 문장에 한 가지 역할만 담기도록 문장 길이를 다듬는다.", NOTE, [
W("문장 나누기", "둘", "마침표", "Min writes the report. Ana pays the fee.", "and가 서로 다른 두 사건을 이으면 마침표로 문장을 나눈다.", "한 문장에 사건을 세 개씩 우겨 넣으면 주어가 누구인지 흐려진다."),
W("문장 잇기", "because", "둘", "I waited because the file was late.", "너무 짧게 끊어진 두 문장이 원인과 결과 관계라면 because로 잇는다.", "인과 관계도 없는데 길게 이어 붙이기만 하면 산만한 문장이 된다."),
W("주어 찾기", "누가", "동사", "Min sent the file.", "문장마다 동작을 수행하는 주어가 누구인지 명확히 드러낸다.", "행위 주어를 생략하면 누가 파일을 보냈는지 알 수 없다."),
W("수식 줄이기", "형용사", "하나", "The short file arrived.", "명사 앞의 형용사 수식은 핵심 특징 하나면 충분하다.", "형용사를 네 개씩 겹쳐 붙이면 정작 중심 명사가 눈에 들어오지 않는다."),
W("접속 하나", "and", "하나", "I wrote the note and sent it.", "한 문장 안의 접속사는 가급적 하나로 제한한다.", "and와 but을 한 문장에 겹쳐 쓰면 논점과 사건이 뒤엉킨다."),
W("능동으로", "누가", "동사", "Min sent the file.", "행위자를 알고 있을 때는 능동태로 써서 책임을 분명히 한다.", "The file was sent처럼 습관적으로 수동태를 쓰면 누가 보냈는지 가려진다."),
W("중복 지우기", "같은 말", "한 번", "The file arrived on Monday.", "같은 의미를 다른 단어로 두 번 반복하지 않는다.", "The file arrived and the file came은 불필요한 동어반복이다."),
W("구체 명사", "이름", "파일", "March Review arrived.", "막연한 일반명사 대신 구체적인 고유 이름이나 문서 제목을 쓴다.", "The thing arrived처럼 대명사성 명사로 때우면 무엇이 도착했는지 알 수 없다."),
W("동사 살리기", "동사", "명사", "Ana decided.", "make a decision처럼 명사구를 늘리는 대신 decided처럼 동사 하나로 힘 있게 쓴다.", "명사화 표현만 쌓으면 문장이 길어지고 동작이 보이지 않는다."),
W("문장 리듬", "짧고", "길고", "The file arrived. I read the first page because the date mattered.", "짧은 핵심 문장 뒤에 이유가 붙은 긴 문장을 배치해 완급을 만든다.", "모든 문장을 똑같은 길이로만 나열하면 글이 단조로워진다."),
W("소리로 길이", "숨", "쉼표", "I read one clause, then I breathe.", "한 호흡에 자연스럽게 읽히는 길이에서 문장을 마무리한다.", "쉼표로만 끝없이 이어 붙이면 소리 내어 읽을 때 호흡이 막힌다."),
W("문단의 문장 수", "다섯", "이내", "A paragraph here holds at most five sentences.", "이 단계에서는 한 문단을 다섯 문장 이내로 유지한다.", "한 문단에 열 문장씩 넣으면 여러 주제가 한데 섞인다."),
W("길이 점검", "일", "하나", "Each sentence does one job.", "모든 문장이 각각 한 가지 명확한 역할만 수행하는지 점검한다.", "한 문장에 서로 다른 두 가지 이야기가 섞여 있으면 다시 나눈다."),
]),
phase(kind("단락 순서"), 235, 247, "문장", "단락", "단락의 순서를 시간, 중요도, 비교 중 하나로 정한다.", NOTE, [
W("단락의 일", "하나", "단락", "This paragraph only explains the date.", "단락은 일 하나만 맡는다.", "한 단락에 날짜와 수수료와 인사를 넣으면 일이 셋이다."),
W("단락 첫 문장", "일", "먼저", "The date changed to 28 March.", "첫 문장이 그 단락의 일이다.", "첫 문장이 배경이면 일이 늦어진다."),
W("뒷받침 둘", "둘", "까지만", "The old date was 21 March. The new date is 28 March.", "뒷받침은 두 문장까지다.", "뒷받침을 다섯 개 두면 단락이 목록이 된다."),
W("전환 문장", "so", "다음", "So the next paragraph covers the fee.", "단락 끝은 다음 단락의 일을 한 줄로 알린다.", "전환 없이 주제를 바꾸면 독자가 끊긴다."),
W("시간 순서", "먼저", "나중", "First the data arrived. Later the file went out.", "시간 순서는 먼저와 나중이다.", "결과를 원인보다 먼저 두면 시간 순서가 아니다."),
W("중요 순서", "먼저", "큰일", "The missing date comes first. The font comes last.", "중요한 일을 앞 단락에 둔다.", "글꼴을 앞에 두면 빠진 날짜가 묻힌다."),
W("비교 순서", "한쪽", "다른쪽", "Monday had 8 calls. Tuesday had 12.", "비교는 한쪽을 끝내고 다른 쪽으로 간다.", "두 대상을 문장마다 오가면 순서가 없다."),
W("단락 옮기기", "앞", "뒤", "Move the fee paragraph before the greeting.", "일의 순서에 맞게 단락을 옮긴다.", "쓴 순서를 순서로 착각하면 옮기지 못한다."),
W("단락 합치기", "같은 일", "하나", "Both sentences are about the date, so they share a paragraph.", "같은 일의 문장은 한 단락이다.", "같은 일을 두 단락에 나누면 일이 둘처럼 보인다."),
W("단락 나누기", "다른 일", "둘", "The fee is a new job, so it starts a new paragraph.", "일이 바뀌면 단락을 나눈다.", "한 단락에 일을 남겨 두면 나눈 것이 아니다."),
W("단락 끝 문장", "그래서", "결과", "So Ana can read the file on 28 March.", "끝 문장은 그 단락의 결과다.", "끝 문장에서 새 일을 열면 단락이 안 끝난다."),
W("개요 여섯", "여섯", "일", "Date, fee, file, contact, review, close.", "개요는 단락의 일 여섯 개다.", "개요에 문장을 그대로 쓰면 개요가 아니라 초고다."),
W("순서 점검", "일", "순서", "The six jobs appear in the order of the outline.", "단락 순서가 개요와 같다.", "개요에 없는 단락이 있으면 순서 점검이 아니다."),
]),
phase(kind("장면 단락"), 248, 260, "단락", "장면", "설명문 다음에 한 자리의 장면을 쓴다.", NOTE, [
W("장면 하나", "자리", "하나", "At the desk, Min closed the laptop.", "장면은 자리 하나와 행동 하나다.", "자리를 세 곳 쓰면 장면이 셋이다."),
W("장면의 감각", "소리", "하나", "The fan hummed beside the desk.", "감각은 하나면 충분하다.", "감각을 다섯 개 나열하면 장면이 목록이 된다."),
W("장면의 행동", "동사", "하나", "Min sent the file and waited.", "행동의 동사는 장면 안에서 끝난다.", "그 해의 인생을 요약하면 장면이 아니다."),
W("장면 대화", "두 줄", "말", "Ana asked, Where is the file? Min said, It is in the mail.", "대화는 두 줄까지 먼저 쓴다.", "대화를 열 줄 쓰면 장면이 희곡이 된다."),
W("장면의 장소", "어디", "한 줄", "The desk faced the window.", "장소는 한 줄로 적는다.", "도시 역사를 쓰면 장소가 설명문이 된다."),
W("장면의 시각", "언제", "한 줄", "It was just after four.", "시각은 한 줄로 적는다.", "연표를 쓰면 장면의 시각이 아니다."),
W("장면 밖 설명", "밖으로", "빼기", "Move the fee explanation out of the scene.", "설명은 장면 밖에 둔다.", "장면 한가운데 수수료 정의를 넣으면 자리가 끊긴다."),
W("과한 수식", "하나", "남기기", "The loud fan stayed. The other adjectives went.", "수식은 장면당 하나다.", "수식을 쌓으면 행동이 안 보인다."),
W("장면 끝내기", "마지막", "행동", "Min closed the laptop.", "끝은 행동 하나로 닫는다.", "그리고 모두 행복했다는 요약으로 끝내면 장면이 아니다."),
W("장면 낭독", "소리", "자리", "At the desk, Min closed the laptop.", "소리 내어 읽어 자리가 하나인지 듣는다.", "자리를 옮겨 가며 읽히면 장면이 둘이다."),
W("장면 고치기", "삭제", "자리", "Delete the sentence that leaves the desk.", "자리를 벗어나는 문장을 지운다.", "좋은 문장이라도 자리 밖이면 남기지 않는다."),
W("장면과 요약", "앞", "뒤", "The scene stays. The summary moves below it.", "장면 다음에 요약을 둔다.", "요약을 장면 앞에 두면 자리를 보기 전에 결론이 온다."),
W("장면 점검", "자리", "행동", "One desk, one action, no second place.", "자리 하나와 행동 하나가 남는다.", "자리가 둘이면 장면 점검이 아니다."),
]),
phase(kind("목소리"), 261, 273, "장면", "말투", "누가 말하는지 서술 시점과 어조를 끝까지 일관되게 유지한다.", NOTE, [
W("화자", "누가", "한 명", "Min tells the story. Ana does not narrate.", "서술자(화자)는 한 명으로 고정한다.", "문장마다 서술 시점이 바뀌면 누구의 시선인지 독자가 혼란스러워진다."),
W("거리", "가깝다", "멀다", "Min stood at his own desk.", "서술자가 인물과 얼마나 가까운 거리에서 묘사하는지 일정하게 유지한다.", "책상 앞 인물의 시선으로 묘사하다가 갑자기 전지적 시점으로 뛰어오르면 시점의 거리가 깨진다."),
W("어조의 격식", "표준", "한 결", "Min said the file was late, without slang.", "한 서술자의 격식 수준(Register)을 일관되게 유지한다.", "차분한 표준어 문단 사이에 갑자기 속어가 섞이면 다른 사람이 말한 것처럼 들린다."),
W("말버릇", "반복", "하나", "Min starts answers with Well.", "인물의 특징적인 말버릇은 하나만 써도 충분히 개성이 드러난다.", "말버릇 표현을 다섯 개씩 남발하면 자연스러운 대화가 아니라 과장이 된다."),
W("화자 바꾸기", "표시", "이름", "Then Ana spoke. She asked for the date.", "대화나 발화 주체가 바뀔 때는 이름을 분명히 밝혀 준다.", "이름 표시 없이 대사를 이어 쓰면 누가 묻고 답하는지 알 수 없다."),
W("간접 생각", "thought", "한 줄", "Min thought the date was wrong.", "인물의 속생각은 thought를 활용한 간접화법 한 문장으로 명확히 시작한다.", "속생각과 소리 내어 한 대화를 구분 없이 섞어 쓰면 실제로 말한 것인지 알 수 없다."),
W("독백 네 줄", "네 줄", "까지", "The date is wrong. I should write. Not now. Later.", "내면 독백은 네 문장 이내로 짧게 끊어 긴장감을 유지한다.", "독백이 한 문단을 넘어가면 장면의 행동이 멈추어 버린다."),
W("상대 말투", "짧게", "다르게", "Ana's lines are shorter than Min's.", "상대 인물의 대사는 문장 길이와 호흡을 달리해 서술자와 구분한다.", "두 인물의 문장 길이와 어투가 똑같으면 한 사람이 혼자 말하는 것처럼 들린다."),
W("말투 충돌", "고치기", "한 줄", "Rewrite the slang line in Min's plain voice.", "전체 어조에서 튀는 속어 문장 하나를 서술자의 담백한 말투로 고친다.", "어조가 깨지는 문장을 개성이라며 그대로 방치하면 서술자의 목소리가 둘로 갈라진다."),
W("말투 일관", "처음부터", "끝", "The last line still sounds like Min.", "마지막 문장까지 첫 문장의 서술자 어조가 그대로 이어져야 한다.", "글 끝에서 갑자기 딱딱한 논문 투로 바뀌면 글의 일관성이 무너진다."),
W("목소리 녹음", "소리", "화자", "Read Min's lines in one voice.", "서술자의 문장들을 한결같은 톤으로 소리 내어 읽어 본다.", "서술문까지 등장인물 연기하듯 과장해 읽으면 서술과 대사의 구분이 사라진다."),
W("목소리 고치기", "한 줄", "화자", "Change the one line that is not Min.", "서술자의 말투에서 벗어난 한 문장만 정확히 찾아 고친다.", "문단 전체를 새로 다 써 버리면 원래 어느 문장이 어조를 깼는지 비교할 수 없다."),
W("목소리 점검", "한 명", "끝", "Every narration line belongs to Min.", "모든 서술 문장이 한 사람의 일관된 목소리로 읽히는지 확인한다.", "단 한 줄이라도 다른 사람의 말투처럼 튀면 점검을 통과하지 못한다."),
]),
phase(kind("주장 글"), 274, 286, "말투", "주장", "주장 하나, 이유 둘, 반론 하나로 단락을 쓴다.", NOTE, [
W("주장 문장", "하나", "문장", "The review should move to Thursday.", "주장은 한 문장으로 쓴다.", "주장을 두 개 넣으면 글이 둘이다."),
W("이유 둘", "because", "둘", "The room is booked Wednesday. Ana is away Tuesday.", "이유는 두 개까지만 둔다.", "이유를 다섯 개 두면 주장이 묻힌다."),
W("반론 문장", "although", "반대", "Although Friday is free, the file is due earlier.", "반론은 although로 반대 하나를 말한다.", "반론을 빼면 글이 광고처럼 들린다."),
W("반론에 답", "still", "주장", "Friday is free. Still, Thursday meets the due date.", "답은 반론 뒤에도 주장이 남는 이유다.", "반론에서 끝내면 주장이 취소된 것처럼 들린다."),
W("근거 표시", "출처", "어디", "The booking mail on 2 April says the room is taken.", "근거는 어디서 왔는지 표시한다.", "Everyone knows는 출처가 아니다."),
W("과장 빼기", "very", "삭제", "The room is booked, not completely impossible forever.", "very와 절대 표현을 뺀다.", "절대 표현이 남으면 근거보다 소리가 크다."),
W("주장과 사실", "분리", "사실", "The room is booked. I think Thursday is better.", "사실은 주장 앞에 둔다.", "사실을 의견으로 쓰면 예약이 취향처럼 들린다."),
W("결론 먼저", "첫 문장", "주장", "Move the review to Thursday.", "결론을 첫 문장에 둔다.", "결론을 마지막에만 숨기면 독자가 길을 잃는다."),
W("독자에게 요청", "please", "하나", "Please confirm Thursday.", "요청은 하나만 남긴다.", "요청을 세 개 하면 어느 것을 할지 모른다."),
W("주장 단락", "네 문장", "틀", "Thursday works. The room is taken. Ana is away. Please confirm.", "단락은 주장, 이유, 반론 또는 요청이다.", "일화를 길게 넣으면 주장 단락이 아니다."),
W("주장 말하기", "60초", "하나", "Say the claim, two reasons, and one request.", "60초 안에 주장 하나를 말한다.", "60초에 주제를 바꾸면 주장이 둘이다."),
W("주장 고치기", "하나", "남기기", "Delete the second recommendation.", "주장이 둘이면 하나를 지운다.", "둘 다 좋은 문장이라도 하나를 남긴다."),
W("주장 점검", "요청", "하나", "The paragraph asks for Thursday and nothing else.", "요청이 주장과 같은 날이다.", "요청이 다른 날이면 점검이 아니다."),
]),
phase(kind("구체와 어조"), 287, 299, "주장", "어조", "추상어를 구체로 바꾸고 독자에 맞게 어조를 맞춘다.", NOTE, [
W("추상어 바꾸기", "thing", "이름", "Replace the issue with the missing date.", "추상 명사는 셀 수 있는 이름으로 바꾼다.", "issue, thing, aspect를 두면 무엇이 빠졌는지 모른다."),
W("숫자 넣기", "몇", "날짜", "The file is 12 pages and is due on 28 March.", "구체는 숫자와 날짜다.", "곧, 많이, 조금은 숫자가 아니다."),
W("고유 이름", "이름", "파일", "March Review is late. The document is not a name.", "파일과 사람에게 고유 이름을 붙인다.", "the document만 반복하면 어느 파일인지 모른다."),
W("감각 어조", "하나", "소리", "The fan hummed. That is the only sensory line.", "감각 어조는 문단당 한 줄이다.", "감각을 쌓으면 주장이 분위기에 묻힌다."),
W("공식 어조", "please", "이름", "Please send March Review by Friday.", "공식 어조는 부탁과 이름과 기한이다.", "Hey, send it는 공식 어조가 아니다."),
W("가까운 어조", "이름", "짧게", "Ana, I will send it Friday.", "가까운 어조는 이름과 짧은 문장이다.", "가까운 사이인데 조항 번호를 늘어놓으면 거리가 멀어진다."),
W("어조 충돌", "한 줄", "고치기", "Rewrite the joke in the formal note.", "공식 문서에 섞여 들어간 가벼운 농담 한 줄을 격식에 맞게 고친다.", "격식 있는 문서에 농담을 재미 삼아 남겨 두면 글의 어조가 두 갈래로 깨진다."),
W("독자 호칭", "you", "이름", "Use Ana in the mail, and you in the note.", "독자를 부르는 호칭 방식은 글 하나 안에서 일관되게 유지한다.", "같은 글 안에서 친근한 이름과 격식 호칭(sir)을 섞어 쓰면 거리감이 흔들린다."),
W("유머 한 줄", "하나", "뿐", "One dry line is enough, and it must not hide the date.", "가벼운 위트는 한 줄이면 충분하며 핵심 기한 정보를 가리지 않아야 한다.", "농담으로 마감 기한 안내를 대신하면 정작 전달해야 할 구체적 정보가 사라진다."),
W("어조 맞추기", "독자", "하나", "The whole note speaks to Ana in one register.", "글 전체가 한 명의 독자를 향해 일관된 격식(Register)을 유지해야 한다.", "문단마다 예상 독자와 말투가 바뀌면 통일된 글이 되지 못한다."),
W("구체 고치기", "추상", "삭제", "Delete aspect and write the page count.", "aspect 같은 모호한 추상어를 지우고 구체적인 쪽수로 바꾼다.", "추상어를 그대로 둔 채 수식어만 늘리면 글이 구체화되지 않는다."),
W("어조 낭독", "소리", "높이", "Read the note and mark the one line that changes height.", "소리 내어 읽으며 격식 수준이 갑자기 달라지는 문장을 찾아 표시한다.", "눈으로만 읽으면 어조가 튀는 농담 한 줄을 그냥 지나치기 쉽다."),
W("어조 점검", "이름", "숫자", "Ana, the 12-page file, and Friday are all in the note.", "이름, 숫자, 기한이 한 어조 안에 있다.", "하나라도 추상어로 남으면 점검이 아니다."),
]),
phase(kind("초고 고치기"), 300, 312, "어조", "교정", "하루 지난 초고를 구조부터 고친다.", NOTE, [
W("하루 거리", "어제", "다시", "Read yesterday's draft before changing a word.", "고치기 전에 하루 지난 초고를 읽는다.", "쓰자마자 고치면 방금의 의도가 글처럼 보인다."),
W("구조 표시", "일", "여백", "Mark each paragraph with its job in the margin.", "단어보다 단락의 일을 먼저 표시한다.", "쉼표부터 고치면 구조가 남는다."),
W("군더더기", "삭제", "목적", "Delete the sentence that does not serve the job.", "목적 밖 문장을 지운다.", "예쁜 문장을 남기는 것이 교정이 아니다."),
W("빠진 단계", "사이", "추가", "Add the step between opening the file and sending it.", "단계가 비면 그 사이만 추가한다.", "빠진 단계 옆에 새 주제를 넣으면 구멍이 아니다."),
W("반복 단어", "두 번", "하나", "File appears twice. Keep one.", "같은 명사가 같은 뜻으로 두 번이면 하나를 지운다.", "반복을 강조로 착각하면 군더더기가 남는다."),
W("끝 다듬기", "마지막", "요청", "The last sentence asks Ana to confirm Friday.", "끝 문장은 요청이나 결과다.", "끝에서 새 일화를 열면 글이 안 끝난다."),
W("제목 다시", "일", "제목", "Title the note Missing date, not Thoughts.", "제목은 그 글의 일이다.", "제목이 감상어면 일을 가린다."),
W("첫 문단", "결론", "먼저", "The first paragraph states the new date.", "첫 문단이 결론을 말한다.", "첫 문단이 일대기면 결론이 늦다."),
W("피드백 하나", "한 가지", "반영", "Use one comment: the date is hard to find.", "피드백은 한 가지를 고친다.", "댓글을 모두 한꺼번에 반영하면 어느 고침인지 모른다."),
W("반영 표시", "고침", "이유", "I moved the date up because Ana could not find it.", "고친 곳과 이유를 한 줄 남긴다.", "고쳤다는 말만 있으면 어디인지 모른다."),
W("소리 교정", "낭독", "걸림", "Read aloud and mark the one place you stumble.", "걸리는 곳 하나만 고친다.", "안 걸리는 문장까지 다시 쓰면 교정 범위가 글 전체가 된다."),
W("버전 둘", "v1", "v2", "Keep v1. Save the revision as v2.", "옛 버전을 지우지 않는다.", "덮어쓰면 무엇을 고쳤는지 비교할 수 없다."),
W("교정 점검", "일", "끝", "The revised note states the date and asks for Friday.", "고친 글이 원래의 일을 한다.", "일이 바뀌었으면 교정이 아니라 다른 글이다."),
]),
phase(kind("책의 구조"), 313, 325, "교정", "구조", "짧은 글의 장 순서와 구조 메모를 남긴다. 포트폴리오는 이 메모를 쓴다.", BOOK, [
W("책의 질문", "하나", "질문", "The book asks how a late file gets to Ana.", "책의 질문은 하나만 둔다.", "질문이 둘이면 책이 둘이다."),
W("장 제목", "일", "제목", "Chapter 1 is The missing date.", "장 제목은 그 장의 일이다.", "Chapter 1 Introduction은 일이 없다."),
W("장의 일", "하나", "장", "This chapter only shows the missing date.", "장은 일 하나만 맡는다.", "한 장에 수수료와 여행을 넣으면 일이 둘이다."),
W("장 연결", "앞", "뒤", "Chapter 2 starts from the date chapter 1 found.", "다음 장은 앞 장의 결과에서 시작한다.", "장마다 새로 시작하면 연결이 없다."),
W("독자 약속", "끝", "얻을것", "By the end, the reader can list the three steps.", "서두의 약속은 끝이 지키는지 본다.", "약속을 바꾸면 구조가 바뀐다."),
W("예시의 자리", "장", "하나", "Each chapter holds one example.", "예시는 장마다 하나다.", "한 장에 예시를 넷 두면 일이 넷이다."),
W("요약 장", "마지막", "질문", "The last chapter answers the book's question.", "마지막 장은 처음의 질문에 답한다.", "마지막 장이 새 질문이면 요약이 아니다."),
W("주석의 일", "출처", "본문", "A note names the mail. It does not add a new claim.", "주석은 출처만 말한다.", "주석에서 새 주장을 하면 본문이 둘이다."),
W("서문", "질문", "독자", "This book is for Ana, and it asks one question.", "서문은 독자와 질문이다.", "서문이 자서전이면 질문이 없다."),
W("목차 낭독", "제목", "순서", "Read the chapter titles in order.", "목차만 읽어도 질문의 순서가 들려야 한다.", "제목이 감상이면 순서가 안 들린다."),
W("구조 메모", "메모", "이유", "Write why chapter 2 follows chapter 1.", "구조 메모는 순서의 이유다. 이 메모를 포트폴리오가 나중에 쓴다.", "느낌상 이 순서다는 이유가 아니다."),
W("장 옮기기", "질문", "순서", "Move the fee chapter after the date, because the question starts with the date.", "질문의 순서에 맞게 장을 옮긴다.", "쓴 순서를 지키려고 질문을 고치면 구조가 아니다."),
W("구조 점검", "질문", "목차", "The table of contents answers one question in order.", "목차가 질문 하나에 답한다.", "목차에 다른 질문이 있으면 구조 점검이 아니다."),
]),
phase(kind("인물과 산문"), 326, 338, "구조", "산문", "인물 하나의 원하는 것과 장애로 한 쪽을 쓴다.", NOTE, [
W("인물 한 줄", "누구", "한 명", "Min is the person who has to send the file.", "인물은 한 줄로 누구인지 말한다.", "인물을 셋 소개하면 한 쪽의 인물이 아니다."),
W("원하는 것", "want", "하나", "Min wants the file to reach Ana today.", "원하는 것은 하나만 둔다.", "원하는 것이 둘이면 이야기가 둘이다."),
W("장애", "막힘", "하나", "The date on the file is wrong.", "장애는 원하는 것을 막는 하나다.", "장애를 성격 설명으로 바꾸면 막힘이 없다."),
W("선택", "둘", "고름", "Min can wait, or Min can send a note about the date.", "선택은 두 갈래로 적는다.", "선택의 결과가 미리 정해져 있으면 선택이 아니다."),
W("변화", "전", "후", "Before, Min hid the date. After, Min wrote it in the first line.", "변화는 전과 후로 적는다.", "성격이 훌륭하다는 말은 변화가 아니다."),
W("산문 첫 쪽", "쪽", "하나", "The first page ends when Min chooses.", "첫 쪽은 선택에서 끝난다.", "첫 쪽에 결말까지 넣으면 쪽이 아니다."),
W("쪽의 끝", "행동", "끊기", "Min opened a new message and stopped.", "쪽의 끝은 행동에서 끊는다.", "그 뒤로 오래 행복했다는 문장으로 넘기면 끝이 아니다."),
W("시간 건너뛰기", "later", "표시", "Later that afternoon, the reply came.", "건너뛴 시간은 later로 표시한다.", "표시 없이 저녁으로 넘어가면 독자가 순간을 잃는다."),
W("되돌아오기", "다시", "장애", "The wrong date returned in Ana's reply.", "되돌아옴은 같은 장애가 다시 나타나는 것이다.", "새 인물의 새 문제는 되돌아옴이 아니다."),
W("인물 대화", "원하는것", "말", "Min said, The date is wrong, and I am sending it anyway.", "대화는 원하는 것을 드러낸다.", "대화가 날씨뿐이면 인물의 일이 아니다."),
W("산문 낭독", "10분", "쪽", "Read the page aloud in ten minutes or less.", "한 쪽을 10분 안에 읽는다.", "10분을 넘기면 쪽이 아니다."),
W("쪽 고치기", "장애", "하나", "Keep the wrong date and delete the second problem.", "장애가 둘이면 하나를 지운다.", "둘 다 재미있어도 한 쪽에는 하나를 남긴다."),
W("산문 점검", "원함", "장애", "The page shows one want and one obstacle.", "원하는 것과 장애가 하나씩이다.", "둘 중 하나가 없으면 산문 점검이 아니다."),
]),
phase(kind("세 편의 글"), 339, 351, "산문", "세 편", "서로 다른 일 세 편을 쓰고 한 편을 고른다.", NOTE, [
W("글감 셋", "셋", "다름", "A date note, a desk scene, and a Thursday claim.", "세 글감은 일이 다르다.", "같은 일을 제목만 바꾸면 세 편이 아니다."),
W("첫째 개요", "여섯", "일", "Reader, date, two facts, request, close.", "첫째 편의 개요는 일 여섯 개다.", "개요 없이 초고를 시작하면 일이 흔들린다."),
W("첫째 초고", "한 장", "끝", "Finish a one-page draft of the date note.", "초고는 한 장에서 끝낸다.", "한 장 중간에 둘째 편으로 넘어가면 초고가 아니다."),
W("둘째 개요", "장면", "자리", "Desk, one action, one sound, stop.", "둘째 편은 장면 개요다.", "둘째 개요를 첫째와 같게 쓰면 다른 편이 아니다."),
W("둘째 초고", "쪽", "끝", "Finish the desk page and stop at the action.", "둘째 초고는 행동에서 끝난다.", "설명문 결론을 붙이면 장면이 설명문이 된다."),
W("셋째 개요", "주장", "요청", "Thursday, two reasons, one request.", "셋째 편은 주장 개요다.", "셋째 개요에 장면을 넣으면 일이 섞인다."),
W("셋째 초고", "요청", "끝", "End the claim with Please confirm Thursday.", "셋째 초고는 요청으로 끝난다.", "일화로 끝내면 주장 글이 아니다."),
W("세 편의 차이", "일", "셋", "One explains, one shows a desk, one asks for Thursday.", "세 편의 일이 서로 다르다.", "차이가 형용사뿐이면 같은 글이다."),
W("공통 독자", "Ana", "셋", "Ana can read all three.", "독자는 같아도 일은 다르다.", "독자까지 바꾸면 차이가 일이 아니라 청중이다."),
W("한 편 고르기", "하나", "이유", "Choose the date note because the question needs it.", "고르는 이유는 일의 필요다.", "더 잘 썼다는 이유만이면 구조와 무관하다."),
W("고른 편 늘리기", "두 배", "일", "Double the chosen piece without adding a second job.", "늘려도 일은 하나만 남는다.", "늘리면서 다른 편을 끼워 넣으면 세 편이 한 편이 된다."),
W("세 편 낭독", "차례", "차이", "Read the openings and hear three different jobs.", "첫 문장만 읽어도 일이 다르게 들려야 한다.", "첫 문장이 같으면 차이가 없다."),
W("세 편 점검", "고른편", "하나", "One piece is chosen, and the other two stay as they are.", "고른 편 하나만 늘린다.", "세 편을 모두 합치면 점검이 아니다."),
]),
phase(kind("글 포트폴리오"), 352, 364, "세 편", "묶음", "책의 구조 단계에서 남긴 메모로 고른 글을 묶는다.", BOOK, [
W("글 고르기", "기준", "질문", "Choose pieces that answer the book's one question.", "기준은 책의 질문이다.", "분량이 길다는 이유로 고르면 질문이 없다."),
W("구조 메모 붙이기", "메모", "순서", "Attach the structure note that says why this piece is chapter 1.", "순서는 책의 구조 단계에서 남긴 메모를 따른다.", "메모 없이 쓴 순서로 묶으면 구조가 아니다."),
W("묶음 순서", "질문", "앞뒤", "The date piece comes before the request.", "질문의 원인 다음에 요청을 둔다.", "가장 잘 쓴 글을 무조건 앞에 두면 질문이 끊긴다."),
W("머리말", "독자", "질문", "This set is for Ana and asks how the file arrives.", "머리말은 독자와 질문이다.", "머리말이 감사 인사뿐이면 질문이 없다."),
W("글마다 한 줄", "일", "한줄", "Under each piece, write the one job it does.", "한 줄은 그 글의 일이다.", "한 줄이 감상평이면 일이 아니다."),
W("고친 문장 모음", "네 문장", "전후", "Keep four sentences with the old line and the new line.", "모음은 고치기 전과 후다.", "고친 문장만 있으면 무엇이 달라졌는지 없다."),
W("묶음 낭독", "머리말", "목차", "Read the preface and the list of jobs aloud.", "낭독은 머리말과 일의 목록이다.", "본문 전체를 한 번에 읽으면 묶음이 아니라 긴 초고다."),
W("피드백 반영", "한 가지", "질문", "Use the comment that says the question is easy to miss.", "반영은 질문이 보이게 하는 한 가지다.", "맞춤법만 고치면 구조 메모를 쓴 것이 아니다."),
W("묶음 목차", "제목", "일", "List titles and jobs: date, desk, Thursday.", "목차는 제목과 일이다.", "쪽 번호만 있으면 목차가 아니다."),
W("표지 문장", "질문", "한문장", "How does a late file reach Ana?", "표지 문장은 책의 질문이다.", "표지가 저자 소개면 질문이 없다."),
W("빠진 글", "질문", "구멍", "Add a piece only if the question has a hole.", "질문은 답하는데 단계가 없을 때만 글을 더한다.", "더 넣고 싶어서 더하면 질문이 흐려진다."),
W("묶어 읽기", "순서", "메모", "Read in the order the structure note gives.", "읽는 순서는 구조 메모의 순서다.", "순서를 무시하고 마음에 드는 글부터 읽으면 묶음이 아니다."),
W("포트폴리오 점검", "메모", "질문", "The set follows the structure note and answers one question.", "책의 구조 단계에서 남긴 메모와 질문 하나가 맞다.", "메모와 다른 순서면 포트폴리오 점검이 아니다."),
]),
]
