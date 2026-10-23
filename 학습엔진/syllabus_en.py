# -*- coding: utf-8 -*-
from syllabus_util import phase
from syllabus_en_y1 import Y1
from syllabus_en_mid import MID
from syllabus_en_late import LATE

R = "보존한 주. 각 주의 원래 자료를 쓴다."

PHASES = [
    phase("소리와 일상", 1, 13, "시작", "일상", "소리, 문장, 과거와 미래를 하루 이야기로 말한다.", R, list(range(1, 14))),
    Y1[0],
    Y1[1],
    Y1[2],
    phase("완료와 전달", 53, 65, "4분", "설명", "완료, 조동사, 수동, 관계절, 전달, 이메일과 단락을 한 설명으로 모은다.", R, list(range(14, 27))),
    MID[0],
    phase("회의와 제안", 79, 91, "가정", "회의", "첫 만남, 회의, 발표, 차트, 제안과 가격을 한 미팅으로 모은다.", R, list(range(27, 40))),
    MID[1],
    phase("계약 읽기", 105, 117, "차트", "조항", "의무, 기간, 책임, 해지, 비밀, 고치는 말을 읽어 표시한다. 법률 자문이 아니다.", R, list(range(40, 53))),
    *MID[2:],
    *LATE,
]
