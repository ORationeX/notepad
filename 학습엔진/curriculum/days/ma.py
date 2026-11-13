# -*- coding: utf-8 -*-
"""Mathematics (ma) 7-day plan builder and check/blank thickening helpers."""
import re

from curriculum.common import day, day_title, particle_eul, particle_i, with_focus


def thicken_math_check(week_no, check, mode="calc"):
    """Years 1–2 calculation checks that name one or two problems get a full set."""
    if mode != "calc" or week_no > 104:
        return check
    if any(word in check for word in ("증명", "귀납", "대우", "반례", "진술", "스케치")):
        return check
    counts = [int(n) for n in re.findall(r"(\d+)\s*(?:개|문제|식|문항)", check)]
    if counts and max(counts) >= 3:
        return check
    return (
        check
        + " 위에 적힌 계산이 여덟 문제보다 적으면 숫자만 바꾼 문제를 만들어 여덟 문제를 채운다. "
        + "각 답을 검산하고, 여덟 문제를 끝내기 전에는 해설을 보지 않는다."
    )


def thicken_math_blank(week_no, example, mode="calc"):
    """Calculation weeks redo one example on the blank day. That one line does not fill 40 minutes."""
    base = "노트를 덮고 다음을 백지에 다시 한다. " + example
    if mode != "calc" or week_no > 104:
        return base
    if any(word in example for word in ("증명", "귀납", "대우", "반례", "진술", "스케치")):
        return base
    counts = [int(n) for n in re.findall(r"(\d+)\s*(?:개|문제|식|문항)", example)]
    if counts and max(counts) >= 3:
        return base
    return (
        base
        + " 이 예만으로 40분이 차지 않으면 숫자만 바꾼 문제를 만들어 여덟 문제가 될 때까지 백지에서 푼다. "
        + "각 답을 검산하고, 여덟 문제를 끝내기 전에는 노트를 열지 않는다."
    )


