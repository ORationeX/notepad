# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Emu, Pt

PATH = r"d:\유틸\잡무\UI 설계서\UI설계서_물류창고관리 고도화&운영_V0.2_20261116.pptx"


def cm(v):
    return Emu(int(round(v * 360000)))


def to_cm(v):
    return round(v / 360000, 3)


prs = Presentation(PATH)
slide = prs.slides[2]
reds = []
for sh in slide.shapes:
    if sh.has_text_frame and sh.text_frame.text.strip() == "삭제":
        sh.top = cm(10.95)
    if sh.has_text_frame and sh.text_frame.text.startswith("품번 삭제 시"):
        sh.top = cm(11.75)
    try:
        if sh.line.color.rgb == RGBColor(0xFF, 0x00, 0x00) and sh.line.width >= Pt(2.5):
            reds.append(sh)
    except Exception:
        pass

for sh in reds:
    top = to_cm(sh.top)
    if 6.1 < top < 6.6 and to_cm(sh.height) < 6:
        sh.height = cm(4.40)  # bottom 10.72, below 저장(10.34)
    if 10.2 < top < 10.8:
        sh.top = cm(10.86)
        sh.height = cm(2.70)  # bottom 13.56, note ends 13.35
        for b in slide.shapes:
            if b.has_text_frame and b.text_frame.text.strip() == "4" and b.width < cm(1.2):
                b.left = cm(13.96 + 6.10 - 0.304)
                b.top = cm(10.86 - 0.28)

prs.save(PATH)
print("adjusted", len(reds))
