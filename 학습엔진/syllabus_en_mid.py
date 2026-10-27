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

SPEAK["가정과 소리"] = "{pattern} 현실과 다른 일 세 가지를 60초 말한다. 첫 문장: {model}"
WRITE["가정과 소리"] = "{trap} 그 틀린 꼴을 바른 가정 네 문으로 고치고, if와 결과 동사에 밑줄을 긋는다."
SPEAK["차트와 후속"] = "{pattern} 차트의 숫자만 보고 60초 말한다. 첫 문장: {model}"
WRITE["차트와 후속"] = "{trap} 빠진 축이나 숫자를 채워 메일 여섯 줄을 쓴다. 본문에 {model}"
SPEAK["계약 초안"] = "{pattern} 보고서 초안을 소리 내어 60초 읽는다. 들을 문장: {model}"
WRITE["계약 초안"] = "{trap} 빈칸을 채운 초안 여섯 줄을 쓴다. 남길 문장: {model}"
SPEAK["거래 하나"] = "{pattern} 서버 유지 사실만 60초 말한다. 사실 문장: {model}"
WRITE["거래 하나"] = "{trap} 바람이 섞이지 않은 사실 여섯 줄을 쓴다. 앵커: {model}"
SPEAK["문장 협상"] = "{pattern} 번역 분량 협상을 60초 말한다. 시작: {model}"
WRITE["문장 협상"] = "{trap} 양보 하나와 대안 하나가 있는 메일 여섯 줄을 쓴다. 숫자 문장: {model}"
SPEAK["긴 글 읽기"] = "{pattern} 워크숍 안내의 해당 줄만 60초 읽는다. 줄: {model}"
WRITE["긴 글 읽기"] = "{trap} 날짜와 금액을 표로 모아 여섯 줄로 적는다. 기준 줄: {model}"
SPEAK["정의와 참조"] = "{pattern} 용어 하나를 정의로 되돌려 60초 말한다. 정의: {model}"
WRITE["정의와 참조"] = "{trap} 용어, 뜻, 조항 번호가 있는 네 줄을 쓴다. 바로잡을 문장: {model}"
SPEAK["문장 수정"] = "{pattern} 인쇄 일정의 고친 곳만 60초 읽는다. 고친 문장: {model}"
WRITE["문장 수정"] = "{trap} 지운 말과 넣은 말과 이유를 여섯 줄로 적는다. 대상: {model}"
SPEAK["위험 문장"] = "{pattern} 카메라 대여 문장의 위험한 단어를 60초 말한다. 문장: {model}"
WRITE["위험 문장"] = "{trap} 그 단어를 날짜나 행동으로 바꾼 네 줄을 쓴다. 연습 문장: {model}"

SOUND = "녹음기. English Grammar in Use의 가정법 단원. 카드에는 영어만 적는다."
CHART = "녹음기. 직접 그린 차트 하나. 카드에는 영어만 적는다."
DRAFT = "녹음기. 자신이 만든 가상 거래. 이 문장은 법률 자문이 아니며 실제 계약에 쓰지 않는다."

