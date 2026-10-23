# -*- coding: utf-8 -*-

def phase(name, start, end, fr, to, result, resource, weeks):
    if len(weeks) != end - start + 1:
        raise SystemExit(f"{name}: {len(weeks)}")
    return {
        "name": name, "start": start, "end": end, "from": fr, "to": to,
        "result": result, "resource": resource, "weeks": weeks,
    }

def A(title, lab2, lab3, what, example, mistake, why):
    drill = example + " 숫자나 입력만 바꾼 경우를 두 개 더 같은 절차로 처리한다."
    check = "노트를 덮고 다음을 다시 한다. " + example + " 이어서 다음 실수가 어느 줄을 깨는지 말한다. " + mistake
    return (title, lab2, lab3, what, example, mistake, drill, why, check)

def E(title, lab2, lab3, model, pattern, trap, speak, write):
    check = "대본 없이 60초 이상 녹음하고 고친 문장을 네 개 남긴다. 기준 문장: " + model
    return (title, lab2, lab3, model, pattern, trap, speak, write, check)