def math_days(prev, title, definition, example, trap, drill, why, check, week_no=0, prev_line="", mode="calc", prev_mode=None):
    past_mode = prev_mode or mode
    if prev == "시작":
        opening = with_focus(
            f"오늘은 '{title}'{particle_eul(title)} 시작한다. 다음 예를 노트에 베끼지 않고, 첫 단계의 결과만 적는다.",
            example,
        )
    elif past_mode == "calc":
        opening = with_focus(
            f"지난주 '{prev}'의 다음 계산을 노트를 덮고 다시 푼다. 숫자만 하나 바꿔 같은 계산을 한 번 더 하고 검산한다.",
            prev_line,
        )
    else:
        opening = with_focus(
            f"지난주 '{prev}'에서 적은 다음 문장을 노트를 덮고 다시 말하고, 그 문장의 첫 근거를 한 줄로 적는다.",
            prev_line,
        )
    if mode == "sketch":
        return [
            day(day_title(title, "진술"), [
                (10, opening),
                (20, definition + " 정리의 가정·결론을 상자 안에 적고, 직접 증명하지 않는 이유를 한 줄로 표시한다."),
                (20, "가정 하나가 빠지면 어떤 반례가 생기는지 스케치만 적는다. 완전한 증명은 쓰지 않는다."),
                (10, with_focus(f"노트를 덮고 '{title}'의 진술을 말한다.", definition)),
            ]),
            day(day_title(title, "의미"), [
                (10, with_focus(f"어제 적은 '{title}' 진술을 덮고 말한다.", definition)),
                (25, example + " 진술이 보장하는 것과 보장하지 않는 것을 표로 나눈다."),
                (15, "같은 진술을 다른 맥락 하나에 적용해 무엇이 바뀌는지 적는다."),
                (10, "의미가 깨지는 조건을 한 줄로 적는다."),
            ]),
            day(day_title(title, "한계"), [
                (10, with_focus(f"어제 '{title}'에서 적은 의미 한계를 말한다.", example)),
                (20, trap),
                (20, "선택공리·무한차원·병리적 반례 또는 긴 보조정리 중 해당 한계를 표시하고, 왜 스케치로 남기는지 적는다."),
                (10, "한계에 짧은 이름을 붙인다."),
            ]),
            day(day_title(title, "스케치"), [
                (10, with_focus(f"어제 '{title}'에 붙인 한계 이름을 말한다.", trap)),
                (20, drill),
                (20, "증명 골격(가정→핵심 아이디어→결론)만 다섯 줄로 스케치한다. 세부 계산은 채우지 않는다."),
                (10, "채우지 않은 빈칸을 표시한다."),
            ]),
            day(day_title(title, "적용"), [
                (10, with_focus(f"어제 '{title}' 스케치의 빈칸을 말한다.", drill)),
                (20, why + " 이 진술을 호출할 수 있는 상황과 호출하면 안 되는 상황을 나란히 적는다."),
                (20, "어제 예의 숫자에 진술을 적용해 결론만 확인한다."),
                (10, "호출 조건을 두 문장으로 줄인다."),
            ]),
            day(day_title(title, "백지"), [
                (10, with_focus(f"어제 적은 '{title}' 호출 조건을 말한다.", why)),
                (40, "노트를 덮고 진술·한계·스케치 골격을 백지에 다시 쓴다. " + example),
                (10, "막힌 줄만 노트를 열어 고친다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}' 진술만 노트를 덮고 말한다.", definition)),
                (40, check),
                (10, "막힌 한 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 정의를 열지 않는다."),
            ]),
        ]
    if mode == "proof":
        return [
            day(day_title(title, "정의"), [
                (10, opening),
                (20, definition + " 노트에 적고, 기호마다 한국어 이름을 붙인다."),
                (20, "정의에서 빠지면 안 되는 조건에 밑줄을 긋고, 그 조건이 없는 문장을 하나 써 본다."),
                (10, with_focus(f"노트를 덮고 '{title}'의 정의를 말한다.", definition)),
            ]),
            day(day_title(title, "전개"), [
                (10, with_focus(f"어제 노트에 적은 '{title}' 정의를 덮고 말한다.", definition)),
                (25, example + " 각 문장이 앞 문장에서 나오는지 번호를 붙인다. 숫자 검산이 아니라 논리 연결을 확인한다."),
                (15, "같은 전개를 기호만 바꿔 한 번 더 쓴다."),
                (10, "전개가 정의의 어느 조건을 쓰는지 표시한다."),
            ]),
            day(day_title(title, "반례"), [
                (10, with_focus(f"어제 전개한 '{title}'의 핵심 문장을 말한다.", example)),
                (20, trap),
                (20, "가정이 빠졌을 때 깨지는 반례를 만들고, 어느 줄이 붕괴하는지 적는다."),
                (10, "이 실패에 짧은 이름을 붙인다."),
            ]),
            day(day_title(title, "증명"), [
                (10, with_focus(f"어제 '{title}'에 붙인 실패 이름을 말한다.", trap)),
                (20, drill),
                (20, "가정·핵심·결론의 세 단락으로 증명을 다시 쓰고, 반례 입력이 가정 밖으로 나가는지 확인한다."),
                (10, "막힌 줄을 표시한다."),
            ]),
            day(day_title(title, "이유"), [
                (10, with_focus(f"어제 '{title}' 증명에서 막힌 줄을 말한다.", drill)),
                (20, why + " 이 이유가 성립하는 원리를 노트에 풀어서 설명하고, 조건을 조금 바꾼 두 경우에서도 같은 이유가 통하는지 확인한다."),
                (20, "이유를 증명 단락의 번호와 연결해 적는다."),
                (10, "이유를 두 문장으로 줄여 적는다."),
            ]),
            day(day_title(title, "백지"), [
                (10, with_focus(f"어제 적은 '{title}'의 이유 두 문장을 소리 내어 말한다.", why)),
                (40, "노트를 덮고 정의·증명·반례를 백지에 다시 쓴다. " + example),
                (10, "막힌 줄만 노트를 열어 고친다."),
            ]),
            day(day_title(title, "점검"), [
                (10, with_focus(f"이번 주 '{title}' 정의만 노트를 덮고 말한다.", definition)),
                (40, check),
                (10, "막힌 한 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 정의를 열지 않는다."),
            ]),
        ]
    return [
        day(day_title(title, "정의"), [
            (10, opening),
            (20, definition + " 노트에 적고, 기호마다 한국어 이름을 붙인다."),
            (20, "정의에서 빠지면 안 되는 조건에 밑줄을 긋고, 그 조건이 없는 문장을 하나 써 본다."),
            (10, with_focus(f"노트를 덮고 '{title}'의 정의를 말한다.", definition)),
        ]),
        day(day_title(title, "예"), [
            (10, with_focus(f"어제 노트에 적은 '{title}' 정의를 덮고 말한다.", definition)),
            (25, example + " 풀이의 각 단계가 정의의 어느 규칙을 썼는지 옆에 적고, 나온 결과를 역연산이나 대입으로 직접 검산한다."),
            (15, "같은 유형으로 숫자나 대상만 바꾼 문제를 두 개 더 만들어 푼다."),
            (10, "각 예가 정의의 어느 조건을 쓰는지 번호를 붙인다."),
        ]),
        day(f"{title}{particle_i(title)} 깨지는 경우", [
            (10, with_focus(f"어제 푼 '{title}'의 다음 예를 검산한다.", example)),
            (20, trap),
            (20, "올바른 풀이를 옆에 적고, 두 풀이의 차이를 한 줄로 말한다."),
            (10, "이 실수에 짧은 이름을 붙인다."),
        ]),
        day(day_title(title, "문제"), [
            (10, with_focus(f"어제 '{title}'에 붙인 실수 이름을 말한다. 그 실수는 다음이다.", trap)),
            (20, drill),
            (20, "풀이를 가리고 다시 푼 뒤, 결과를 원래 식이나 정의에 넣어 확인한다."),
            (10, "틀린 항목을 개념, 계산, 읽기 중 하나로 표시한다."),
        ]),
        day(day_title(title, "이유"), [
            (10, with_focus(f"어제 '{title}' 문제에서 틀렸다고 표시한 항목을 다시 푼다. 문제는 다음이다.", drill)),
            (20, why + " 이 이유가 성립하는 원리를 노트에 풀어서 설명하고, 숫자나 조건을 조금 바꾼 두 가지 경우에서도 같은 이유가 통하는지 확인한다."),
            (20, "그 이유를 오늘의 예 숫자에 대입해 맞는지 확인한다."),
            (10, "이유를 두 문장으로 줄여 적는다."),
        ]),
        day(day_title(title, "백지"), [
            (10, with_focus(f"어제 적은 '{title}'의 이유 두 문장을 소리 내어 말한다.", why)),
            (40, thicken_math_blank(week_no, example, mode)),
            (10, "막힌 줄만 노트를 열어 고친다."),
        ]),
        day(day_title(title, "점검"), [
            (10, with_focus(f"이번 주 '{title}' 정의만 노트를 덮고 말한다.", definition)),
            (40, check),
            (10, "막힌 한 줄을 다음 주 첫날 맨 위에 적는다. 오늘은 새 정의를 열지 않는다."),
        ]),
    ]
