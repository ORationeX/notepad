# -*- coding: utf-8 -*-
"""UI Design 번호 영역에 빨간 점선 상자를 두고, 배지를 상자 모서리에 건다."""
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

PATH = r"d:\유틸\잡무\UI 설계서\UI설계서_물류창고관리 고도화&운영_V0.2_20261116.pptx"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def cm(v):
    return Emu(int(round(v * 360000)))


def add_dash_box(slide, x, y, w, h):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cm(x), cm(y), cm(w), cm(h))
    sh.shadow.inherit = False
    sh.fill.background()
    sh.line.color.rgb = RGBColor(0xFF, 0x00, 0x00)
    sh.line.width = Pt(3.0)
    ln = sh.line._get_or_add_ln()
    for child in list(ln):
        if child.tag == qn("a:prstDash"):
            ln.remove(child)
    dash = etree.SubElement(ln, qn("a:prstDash"))
    dash.set("val", "dash")
    return sh


def find_badge(slide, number):
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        if sh.text_frame.text.strip() != str(number):
            continue
        if sh.width < cm(1.2) and sh.height < cm(1.2):
            return sh
    raise RuntimeError(f"badge {number} not found")


def place_badge(slide, number, x, y):
    sh = find_badge(slide, number)
    sh.left = cm(x)
    sh.top = cm(y)
    return sh


def bring_to_front(slide, shapes):
    tree = slide.shapes._spTree
    for sh in shapes:
        el = sh._element
        tree.remove(el)
        tree.append(el)


def corner(x, y, w, where="tr"):
    """Badge origin so the circle sits on the box corner."""
    size = 0.584
    hang = 0.28
    if where == "tr":
        return x + w - (size - hang), y - hang
    return x - hang, y - hang


def main():
    prs = Presentation(PATH)

    # --- ESL 구역 및 표기 관리 ---
    zone = prs.slides[2]
    # 1 조회 조건, 2 목록, 3 등록·저장, 4 품번 삭제
    z_boxes = [
        (1, 0.58, 4.22, 19.48, 1.96, "tr"),
        (2, 0.58, 6.24, 13.20, 11.36, "tl"),
        (3, 13.96, 6.32, 6.10, 4.06, "tr"),
        (4, 13.96, 10.50, 6.10, 2.68, "tr"),
    ]
    z_shapes = []
    for n, x, y, w, h, where in z_boxes:
        z_shapes.append(add_dash_box(zone, x, y, w, h))
        bx, by = corner(x, y, w, where)
        z_shapes.append(place_badge(zone, n, bx, by))
    bring_to_front(zone, z_shapes)

    # --- ESL 동기화 설정 및 이력 ---
    sync = prs.slides[9]
    # 수동 동기화 버튼을 설정 저장과 겹치지 않게 오른쪽으로 이동
    for sh in sync.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == "수동 동기화 실행":
            sh.left = cm(6.30)
            sh.top = cm(6.55)
            break
    s_boxes = [
        (1, 0.78, 4.90, 14.28, 0.68, "tr"),  # 시작·종료
        (2, 0.78, 5.64, 5.28, 1.68, "tr"),   # 간격 + 설정 저장
        (3, 6.18, 6.43, 3.84, 0.88, "tr"),   # 수동 동기화
        (4, 0.58, 8.90, 19.48, 1.90, "tr"),  # 이력 조회 조건
    ]
    s_shapes = []
    for n, x, y, w, h, where in s_boxes:
        s_shapes.append(add_dash_box(sync, x, y, w, h))
        bx, by = corner(x, y, w, where)
        s_shapes.append(place_badge(sync, n, bx, by))
    bring_to_front(sync, s_shapes)

    prs.save(PATH)
    print("saved", len(prs.slides))


if __name__ == "__main__":
    main()