MID = [
phase(kind("가정과 소리"), 66, 78, "메일", "가정", "현실과 다른 조건을 말하고, 들은 안내를 받아쓴다.", SOUND, [
W("과거 가정", "if", "would", "If I had time, I would call you.", "if 절은 과거형, 결과는 would다. 지금 사실과 반대다.", "If I would have time는 if 안에 would를 넣은 형태다."),
W("먼 과거 가정", "had", "would have", "If I had known, I would have stayed.", "had와 would have는 이미 지난 일과 반대다.", "If I knew, I would have stayed는 두 시제를 섞는다."),
W("unless", "아니면", "결과", "Unless you reply, I will wait here.", "unless는 if not 한 덩어리다.", "Unless you will reply는 unless 안에 will을 넣는다."),
W("wish", "아쉬움", "과거", "I wish I had the file today.", "wish 뒤에는 원하는 상태가 과거형으로 온다.", "I wish I have the file는 현재형을 그대로 둔다."),
W("rather", "선택", "than", "I would rather meet on Tuesday than on Monday.", "rather 뒤에는 동사 원형, than 뒤에 비교 대상이 온다.", "I would rather to meet는 to를 더한다."),
W("제안 한 가지", "let us", "동사", "Let us move the call to Thursday.", "제안은 let us와 동사 원형 하나다.", "Let us to move는 to를 더한다."),
W("약한 추측", "might", "so", "It might rain, so I will bring a coat.", "might는 약한 추측이고 so 뒤에 행동을 둔다.", "It might to rain는 to를 더한다."),
W("th 소리", "think", "third", "I think the third date is Thursday.", "th는 s와 다르게 혀를 가볍게 낸다.", "think를 sink로 말하면 다른 단어가 된다."),
W("정보 강세", "notes", "slides", "I sent the notes, not the slides.", "고친 단어에만 강세를 둔다.", "모든 단어에 같은 강세를 주면 어느 단어가 정정인지 안 들린다."),
W("안내 두 문장", "from", "to", "The meeting moved from Monday to Wednesday at 2.", "from과 to로 옛 시점과 새 시점을 받아쓴다.", "요일만 적고 at 2를 빼면 안내가 반이다."),
W("however", "대조", "문장", "The room is small. However, it is quiet.", "However는 새 문장에서 대조를 연다.", "The room is small however it is quiet는 두 절을 접속 없이 붙인다."),
W("3분 이야기", "so", "과거", "Yesterday I missed the bus, so I walked.", "3분은 한 사건과 so로 잇는 결과다.", "주제를 두 개 넣으면 3분이 이야기 둘이 된다."),
W("가정 점검", "were", "would", "If I were free on Friday, I would join.", "가정과 결과의 시제가 맞으면 점검이 끝난다.", "If I am free on Friday, I would join은 현실 조건과 가정이 섞인다."),
]),
phase(kind("차트와 후속"), 92, 104, "회의", "차트", "차트 하나를 문장으로 읽고, 그 문장으로 후속 메일을 쓴다.", CHART, [
W("축 읽기", "가로", "세로", "The horizontal axis is the week, and the vertical axis is calls.", "축 이름과 단위를 먼저 말한다.", "축을 말하지 않고 숫자만 읽으면 차트가 아니다."),
W("증가 문장", "rose", "from", "Calls rose from 8 to 12.", "rose from A to B는 증가의 시작과 끝이다.", "Calls rose 12는 시작점이 없다."),
W("감소 문장", "fell", "to", "Calls fell from 12 to 9.", "fell from A to B는 감소다. 방향이 바뀌면 rose를 쓰지 않는다.", "fell up은 방향이 모순이다."),
W("막대 비교", "higher", "than", "Tuesday was higher than Monday.", "두 막대는 higher than으로 비교한다.", "Tuesday was higher는 비교 대상이 없다."),
W("비율 한 문장", "percent", "of", "Calls were 40 percent of the week's total.", "percent of 뒤에 전체가 온다.", "40 percent만 말하면 무엇의 비율인지 모른다."),
W("추세 한 문장", "over", "week", "Calls rose over the week, then fell on Friday.", "추세는 방향과 꺾인 지점 하나다.", "요일 숫자를 전부 읽으면 추세가 아니라 목록이다."),
W("차트 질문", "why", "which", "Which day was the highest, and why did it fall?", "질문은 최고점과 이유 하나다.", "차트 질문을 다섯 개 던지면 듣는 사람이 어디를 볼지 모른다."),
W("후속 첫 줄", "thanks", "today", "Thanks for today's review. I am writing about the chart.", "후속 메일의 첫 줄은 어느 회의인지 말한다.", "Hello만 쓰면 어느 차트인지 모른다."),
W("기한 다시", "by", "Friday", "Could you confirm the numbers by Friday?", "기한은 by와 요일 하나다.", "Could you confirm the numbers는 기한이 없다."),
W("첨부 안내", "attached", "chart", "The chart is attached.", "첨부 문장은 파일의 내용이 무엇인지 말한다.", "See attached만 쓰면 무엇이 붙었는지 모른다."),
W("할 일 세 줄", "action", "owner", "Ana will check Tuesday. I will redraw Friday.", "할 일은 사람과 행동이다.", "Check the chart는 누가 하는지 없다."),
W("차트 2분", "점", "숫자", "Calls rose from 8 to 12, then fell to 9.", "2분은 점 하나와 숫자 둘이다.", "숫자를 모두 읽으면 2분이 표를 베낀 것이다."),
W("차트 메일 점검", "문장", "부탁", "Calls rose from 8 to 12. Could you confirm that by Friday?", "메일 부탁이 차트 문장과 같은 숫자를 말한다.", "메일이 다른 주 숫자를 말하면 점검이 아니다."),
]),
phase(kind("계약 초안"), 118, 130, "읽기", "초안", "가상 거래의 당사자, 기간, 대금을 문장으로 초안한다. 법률 자문이 아니다.", DRAFT, [
W("당사자 이름", "between", "and", "This draft is between Ana Kim and Min Park.", "당사자는 이름 둘과 between이다.", "This draft is between the parties는 이름이 없다."),
W("목적 문장", "to", "동사", "The purpose is to design one report.", "목적은 to와 동사 하나다.", "The purpose is the report는 동작이 없다."),
W("기간을 날짜로", "from", "until", "The work runs from 3 March until 28 March.", "기간은 시작 날짜와 끝 날짜다.", "The work runs for a while는 날짜가 없다."),
W("대금 문장", "amount", "for", "The fee is 500 dollars for the report.", "대금은 금액과 무엇에 대한 값인지다.", "The fee is 500은 무엇의 값인지 없다."),
W("지급일", "on", "date", "Payment is due on 31 March.", "지급일은 on과 날짜 하나다.", "Payment is due soon은 날짜가 아니다."),
W("인도 문장", "deliver", "by", "Min will deliver the file by 28 March.", "인도는 누가, 무엇을, 언제까지다.", "The file will be delivered는 누가 하는지 없다."),
W("정의 한 칸", "means", "용어", "Report means the written file named March Review.", "정의는 용어와 means와 가리키는 것이다.", "Report means the work는 범위가 문장 없이 열린다."),
W("서로 할 일", "will", "각각", "Ana will send the data. Min will write the report.", "양쪽의 will이 각각 하나의 행동만 말한다.", "The parties will cooperate는 행동이 없다."),
W("통지 방법", "by email", "주소", "Notices go by email to ana@example.com.", "통지는 방법과 주소다.", "Notices go by email은 주소가 없다."),
W("서명란", "name", "date", "Name, date, and signature sit at the end.", "서명란은 이름, 날짜, 서명 자리다.", "서명만 있고 날짜가 없으면 언제 서명했는지 없다."),
W("초안 낭독", "소리", "빠짐", "The fee is 500 dollars, due on 31 March.", "소리 내어 읽으며 금액과 날짜가 들리는지 본다.", "눈으로만 보면 빠진 날짜를 지나친다."),
W("빠진 날짜", "빈칸", "채우기", "The end date is 28 March, not a blank.", "빈 날짜는 문장을 고치기 전에 채운다.", "나중에 적는다 하고 빈칸을 두면 초안이 아니다."),
W("초안 점검", "이름", "금액", "Ana Kim and Min Park agree on 500 dollars, due on 31 March.", "이름, 금액, 날짜가 한 문단에 있다.", "셋 중 하나가 빠지면 초안 점검이 아니다."),
]),
phase(kind("거래 하나"), 131, 143, "초안", "사실", "서버 유지 하나의 사실만 모아 문장으로 고정한다. 보고서 초안의 금액과 날짜는 가져오지 않는다. 법률 자문이 아니다.", DRAFT, [
W("사실 여섯", "사실", "목록", "Lea starts Mail Host on 1 June.", "사실은 관찰할 수 있는 행동이다.", "We hope the server stays up은 사실이 아니라 바람이다."),
W("사실과 바람", "hope", "분리", "The monthly fee is 200 dollars. I hope the invoice is short.", "희망 문장은 사실 목록 밖에 둔다.", "희망 문장을 요금 옆에 붙이면 200달러가 희망처럼 들린다."),
W("할 일 문장", "task", "하나", "Northwind keeps Mail Host running and nothing else.", "할 일은 서비스 하나의 이름이다.", "Northwind handles the account는 서비스 이름이 없다."),
W("일정표", "row", "날짜", "Start on 1 June. Review on 1 December. End on 31 May.", "일정표는 서비스와 날짜의 행이다.", "June만 쓰면 어느 날인지 없다."),
W("대금표", "fee", "때", "200 dollars on the first of each month, twelve times.", "대금표는 월 금액과 횟수다.", "2400 dollars total은 언제 내는지 없다."),
W("지연 한 줄", "late", "결과", "If an invoice is late, Lea may pause Mail Host after seven days.", "지연의 결과는 멈추는 서비스다.", "If an invoice is late, we will see는 결과가 없다."),
W("변경 절차", "write", "먼저", "A change of plan is an email sent before the month starts.", "변경은 글과 시점이다.", "We can change the plan later는 절차가 없다."),
W("연락 창구", "one", "person", "Lea is the only contact for Mail Host.", "창구는 사람 한 명이다.", "The desk will answer는 누가 답하는지 없다."),
W("산출물 이름", "file", "이름", "The service name is Mail Host.", "이름은 서비스 하나다.", "The service는 이름이 없다."),
W("검수 시점", "review", "days", "Lea checks uptime within seven days of each month.", "검수는 사람과 기간이다.", "Lea checks uptime은 기간이 없다."),
W("거래 요약", "여섯", "문장", "Mail Host, 200 dollars a month, from 1 June until 31 May.", "요약은 서비스, 월 금액, 기간이다.", "요약에 새 서버를 넣으면 사실이 늘어난다."),
W("거래 메일", "사실", "부탁", "Mail Host starts on 1 June. Could you confirm the 200 dollars?", "메일은 이미 정한 사실만 말한다.", "메일에 다른 달 금액을 슬쩍 넣으면 거래 메일이 아니다."),
W("거래 점검", "사실", "빈칸", "Start 1 June, end 31 May, fee 200 dollars a month.", "시작, 끝, 월 금액이 모두 있다.", "셋 중 하나가 비면 거래가 고정되지 않는다."),
]),
phase(kind("문장 협상"), 144, 156, "사실", "합의", "번역 분량에서 양보 하나와 대안 하나로 문장을 고친다. 법률 자문이 아니다.", DRAFT, [
W("양보 하나", "can", "하나만", "I can move the delivery, but not the page count.", "양보는 되는 것 하나와 안 되는 것 하나다.", "양보를 세 개 하면 무엇이 남는지 모른다."),
W("대안 제시", "or", "둘", "12 July for 40 pages, or 19 July for 55 pages.", "대안은 선택지 둘이다.", "선택지를 다섯 개 주면 제안이 아니다."),
W("숫자 다시", "대신", "금액", "I can translate 40 pages instead of 55.", "숫자 제안은 옛 쪽수와 새 쪽수를 같이 말한다.", "I can do fewer pages는 숫자가 없다."),
W("조건 붙이기", "if", "then", "If the glossary arrives on 1 July, I can deliver on 12 July.", "조건이 있어야 약속이 산다.", "I can deliver는 조건이 빠진 약속이다."),
W("거절 뒤 대안", "cannot", "대신", "I cannot finish 55 pages by 12 July. Forty pages works.", "거절 다음에 대안 하나다.", "I cannot finish 55 pages에서 멈추면 협상이 끝난다."),
W("합의 문장", "agree", "on", "We agree on 40 pages, due on 12 July.", "합의는 agree on과 항목 하나다.", "We agree는 무엇에 합의했는지 없다."),
W("미합의", "open", "항목", "The glossary format is still open.", "못 정한 항목은 open이라고 남긴다.", "대충 정한 듯 쓰면 미합의가 합의처럼 보인다."),
W("회의 메모", "said", "next", "Ken said the page count can fall. Next, Ruth sends the 40-page list.", "메모는 말한 것과 다음 행동이다.", "좋은 회의였다는 평만 있으면 메모가 아니다."),
W("고칠 문장", "old", "new", "Change 55 pages to 40 pages.", "고칠 문장은 옛 말과 새 말을 같이 적는다.", "Please fix this는 무엇을 고칠지 없다."),
W("상대 문장", "바꾸기", "그대로", "Keep 12 July. Change only the page count.", "남길 것과 바꿀 것을 가른다.", "문장 전체를 다시 쓰면 합의한 날짜까지 사라진다."),
W("양보의 끝", "여기까지", "금액", "The page count can fall to 40, and no further.", "양보의 끝을 숫자로 말한다.", "I will be flexible는 끝이 없다."),
W("합의 메일", "agree", "다음", "We agree on 40 pages. I will send the list tomorrow.", "메일에는 합의와 다음 행동이 있다.", "Thanks만 쓰면 합의 내용이 없다."),
W("협상 점검", "양보", "합의", "I can move the count to 40 pages. We agree on that count.", "양보 하나와 합의 문장이 같은 숫자를 말한다.", "양보와 합의의 숫자가 다르면 점검이 아니다."),
]),
phase(kind("긴 글 읽기"), 157, 169, "합의", "지도", "워크숍 안내를 목차, 날짜, 돈으로 나눠 읽는다. 법률 자문이 아니다.", DRAFT, [
W("목차 먼저", "heading", "순서", "I read Room, Hours, and Materials before the sentences.", "긴 글은 제목 순서로 먼저 훑는다.", "첫 문단부터 단어마다 멈추면 지도가 없다."),
W("정의로 이동", "term", "means", "When I see Session, I go back to the means line.", "대문자 용어는 정의로 돌아간다.", "단어를 그때의 느낌으로 해석하면 정의와 어긋난다."),
W("조항 번호", "clause", "숫자", "Clause 3 is the room. Clause 4 is the hours.", "번호는 내용의 주소다.", "위의 내용이라고만 쓰면 주소가 없다."),
W("교차 참조", "see", "번호", "See clause 3 for the room.", "참조는 see와 번호다.", "See above는 어디인지 모른다."),
W("날짜 모으기", "list", "달력", "Start 9 April. End 11 April. Pay 18 April.", "날짜만 한곳에 모은다.", "본문에 둔 채 넘어가면 모순을 못 본다."),
W("돈 모으기", "list", "합", "200 dollars for the room plus 80 dollars for materials is 280.", "돈을 모아 합이 본문과 같은지 본다.", "본문의 280과 표의 300을 따로 두면 모순이 남는다."),
W("의무 동사", "will", "표시", "Ruth will open the room. Ken will bring the materials.", "will이 있는 문장만 의무 후보로 표시한다.", "may와 will을 같은 표시로 두면 의무가 늘어난다."),
W("예외 절", "except", "경우", "Ruth will open the room, except when the building is closed.", "except 뒤를 본문과 따로 적는다.", "except를 빼면 예외가 본문처럼 들린다."),
W("첨부 목록", "schedule", "이름", "Schedule A is the room list. Schedule B is the hours.", "첨부는 이름과 번호다.", "첨부라고만 쓰면 어느 표인지 모른다."),
W("긴 문장 끊기", "and", "둘", "Ruth will open the room. Ken will bring the workbook.", "and가 두 의무를 잇으면 문장을 둘로 나눈다.", "한 문장에 의무를 네 개 두면 누가 하는지 흐린다."),
W("요약 열 문장", "열", "사실", "The workshop ends on 11 April.", "요약은 열 문장 안의 사실이다.", "평가를 섞으면 요약이 길어지고 사실이 줄어든다."),
W("질문 목록", "어디", "번호", "Which date in clause 4 is the last hour?", "질문은 조항 번호를 붙인다.", "이게 맞나요는 어디를 묻는지 없다."),
W("긴 글 점검", "날짜", "돈", "The dates match, and the room plus materials add to 280.", "날짜 목록과 돈 합이 본문과 같다.", "둘 중 하나만 보면 점검이 반이다."),
]),
phase(kind("정의와 참조"), 170, 182, "지도", "용어", "워크숍 용어 하나와 그것이 가리키는 조항을 맞춘다. 법률 자문이 아니다.", DRAFT, [
W("정의 문장", "means", "하나", "Session means the three-hour block on 10 April.", "정의는 용어 하나와 가리키는 것 하나다.", "Session means the class and the fee는 정의를 둘로 늘린다."),
W("대문자 용어", "Report", "소문자", "Session means the named block. A session can mean any meeting.", "대문자는 정의된 용어, 소문자는 보통 말이다.", "둘을 같게 읽으면 모든 모임이 워크숍이 된다."),
W("포함", "includes", "목록", "Materials include the workbook and the slides.", "includes 뒤에는 목록이 온다.", "Materials include related items는 목록이 없다."),
W("제외", "exclude", "하나", "Materials exclude Ruth's private notes.", "제외는 빠지는 것 하나다.", "제외 없이 includes만 두면 개인 노트가 교재에 들어갈 수 있다."),
W("기간 정의", "day", "달력", "A day means a calendar day, not a work day.", "기간 단어는 달력인지 영업일인지 정한다.", "day를 느낌으로 두면 사흘이 닷새가 될 수 있다."),
W("조항 가리키기", "clause", "means", "Hours has the meaning in clause 4.", "참조는 용어와 조항 번호다.", "as defined somewhere는 번호가 없다."),
W("첨부 가리키기", "schedule", "표", "Hours have the meaning in Schedule B.", "표의 숫자는 본문이 아니라 첨부를 가리킨다.", "본문에 다른 시간을 또 쓰면 첨부와 싸운다."),
W("모순된 정의", "둘", "다름", "Clause 2 says three hours. Clause 6 says four hours.", "같은 용어의 숫자가 둘이면 모순이다.", "둘 다 맞다고 두면 어느 쪽도 정의가 아니다."),
W("빠진 정의", "용어", "없음", "The word Workshop is capitalized and never defined.", "대문자인데 정의가 없으면 빠진 정의다.", "문맥으로 짐작해 채우면 상대와 다른 뜻이 된다."),
W("순환 정의", "서로", "means", "Start means the start hour, and the start hour means Start.", "정의가 서로를 가리키면 순환이다.", "순환을 풀어 쓰지 않으면 시각이 생기지 않는다."),
W("정의 고치기", "means", "구체", "Workshop means the 9 April to 11 April classes in clause 3.", "고친 정의는 날짜와 조항이다.", "Workshop means workshop은 순환으로 돌아간다."),
W("용어집", "표", "가나다", "Session, three hours on 10 April. Day, calendar day.", "용어집은 용어와 뜻의 표다.", "본문을 용어집 대신 다시 붙여 넣으면 표가 아니다."),
W("정의 점검", "용어", "조항", "Session means the 10 April block in clause 2.", "용어, 뜻, 조항 번호가 한 줄에 있다.", "번호가 빠지면 점검이 아니다."),
]),
phase(kind("문장 수정"), 183, 195, "용어", "수정", "인쇄 일정의 고칠 문장을 이유와 함께 표시한다. 법률 자문이 아니다.", DRAFT, [
W("바꿀 문장", "하나", "고르기", "Change only the ship-date sentence.", "한 번에 문장 하나만 고른다.", "문단 전체를 다시 쓰면 무엇이 바뀌었는지 없다."),
W("삭제 표시", "strike", "옛말", "Strike 2 August.", "삭제는 지우는 말을 보여 준다.", "그냥 지우면 상대가 옛 날짜를 못 본다."),
W("삽입 표시", "insert", "새말", "Insert 9 August.", "삽입은 새 말을 보여 준다.", "새 문장만 보내면 어디가 삽입인지 모른다."),
W("이유 한 줄", "because", "합의", "Because the paper arrived on 4 August.", "이유 한 줄이 수정 옆에 있다.", "이유 없이 날짜만 바꾸면 상대가 근거를 모른다."),
W("레드라인 묶음", "묶음", "세 곳", "Three ship lines change from 2 August to 9 August.", "같은 이유의 수정은 한 묶음이다.", "같은 수정을 메일 세 통에 나누면 묶음이 아니다."),
W("상대 수정", "읽기", "표시", "Omar struck soon and inserted 9 August.", "상대의 삭제와 삽입을 그대로 읽는다.", "상대 수정을 내 말로 요약만 하면 단어를 놓친다."),
W("수정 수용", "accept", "날짜", "I accept the ship date 9 August.", "수용은 항목을 말한다.", "I accept everything은 어느 수정인지 없다."),
W("수정 거절", "reject", "이유", "I reject the new quantity because the table still says 300 copies.", "거절에는 이유 하나가 있다.", "I reject this는 이유가 없다."),
W("버전 이름", "v2", "날짜", "Call this file Print v2, 5 August.", "버전은 번호와 날짜다.", "final이라고만 쓰면 어느 날의 final인지 없다."),
W("변경 요약", "세 줄", "목록", "Ship 9 August. Copies 300. Title unchanged.", "요약은 바뀐 것과 안 바뀐 것이다.", "많이 고쳤다는 한 줄은 요약이 아니다."),
W("고친 문장 낭독", "소리", "숫자", "The books ship on 9 August, 300 copies.", "소리 내어 읽어 옛 날짜가 남아 있는지 듣는다.", "눈으로만 보면 2 August가 한 줄 남아도 지나친다."),
W("수정 메일", "첨부", "요약", "Print v2 is attached. The ship date is now 9 August.", "메일은 버전과 바뀐 점이다.", "Please see attached만 쓰면 무엇이 바뀌었는지 없다."),
W("수정 점검", "묶음", "이유", "The three ship lines say 9 August because the paper was late.", "묶음의 날짜가 이유와 같다.", "한 줄만 9 August이고 나머지가 2 August면 점검이 아니다."),
]),
phase(kind("위험 문장"), 196, 208, "수정", "위험", "카메라 대여 문장에서 비거나 한쪽으로 열린 말을 표시하고 대체 문장을 쓴다. 법률 자문이 아니다.", DRAFT, [
W("모호한 기간", "soon", "날짜", "Replace soon with 9 August.", "soon은 날짜가 아니다.", "soon을 합의로 두면 사람마다 다른 날이다."),
W("열린 의무", "help", "행동", "Replace help with return the camera to the studio door.", "help는 행동이 아니다.", "열린 동사를 두면 의무의 끝이 없다."),
W("자동 갱신", "renew", "끝", "The loan ends on 9 August and does not renew.", "끝나려면 갱신하지 않는다고 적는다.", "자동으로 이어진다고 두면 반납 날짜가 사라진다."),
W("일방 변경", "alone", "금지", "Neither side changes the pickup place alone.", "변경은 양쪽이 필요하다.", "Nia may change the pickup place alone은 한쪽만 연다."),
W("배타 문장", "only", "자리", "Nia borrows only this camera.", "only의 자리를 문장에서 찾는다.", "only를 빼면 다른 장비까지 대여처럼 들릴 수 있다."),
W("한도 문장", "cap", "금액", "The cap in this practice sentence is 300 dollars.", "한도는 금액이다. 이 문장은 연습이다.", "한도 없이 unlimited를 두면 숫자가 없다."),
W("비밀 기간", "until", "날짜", "Return the camera by 9 August.", "반납은 끝나는 날짜가 있다.", "Return the camera는 끝이 없다."),
W("관할 문장", "어디", "도시", "This practice names Busan as the place of pickup.", "어디서 받을지는 도시 이름이다. 법률 선택이 아니다.", "somewhere appropriate는 도시가 아니다."),
W("모호한 인도", "appropriate", "방법", "Hand the camera to the studio door, not by an appropriate method.", "appropriate method는 방법이 아니다.", "방법 없는 반납은 받았는지 확인할 길이 없다."),
W("조건 없는 보장", "guarantee", "조건", "I do not guarantee the photos. I will return the camera.", "결과 보장과 장비 반납을 가른다.", "I guarantee great photos는 조건 없는 결과다."),
W("위험 표시", "표시", "이유", "Mark soon, because it has no date.", "위험 표시는 단어와 이유다.", "그냥 위험하다고 하면 어느 단어인지 모른다."),
W("대체 문장", "instead", "날짜", "Write by 9 August instead of soon.", "대체 문장은 위험한 말 자리에 들어간다.", "새 문장을 옆에만 두고 옛 말을 남기면 둘 다 산다."),
W("위험 점검", "세 단어", "대체", "soon, help, and appropriate each have a replacement.", "위험 단어 셋이 모두 대체된다.", "하나라도 본문에 남으면 점검이 아니다."),
]),
]
