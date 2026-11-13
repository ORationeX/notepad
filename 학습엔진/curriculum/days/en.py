# -*- coding: utf-8 -*-
"""English (en) 7-day plan builder and duration/take thickening helpers."""
import json
import re

from curriculum.common import day, day_title, focus_line, particle_eul, with_focus


def thicken_english_week(week):
    """Preserved weeks keep their own days. Normalize review blocks to 10m and fill short takes."""
    week = json.loads(json.dumps(week))
    for one in week["days"]:
        blocks = one["blocks"]
        mins = [b["m"] for b in blocks]
        if mins == [5, 15, 30, 10]:
            blocks[0]["m"] = 10
            blocks[2]["m"] = 25
        elif mins == [20, 25, 10, 5]:
            cue = focus_line(week.get("goal") or week.get("check") or "")
            lead = f"이번 주 '{week['title']}'의 핵심 문장을 노트 없이 말한다."
            one["blocks"] = [
                {"m": 10, "t": f"{lead} {cue}".strip()},
                {"m": 20, "t": blocks[0]["t"]},
                {"m": 20, "t": blocks[1]["t"]},
                {"m": 10, "t": blocks[2]["t"] + " " + blocks[3]["t"]},
            ]
        for block in one["blocks"]:
            if english_block_needs_fill(block["m"], block["t"]):
                block["t"] = block["t"] + (
                    f" 이 칸은 {block['m']}분이다. 한 번이 짧으면 소재만 바꿔 같은 과제를 반복한다. "
                    "녹음은 최소 세 번이고, 각 녹음 뒤에 막힌 문장만 고쳐 다시 말한다. "
                    f"세 번으로 {block['m']}분을 채우지 못하면 새 소재로 두 번 더 해 그 칸의 분을 채운다. 마지막 녹음 전에는 대본을 보지 않는다."
                )
    return week


def english_block_needs_fill(minutes, text):
    if minutes < 15:
        return False
    if "분을 채운다" in text or "세 번과 고치기" in text:
        return False
    if re.search(r"(?:1[2-9]|[2-9]\d)\s*(?:개|문장|문제|쌍|단어|문항)", text):
        return False
    if not any(w in text for w in ("말한다", "녹음", "섀도잉", "따라 말")):
        return False
    if re.search(r"60초|90초|1분|3분", text):
        return True
    counts = [int(n) for n in re.findall(r"(\d+)\s*(?:개|문장|질문)", text)]
    return bool(counts) and max(counts) <= 8 and minutes >= 30


def english_expand_minutes(week_no):
    if week_no <= 26:
        return "60~90초"
    if week_no <= 52:
        return "2분"
    if week_no <= 104:
        return "2~3분"
    return "3분"


def thicken_english_check(week_no, check, expand, speak=""):
    if week_no <= 26:
        return check
    target = expand
    if re.search(r"4분(?:을| 리허설)", speak):
        target = "4분"
    elif re.search(r"10분\s*(?:영어로|영문|구술\s*녹음|발표를)", speak):
        target = "10분"
    return re.sub(r"대본 없이 60초 이상", f"대본 없이 {target} 이상", check)


