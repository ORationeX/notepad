# -*- coding: utf-8 -*-
from pptx import Presentation

path = r"d:\유틸\잡무\UI 설계서\UI설계서_물류창고관리 고도화&운영_V0.2_20261116.pptx"
prs = Presentation(path)

def cm(v):
    return round(v / 360000, 3)

for idx in (3, 10):
    s = prs.slides[idx - 1]
    print("=" * 70, "SLIDE", idx)
    for j, sh in enumerate(s.shapes):
        t = ""
        if sh.has_text_frame:
            t = sh.text_frame.text.strip().replace("\n", " | ")[:60]
        print(f"  [{j:02d}] {sh.name:20} {cm(sh.left):7} {cm(sh.top):7} {cm(sh.width):7} {cm(sh.height):6} {t}")