def english_days(prev, title, model, pattern, trap, speak, write, check, prev_line="", mode="core", week_no=0):
    expand = english_expand_minutes(week_no)
    check = thicken_english_check(week_no, check, expand, speak)
    speak_without_inputs = re.sub(
        r"\d+(?:~\d+)?(?:초|분)\s*(?:분량\s*)?(?:원어민\s*)?(?:글쓰기/편집\s*)?(?:안내|일상|업무|강연|기업|토론|대담|내러티브|설명|영상|오디오|질문|자기소개|안에\s*역개요|내\s*완수)"
        r"|(?:오디오|녹음|코멘트|강의|영상)\s*\(?\d+(?:~\d+)?(?:초|분)\)?|결정적\s*\d+분",
        "",
        speak,
    )
    has_explicit_dur = bool(re.search(r"\d+(?:~\d+)?(?:초|분)", speak_without_inputs))
    if prev == "시작":
        opening = with_focus(
            f"오늘은 '{title}'{particle_eul(title)} 시작한다. 다음 모델 문장을 한 번 듣고 그대로 따라 말한다.",
            model,
        )
    else:
        opening = with_focus(
            f"지난주 '{prev}' 녹음에서 막힌 문장 둘만 다시 말한다. 그 주의 문장은 다음이다.",
            prev_line,
        )
    if mode == "listen":
        return [
            day(day_title(title, "듣기"), [
                (10, opening),
                (20, pattern + " 오디오를 한 번 통째로 듣고 핵심 사건·숫자·이유를 메모한다."),
                (20, "같은 구간을 다시 듣고 놓친 덩어리만 받아 적는다."),
                (10, "새로 익힌 표현 다섯 개만 카드에 적는다."),
            ]),
            day(day_title(title, "받아쓰기"), [
                (10, with_focus(f"어제 '{title}' 카드 표현 다섯 개를 말한다. 모델:", model)),
                (25, model + " 짧은 구간을 두세 번 듣고 문장 단위로 받아 쓴다."),
                (15, "대본과 대조해 틀린 기능어·시제만 표시한다."),
                (10, "고친 문장 셋을 따라 말한다."),
            ]),
            day(day_title(title, "함정"), [
                (10, with_focus(f"어제 '{title}'에서 고친 문장 셋을 다시 말한다.", model)),
                (20, trap),
                (20, "들은 내용에서 같은 함정이 나온 자리를 표시하고 바른 문장으로 고친다."),
                (10, "고친 문장 셋을 녹음한다."),
            ]),
            day(day_title(title, "말하기"), [
                (10, with_focus(f"어제 '{title}' 고친 문장을 노트 없이 말한다.", trap)),
                (40, speak + (
                    " 핵심 내용과 답변을 대본 없이 재진술하고, 막힌 문장만 고쳐 두 번 더 녹음한다."
                    if has_explicit_dur
                    else f" 오디오 요지를 {expand} 동안 대본 없이 재진술하고, 막힌 문장만 고쳐 두 번 더 녹음한다."
                )),
                (10, "더듬은 곳만 한 줄로 적는다."),
            ]),
            day(day_title(title, "쓰기"), [
                (10, with_focus(f"어제 '{title}' 말하기에서 더듬은 문장을 다시 말한다.", speak)),
                (25, write + " 받아쓴 요지를 완전한 문단으로 다시 쓴다."),
                (15, "소리 내어 읽고 들은 내용과 어긋난 문장을 고친다."),
                (10, "고친 문장만 다시 적는다."),
            ]),
            day(day_title(title, "늘리기"), [
                (10, with_focus(f"어제 '{title}' 글의 첫 문장을 말한다.", write)),
                (20, f"어제 글에서 다음 함정이 남은 문장을 고친다. {trap}"),
                (20, f"고친 글을 {expand} 이상 대본 없이 녹음한다."),
                (10, "녹음과 글을 비교해 다른 단어 세 개만 표시한다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}'의 모델 문장만 말한다.", model)),
                (40, check + " 한 번이 40분을 채우지 못하면 새 오디오 구간으로 같은 점검을 반복한다."),
                (10, "막힌 문장 하나를 다음 주 첫날 맨 위에 적는다. 오늘은 새 자료를 열지 않는다."),
            ]),
        ]
    if mode == "pron":
        return [
            day(day_title(title, "소리"), [
                (10, opening),
                (20, pattern + " 목표 소리·강세 자리를 표시하고 천천히 여섯 번 따라 말한다."),
                (20, "같은 문장을 자연 속도로 여섯 번 더 말하고 막힌 음절만 표시한다."),
                (10, "최소대립쌍이나 강세 단어 다섯 개를 카드에 적는다."),
            ]),
            day(day_title(title, "모델"), [
                (10, with_focus(f"어제 '{title}' 카드 다섯 개를 보고 말한다.", model)),
                (20, model),
                (20, "강세·연음만 바꿔 문장 여섯 개를 만들고 녹음한다."),
                (10, "가장 자연스러운 세 문장을 고른다."),
            ]),
            day(day_title(title, "함정"), [
                (10, with_focus(f"어제 '{title}'에서 고른 세 문장을 다시 말한다.", model)),
                (20, trap),
                (20, "틀린 발음/강세와 바른 버전을 나란히 녹음해 차이를 한 단어로 표시한다."),
                (10, "고친 문장 셋을 녹음한다."),
            ]),
            day(day_title(title, "말하기"), [
                (10, with_focus(f"어제 '{title}' 고친 문장을 노트 없이 말한다.", trap)),
                (40, speak + (
                    " 같은 구간을 세 번 녹음하고, 매번 강세·연음만 고친다."
                    if has_explicit_dur
                    else f" {expand} 구간을 세 번 녹음하고, 매번 강세·연음만 고친다."
                )),
                (10, "더듬은 음절만 한 줄로 적는다."),
            ]),
            day(day_title(title, "쓰기"), [
                (10, with_focus(f"어제 '{title}'에서 더듬은 음절이 들어간 문장을 말한다.", speak)),
                (25, write + " 강세 둘 자리를 대문자로 표시한 문장 여덟 줄을 쓴다."),
                (15, "소리 내어 읽고 표시와 실제 강세가 다른 줄을 고친다."),
                (10, "고친 문장만 다시 적는다."),
            ]),
            day(day_title(title, "늘리기"), [
                (10, with_focus(f"어제 '{title}' 글의 첫 문장을 말한다.", write)),
                (20, f"어제 글에서 다음 함정이 남은 문장을 고친다. {trap}"),
                (20, f"고친 글을 {expand} 이상 대본 없이 녹음한다."),
                (10, "녹음과 글을 비교해 다른 강세 세 곳만 표시한다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}'의 모델 문장만 말한다.", model)),
                (40, check + " 한 번이 40분을 채우지 못하면 소재를 바꿔 같은 발음 점검을 반복한다."),
                (10, "막힌 문장 하나를 다음 주 첫날 맨 위에 적는다."),
            ]),
        ]
    if mode == "read":
        return [
            day(day_title(title, "읽기"), [
                (10, opening),
                (20, pattern + " 원문 한 편을 훑고 주장·근거·전환 표시를 한다."),
                (20, "핵심 단락을 다시 읽어 모델 문장과 같은 구조를 표시한다."),
                (10, "재사용할 표현 다섯 개를 카드에 적는다."),
            ]),
            day(day_title(title, "모델"), [
                (10, with_focus(f"어제 '{title}' 카드 표현을 말한다. 모델:", model)),
                (20, model),
                (20, "모델 구조를 유지한 채 소재만 바꾼 문장 여섯 개를 만든다."),
                (10, "그중 세 문장을 녹음한다."),
            ]),
            day(day_title(title, "함정"), [
                (10, with_focus(f"어제 '{title}' 세 문장을 다시 말한다.", model)),
                (20, trap),
                (20, "원문과 초고에서 같은 함정을 찾아 바른 문장 옆에 적는다."),
                (10, "고친 문장 셋을 녹음한다."),
            ]),
            day(day_title(title, "말하기"), [
                (10, with_focus(f"어제 '{title}' 고친 문장을 노트 없이 말한다.", trap)),
                (40, speak + (
                    " 원문 요지와 내 재진술을 대조해 녹음한다."
                    if has_explicit_dur
                    else f" 원문 요지와 내 재진술을 {expand} 동안 대조해 녹음한다."
                )),
                (10, "더듬은 곳만 한 줄로 적는다."),
            ]),
            day(day_title(title, "쓰기"), [
                (10, with_focus(f"어제 '{title}' 말하기에서 더듬은 문장을 다시 말한다.", speak)),
                (25, write + " 원문 구조를 모방한 문단을 두 개 쓴다."),
                (15, "소리 내어 읽고 모호한 문장을 고친다."),
                (10, "고친 문장만 다시 적는다."),
            ]),
            day(day_title(title, "늘리기"), [
                (10, with_focus(f"어제 '{title}' 글의 첫 문장을 말한다.", write)),
                (20, f"어제 글에서 다음 함정이 남은 문장을 고친다. {trap}"),
                (20, f"고친 글을 {expand} 이상 대본 없이 녹음한다."),
                (10, "녹음과 글을 비교해 다른 단어 세 개만 표시한다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}'의 모델 문장만 말한다.", model)),
                (40, check + " 한 번이 40분을 채우지 못하면 새 원문 단락으로 같은 점검을 반복한다."),
                (10, "막힌 문장 하나를 다음 주 첫날 맨 위에 적는다."),
            ]),
        ]
    if mode == "contract":
        return [
            day(day_title(title, "조항"), [
                (10, opening),
                (20, pattern),
                (20, "실제 계약서 조항이나 예문에서 의무 주체(Party)·조건(Condition)·예외(Exception)·수치 기한에 네 가지 표시를 한다."),
                (10, "조항의 핵심 권리·의무 한 줄과 실무 용어 다섯 개만 영어 노트에 적는다."),
            ]),
            day(day_title(title, "모델"), [
                (10, with_focus(f"어제 '{title}' 노트에서 뽑은 핵심 용어 다섯 개를 소리 내어 말한다. 기준 조항은 다음과 같다.", model)),
                (20, model),
                (20, "기준 조항의 구조(당사자·조건·예외·시한)를 유지한 채 거래 금액·기한·면책 범위를 바꾼 대안 문장 여섯 개를 쓴다."),
                (10, "가장 모호함이 적은 세 문장을 소리 내어 읽고 녹음한다."),
            ]),
            day(day_title(title, "위험"), [
                (10, with_focus(f"어제 '{title}'에서 녹음한 세 문장을 다시 말한다. 기준 조항은 다음과 같다.", model)),
                (20, trap),
                (20, "의무(shall/must)·권리(may)·금지·단서가 헷갈리게 쓰인 모호한 초안을 옆에 적고, 누가 언제까지 무엇을 해야 하는지 명확한 문장으로 고친다."),
                (10, "고친 조항 셋을 조건과 기한이 들리게 다시 읽는다."),
            ]),
            day(day_title(title, "협상"), [
                (10, with_focus(f"어제 '{title}'에서 고친 조항 셋을 노트 없이 말한다. 피할 위험은 다음과 같다.", trap)),
                (40, speak + (
                    " 협상 상대방에게 이 조항이 왜 필요한지 대본 없이 설명·녹음하고, 상대 반론에 맞춘 대안 조항을 넣어 두 번 더 말하며 고친다."
                    if has_explicit_dur
                    else f" 협상 상대방에게 이 조항이 왜 필요한지 {expand} 동안 대본 없이 설명·녹음하고, 상대 반론에 맞춘 대안 조항을 넣어 두 번 더 말하며 고친다."
                )),
                (10, "설득이 약했던 근거와 막힌 표현 한 줄을 적는다."),
            ]),
            day(day_title(title, "작성"), [
                (10, with_focus(f"어제 '{title}' 협상 설명에서 막힌 표현을 다시 말한다. 과제는 다음과 같다.", speak)),
                (25, write + " 당사자 의무, 예외 단서, 통지 기한이 빠지지 않게 두 단락 분량의 조항 초안을 직접 작성한다."),
                (15, "작성한 조항을 소리 내어 읽으며 중의적 수식이나 정의 없는 용어를 표시해 고친다."),
                (10, "가장 크게 명확해진 문장 두 개만 따로 남긴다."),
            ]),
            day(day_title(title, "레드라인"), [
                (10, with_focus(f"어제 '{title}' 초안의 첫 문장을 노트를 덮고 말한다. 작성 과제는 다음과 같다.", write)),
                (20, f"어제 초안에서 다음 위험이 남아 있는지 점검해 레드라인(수정 추적)으로 고친다. {trap}"),
                (20, f"고친 조항과 수정 이유를 {expand} 이상 대본 없이 브리핑하듯 녹음한다."),
                (10, "초안과 레드라인 수정본에서 책임 범위가 달라진 표현 세 곳을 적는다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}'의 기준 조항만 노트를 덮고 말한다.", model)),
                (40, check + " 대본과 노트를 덮고 새로운 거래 사례 하나에 맞춰 조항을 작성·수정·구술 브리핑한다. 수정 이유까지 40분을 채운다."),
                (10, "막힌 조항 표현 하나를 다음 주 첫날 맨 위에 적는다. 오늘은 새 계약 단원을 열지 않는다."),
            ]),
        ]
    if mode == "prose":
        return [
            day(day_title(title, "독해"), [
                (10, opening),
                (20, pattern),
                (20, "기준 예문과 고품질 원문 단락에서 주어·동사 거리, 정보 흐름(구정보→신정보), 논리 연결 표지를 분석해 표시한다."),
                (10, "문맥에서 건진 정밀 동사·연결 표현 다섯 개를 예문 통째로 카드에 적는다."),
            ]),
            day(day_title(title, "문형"), [
                (10, with_focus(f"어제 '{title}' 카드의 표현 다섯 개를 문맥 문장으로 말한다. 기준 문장은 다음과 같다.", model)),
                (20, model),
                (20, "기준 문장의 수사·구문 설계를 유지한 채 다른 주제(업무·기술·사회)에 적용한 문장 여섯 개를 쓴다."),
                (10, "리듬과 강조 끝자리가 가장 자연스러운 세 문장을 소리 내어 읽고 녹음한다."),
            ]),
            day(day_title(title, "모호성"), [
                (10, with_focus(f"어제 '{title}'에서 고른 세 문장을 다시 말한다. 기준 문장은 다음과 같다.", model)),
                (20, trap),
                (20, "명사화 남용·공허한 수식·논리 비약이 들어간 초고 문장을 나란히 놓고, 행위자·동작·근거가 드러나게 고쳐 쓴다."),
                (10, "고친 문장 셋을 소리 내어 읽으며 호흡이 끊기는 곳을 확인한다."),
            ]),
            day(day_title(title, "말하기"), [
                (10, with_focus(f"어제 '{title}'에서 고친 문장 셋을 노트 없이 말한다. 피할 함정은 다음과 같다.", trap)),
                (40, speak + (
                    " 주장·근거·반론 고려를 갖춰 대본 없이 구술 녹음하고, 모호하거나 동어반복인 곳만 고쳐 두 번 더 녹음한다."
                    if has_explicit_dur
                    else f" 주장·근거·반론 고려를 갖춰 {expand} 동안 대본 없이 구술 녹음하고, 모호하거나 동어반복인 곳만 고쳐 두 번 더 녹음한다."
                )),
                (10, "구술 중 논리가 흐려졌거나 더듬은 문장 한 줄을 적는다."),
            ]),
            day(day_title(title, "집필"), [
                (10, with_focus(f"어제 '{title}' 구술에서 더듬은 논점을 다시 말한다. 말하기 과제는 다음과 같다.", speak)),
                (25, write + " 각 문단이 하나의 약속만 지키는지 확인하며 목표 분량 초고를 완성한다."),
                (15, "초고를 소리 내어 낭독하며 주어-서술어 호응과 문장 끝자리 강조가 무너진 문장을 표시해 고친다."),
                (10, "퇴고 전보다 선명해진 핵심 문장 두 개만 남긴다."),
            ]),
            day(day_title(title, "퇴고"), [
                (10, with_focus(f"어제 '{title}' 초고의 도입 문장을 노트를 덮고 말한다. 쓰기 과제는 다음과 같다.", write)),
                (20, f"어제 쓴 초고에서 군더더기와 다음 함정이 남은 문장을 골라 과감히 줄이고 고친다. {trap}"),
                (20, f"퇴고한 글을 바탕으로 핵심 논지와 근거를 {expand} 이상 대본 없이 발표하듯 녹음한다."),
                (10, "삭제하거나 압축한 군더더기 표현 세 곳과 이유를 적는다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}'의 기준 문장만 노트를 덮고 말한다.", model)),
                (40, check + " 노트를 덮고 새로운 논제로 초고 작성·소리 낭독 퇴고·구술 요약까지 한 번에 마친다."),
                (10, "막힌 표현이나 구조 문제 하나를 다음 주 첫날 맨 위에 적는다. 오늘은 새 기법을 열지 않는다."),
            ]),
        ]
    # core / default
    return [
        day(day_title(title, "소리"), [
            (10, opening),
            (20, pattern),
            (20, "그 소리를 최소 여섯 번 따라 말하고, 막힌 단어만 표시한다."),
            (10, "새로 익힌 단어 다섯 개만 카드에 적는다. 한국어 해설은 적지 않는다."),
        ]),
        day(day_title(title, "모델"), [
            (10, with_focus(f"어제 '{title}'에서 카드에 적은 단어 다섯 개를 보고 말한다. 오늘의 모델 문장은 다음이다.", model)),
            (20, model),
            (20, "모델의 고유명사·숫자·상황만 바꿔 문장 여섯 개를 만든다. 바꿀 자리가 없으면 주어·시제만 바꾼다."),
            (10, "그중 세 문장을 녹음한다."),
        ]),
        day(day_title(title, "함정"), [
            (10, with_focus(f"어제 '{title}'에서 녹음한 세 문장을 다시 말한다. 모델 문장은 다음이다.", model)),
            (20, trap),
            (20, "틀린 문장을 올바른 문장 옆에 적고 차이를 한 단어로 표시한다."),
            (10, "고친 문장 셋을 녹음한다."),
        ]),
        day(day_title(title, "말하기"), [
            (10, with_focus(f"어제 '{title}'에서 고친 문장 셋을 노트 없이 말한다. 고친 함정은 다음이다.", trap)),
            (40, speak + " 준비 뒤에 녹음하고, 막힌 문장만 고쳐 다시 녹음한 다음, 소재를 바꿔 같은 과제를 한 번 더 한다. 한 번이 짧아도 세 번과 고치기로 40분을 채운다." + ("" if has_explicit_dur else f" 목표 길이는 {expand}이다.") + " 대본은 마지막 녹음 뒤에만 본다."),
            (10, "더듬은 곳만 한 줄로 적는다."),
        ]),
        day(day_title(title, "쓰기"), [
            (10, with_focus(f"어제 '{title}' 말하기에서 더듬은 문장을 다시 말한다. 말할 과제는 다음이다.", speak)),
            (25, write + " 같은 과제의 문단을 두 개 더 쓴다. 각 문단은 여섯 줄 이상이다. 시간이 남으면 소리 내어 읽고 문장마다 한 군데를 고친다."),
            (15, "쓴 글을 소리 내어 읽고, 말하지 못한 문장을 고친다."),
            (10, "고친 문장만 다시 적는다."),
        ]),
        day(day_title(title, "늘리기"), [
            (10, with_focus(f"어제 '{title}'에서 쓴 글의 첫 문장을 말한다. 쓰기 과제는 다음이다.", write)),
            (20, f"어제 '{title}' 글에서 다음 함정이 남은 문장을 고친다. " + trap),
            (20, f"고친 글을 {expand} 이상 대본 없이 녹음한다. 막히면 그 문장만 적고 이어서 말한다."),
            (10, "녹음과 글을 비교해 다른 단어 세 개만 표시한다."),
        ]),
        day(day_title(title, "점검"), [
            (10, with_focus(f"이번 주 '{title}'의 모델 문장만 말한다.", model)),
            (40, check + " 한 번이 40분을 채우지 못하면 소재를 바꿔 같은 점검을 두 번 더 한다. 세 번 모두 고친 문장을 남긴다."),
            (10, "막힌 문장 하나를 다음 주 첫날 맨 위에 적는다. 오늘은 새 문법을 열지 않는다."),
        ]),
    ]
