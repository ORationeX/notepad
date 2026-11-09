# -*- coding: utf-8 -*-
"""ESL integration flowcharts: decision branches, not prose boxes."""
import shutil
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

SRC = r"d:\유틸\잡무\UI설계서_물류창고관리 고도화&운영_20261102.pptx"
DST = r"d:\유틸\잡무\UI설계서_물류창고관리_ESL연동흐름.pptx"

NAVY = RGBColor(0x1F, 0x49, 0x7D)
BLUE = RGBColor(0x4F, 0x81, 0xBD)
GREEN = RGBColor(0x5B, 0x7A, 0x32)
ORANGE = RGBColor(0xD4, 0x72, 0x1A)
RED = RGBColor(0xC0, 0x50, 0x4D)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x22, 0x27, 0x3E)
PALE_N = RGBColor(0xE7, 0xEE, 0xF6)
PALE_B = RGBColor(0xE8, 0xF1, 0xFA)
PALE_G = RGBColor(0xEE, 0xF4, 0xE4)
PALE_O = RGBColor(0xFD, 0xF1, 0xE4)
PALE_R = RGBColor(0xF8, 0xE6, 0xE4)
PALE_Y = RGBColor(0xFF, 0xF8, 0xDC)
YES = RGBColor(0x2E, 0x7D, 0x32)
NO = RGBColor(0xC0, 0x50, 0x4D)
LINE = RGBColor(0x4F, 0x81, 0xBD)

UI = (PALE_N, NAVY)
SV = (PALE_B, BLUE)
DB = (PALE_G, GREEN)
EX = (PALE_O, ORANGE)
ER = (PALE_R, RED)
OK = (PALE_G, GREEN)


def emu(v):
    return int(round(v * 914400))


def strip_style(shape):
    style = shape._element.find(qn("p:style"))
    if style is not None:
        shape._element.remove(style)


def style_run(run, size, bold, color):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "맑은 고딕"
    r_pr = run._r.get_or_add_rPr()
    r_pr.set("lang", "ko-KR")
    r_pr.set("altLang", "en-US")
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = r_pr.find(qn(tag))
        if el is not None:
            r_pr.remove(el)
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = etree.SubElement(r_pr, qn(tag))
        el.set("typeface", "맑은 고딕")


def write_line(shape, text, size, bold, color):
    tf = shape.text_frame
    tf.word_wrap = False
    tf.auto_size = None
    body = tf._txBody.find(qn("a:bodyPr"))
    body.set("anchor", "ctr")
    for k in ("lIns", "rIns", "tIns", "bIns"):
        body.set(k, str(emu(0.04)))
    first = tf.paragraphs[0]
    for r in list(first.runs):
        r._r.getparent().remove(r._r)
    first.alignment = PP_ALIGN.CENTER
    first.space_before = Pt(0)
    first.space_after = Pt(0)
    p_pr = first._p.get_or_add_pPr()
    if p_pr.find(qn("a:buNone")) is None:
        p_pr.append(etree.Element(qn("a:buNone")))
    run = first.add_run()
    run.text = text
    style_run(run, size, bold, color)


def paint(shape, fill, line, lw=1.25):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(lw)
    strip_style(shape)


class Board:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add(self, nid, kind, text, x, y, w, h, fill, line, size=12):
        self.nodes.append(dict(id=nid, kind=kind, text=text, x=x, y=y, w=w, h=h, fill=fill, line=line, size=size))
        return nid

    def box(self, nid, text, x, y, w, h, tone=UI, size=12):
        return self.add(nid, "box", text, x, y, w, h, tone[0], tone[1], size)

    def dia(self, nid, text, x, y, w=1.55, h=0.62, size=11):
        return self.add(nid, "dia", text, x, y, w, h, PALE_Y, BLUE, size)

    def edge(self, a, b, sa="b", db="t", label=None, color=INK):
        self.edges.append((a, b, sa, db, label, color))

    def _at(self, nid):
        for n in self.nodes:
            if n["id"] == nid:
                return n
        raise KeyError(nid)

    def render(self, slide):
        by = {n["id"]: n for n in self.nodes}

        def port(n, name):
            x, y, w, h = n["x"], n["y"], n["w"], n["h"]
            return {
                "t": (x + w / 2, y),
                "b": (x + w / 2, y + h),
                "l": (x, y + h / 2),
                "r": (x + w, y + h / 2),
            }[name]

        for a, b, sa, db, label, color in self.edges:
            n1, n2 = by[a], by[b]
            x1, y1 = port(n1, sa)
            x2, y2 = port(n2, db)
            if sa in ("t", "b") and db in ("t", "b") and abs(x1 - x2) > 0.08:
                pts = [(x1, y1), (x1, y2), (x2, y2)]
            elif sa in ("l", "r") and db in ("l", "r") and abs(y1 - y2) > 0.08:
                pts = [(x1, y1), (x2, y1), (x2, y2)]
            elif abs(x1 - x2) < 0.08 or abs(y1 - y2) < 0.08:
                pts = [(x1, y1), (x2, y2)]
            elif sa in ("l", "r"):
                pts = [(x1, y1), (x2, y1), (x2, y2)]
            else:
                pts = [(x1, y1), (x1, y2), (x2, y2)]
            for i in range(len(pts) - 1):
                p, q = pts[i], pts[i + 1]
                if abs(p[0] - q[0]) < 0.02 and abs(p[1] - q[1]) < 0.02:
                    continue
                last = i == len(pts) - 2
                c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, emu(p[0]), emu(p[1]), emu(q[0]), emu(q[1]))
                c.line.color.rgb = LINE
                c.line.width = Pt(1.5)
                strip_style(c)
                if last:
                    ln = c.line._get_or_add_ln()
                    tail = etree.SubElement(ln, qn("a:tailEnd"))
                    tail.set("type", "triangle")
                    tail.set("w", "sm")
                    tail.set("len", "med")
            if label:
                mx = (pts[0][0] + pts[1][0]) / 2
                my = (pts[0][1] + pts[1][1]) / 2
                if abs(pts[0][0] - pts[1][0]) < 0.08:
                    lx, ly = mx + 0.04, my - 0.16
                else:
                    lx, ly = mx - 0.18, my - 0.20
                tb = slide.shapes.add_textbox(emu(lx), emu(ly), emu(0.55), emu(0.22))
                write_line(tb, label, 10, True, color)

        for n in self.nodes:
            kind = MSO_SHAPE.DIAMOND if n["kind"] == "dia" else MSO_SHAPE.ROUNDED_RECTANGLE
            sh = slide.shapes.add_shape(kind, emu(n["x"]), emu(n["y"]), emu(n["w"]), emu(n["h"]))
            paint(sh, n["fill"], n["line"], 1.35)
            if n["kind"] == "box":
                try:
                    sh.adjustments[0] = 0.18
                except Exception:
                    pass
            write_line(sh, n["text"], n["size"], True, n["line"] if n["kind"] == "box" else INK)


def new_slide(prs):
    layout = prs.slide_masters[0].slide_layouts[2]
    slide = prs.slides.add_slide(layout)
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    return slide


def chrome(slide, title):
    tb = slide.shapes.add_textbox(emu(0.40), emu(0.28), emu(7.2), emu(0.46))
    write_line(tb, title, 26, True, RGBColor(0, 0, 0))
    tb.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    tag = slide.shapes.add_textbox(emu(6.4), emu(0.02), emu(4.15), emu(0.32))
    write_line(tag, "(ESL 연동 흐름)", 16, True, RGBColor(0x9B, 0xBB, 0x59))
    tag.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    badge = slide.shapes.add_textbox(emu(6.4), emu(0.34), emu(4.15), emu(0.36))
    write_line(badge, "Process Flow", 20, False, RGBColor(0x8D, 0x96, 0x82))
    badge.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
    legend = [
        (0.40, "화면", NAVY),
        (1.25, "서버", BLUE),
        (2.10, "DB", GREEN),
        (2.85, "ESL", ORANGE),
        (3.70, "오류", RED),
        (4.55, "판단", BLUE),
    ]
    for x, text, color in legend:
        chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, emu(x), emu(1.02), emu(0.78), emu(0.28))
        paint(chip, WHITE, color, 1.25)
        try:
            chip.adjustments[0] = 0.3
        except Exception:
            pass
        write_line(chip, text, 10, True, color)


def slide_overview(prs):
    s = new_slide(prs)
    chrome(s, "ESL 연동 전체 분기")
    b = Board()
    # band 1 — when to run
    b.box("enum", "설정 읽기", 0.40, 1.48, 1.6, 0.36, DB)
    b.dia("auto", "자동?", 0.48, 2.05, 1.45, 0.56)
    b.box("manual", "수동 1회", 2.40, 2.14, 1.55, 0.36, UI)
    b.dia("win", "시간 창?", 0.42, 2.85, 1.55, 0.56)
    b.box("stop1", "미실행", 2.40, 2.94, 1.4, 0.36, ER)
    b.dia("gap", "간격 경과?", 0.38, 3.65, 1.65, 0.56)
    b.box("stop2", "미실행", 2.40, 3.74, 1.4, 0.36, ER)
    b.box("item", "건별 분기", 0.45, 4.45, 1.6, 0.36, SV)
    # band 2 — one item
    b.dia("ex", "제외 일치?", 2.55, 4.32, 1.6, 0.56)
    b.box("skip", "SYNC 제외", 4.55, 4.05, 1.6, 0.34, ER, 11)
    b.dia("dele", "삭제?", 4.55, 4.55, 1.35, 0.54, 11)
    b.box("dque", "DELETE", 6.25, 4.20, 1.35, 0.32, EX, 11)
    b.box("none", "삭제 없음", 6.25, 4.68, 1.45, 0.32, UI, 11)
    b.dia("zn", "구역?", 2.60, 5.15, 1.4, 0.54)
    b.box("withz", "ZONE 첨부", 4.55, 5.22, 1.55, 0.34, DB, 11)
    b.dia("bare", "무구역?", 2.60, 5.90, 1.45, 0.54)
    b.box("plain", "ZONE 없이", 4.55, 5.78, 1.55, 0.32, SV, 11)
    b.box("drop", "건 스킵", 4.55, 6.25, 1.4, 0.32, UI, 11)
    b.box("sque", "SYNC", 6.35, 5.45, 1.3, 0.34, EX)
    # band 3 — call
    b.box("call", "ESL 호출", 8.15, 4.40, 1.85, 0.36, EX)
    b.dia("ok", "성공?", 8.40, 5.00, 1.35, 0.54)
    b.box("suc", "SUCCESS", 8.30, 5.70, 1.55, 0.32, OK, 11)
    b.box("fail", "FAILURE", 6.40, 5.72, 1.55, 0.32, ER, 11)
    b.box("hist", "이력 1행", 6.45, 6.30, 1.7, 0.34, DB, 11)

    b.edge("enum", "auto", "b", "t")
    b.edge("auto", "manual", "r", "l", "아니오", NO)
    b.edge("auto", "win", "b", "t", "예", YES)
    b.edge("manual", "item", "b", "t")
    b.edge("win", "stop1", "r", "l", "아니오", NO)
    b.edge("win", "gap", "b", "t", "예", YES)
    b.edge("gap", "stop2", "r", "l", "아니오", NO)
    b.edge("gap", "item", "b", "t", "예", YES)
    b.edge("item", "ex", "r", "l")
    b.edge("ex", "skip", "r", "b", "예", YES)
    b.edge("ex", "zn", "b", "t", "아니오", NO)
    b.edge("skip", "dele", "b", "t")
    b.edge("dele", "dque", "r", "b", "예", YES)
    b.edge("dele", "none", "b", "l", "아니오", NO)
    b.edge("zn", "withz", "r", "l", "예", YES)
    b.edge("zn", "bare", "b", "t", "아니오", NO)
    b.edge("withz", "sque", "r", "t")
    b.edge("bare", "plain", "r", "l", "전송", YES)
    b.edge("bare", "drop", "b", "t", "제외", NO)
    b.edge("plain", "sque", "r", "b")
    b.edge("sque", "call", "r", "l")
    b.edge("dque", "call", "r", "t")
    b.edge("call", "ok", "b", "t")
    b.edge("ok", "suc", "b", "t", "예", YES)
    b.edge("ok", "fail", "l", "r", "아니오", NO)
    b.edge("suc", "hist", "l", "t")
    b.edge("fail", "hist", "b", "t")
    b.render(s)
    return s


def slide_query(prs, title, field_a, col_a, field_b, col_b, table):
    s = new_slide(prs)
    chrome(s, title)
    b = Board()
    # main spine x=0.45, side x=3.5 / x=6.3
    b.box("open", "조회 화면", 0.70, 1.48, 2.1, 0.40, UI)
    b.dia("a", field_a, 0.95, 2.15)
    b.box("a_no", "조건 제외", 3.15, 2.28, 1.7, 0.38, SV)
    b.box("a_yes", col_a, 3.15, 2.85, 1.7, 0.38, DB)
    b.dia("b", field_b, 0.95, 3.55)
    b.box("b_no", "조건 제외", 3.15, 3.68, 1.7, 0.38, SV)
    b.box("b_yes", col_b, 3.15, 4.25, 1.7, 0.38, DB)
    b.box("btn", "조회 클릭", 0.85, 4.50, 1.8, 0.38, UI)
    b.box("sql", table, 0.55, 5.05, 2.4, 0.36, DB, 11)
    b.dia("cnt", "0건?", 0.95, 5.58, 1.45, 0.56)
    b.box("empty", "빈 그리드", 3.05, 5.66, 1.7, 0.36, UI)
    b.box("end1", "종료", 5.10, 5.66, 1.25, 0.36, SV)
    b.box("grid", "그리드", 0.90, 6.35, 1.6, 0.36, UI)
    b.box("end2", "종료", 3.05, 6.35, 1.25, 0.36, SV)

    b.edge("open", "a", "b", "t")
    b.edge("a", "a_no", "r", "l", "없음", NO)
    b.edge("a", "a_yes", "b", "t", "있음", YES)
    b.edge("a_no", "b", "b", "r")
    b.edge("a_yes", "b", "r", "r")
    b.edge("b", "b_no", "r", "l", "없음", NO)
    b.edge("b", "b_yes", "b", "t", "있음", YES)
    b.edge("b_no", "btn", "b", "r")
    b.edge("b_yes", "btn", "b", "r")
    b.edge("btn", "sql", "b", "t")
    b.edge("sql", "cnt", "b", "t")
    b.edge("cnt", "empty", "r", "l", "예", NO)
    b.edge("cnt", "grid", "b", "t", "아니오", YES)
    b.edge("empty", "end1", "r", "l")
    b.edge("grid", "end2", "r", "l")
    b.render(s)
    return s


def slide_save(prs, title, f1, f2, table, hist):
    s = new_slide(prs)
    chrome(s, title)
    b = Board()
    b.box("go", "저장 클릭", 0.55, 1.48, 1.9, 0.38, UI)
    b.dia("f1", f1, 0.70, 2.05, 1.6, 0.60)
    b.box("e1", "필수 오류", 3.00, 2.16, 1.7, 0.38, ER)
    b.dia("f2", f2, 0.70, 2.85, 1.6, 0.60)
    b.box("e2", "필수 오류", 3.00, 2.96, 1.7, 0.38, ER)
    b.dia("len", "40자?", 0.75, 3.65, 1.5, 0.58)
    b.box("e3", "길이 오류", 3.00, 3.75, 1.7, 0.38, ER)
    b.box("key", "TIMEKEY 채번", 0.45, 4.45, 2.1, 0.38, SV)
    b.dia("pk", "PK?", 0.75, 5.05, 1.5, 0.58)
    b.box("upd", "UPDATE", 3.00, 5.15, 1.9, 0.40, DB)
    b.box("ins", "INSERT", 0.55, 5.85, 1.9, 0.40, DB)
    b.box("his", hist, 5.30, 5.50, 2.5, 0.40, DB, 11)
    b.box("ev", "이벤트 컬럼", 5.45, 6.15, 2.2, 0.36, SV)
    b.box("re", "재조회", 8.15, 5.85, 1.5, 0.40, UI)

    b.edge("go", "f1", "b", "t")
    b.edge("f1", "e1", "r", "l", "없음", NO)
    b.edge("f1", "f2", "b", "t", "있음", YES)
    b.edge("f2", "e2", "r", "l", "없음", NO)
    b.edge("f2", "len", "b", "t", "있음", YES)
    b.edge("len", "e3", "r", "l", "초과", NO)
    b.edge("len", "key", "b", "t", "이하", YES)
    b.edge("key", "pk", "b", "t")
    b.edge("pk", "upd", "r", "l", "있음", YES)
    b.edge("pk", "ins", "b", "t", "없음", NO)
    b.edge("upd", "his", "r", "l")
    b.edge("ins", "his", "r", "l")
    b.edge("his", "ev", "b", "t")
    b.edge("ev", "re", "r", "l")
    b.render(s)
    return s


def slide_setting(prs):
    s = new_slide(prs)
    chrome(s, "동기화 설정 저장 분기")
    b = Board()
    b.box("open", "설정 변경", 0.45, 1.46, 1.7, 0.34, UI)
    b.box("q", "ENUM 조회", 0.45, 1.95, 1.7, 0.34, DB)
    b.dia("st", "START?", 0.52, 2.42, 1.55, 0.54)
    b.box("stn", "09:00", 2.50, 2.52, 1.2, 0.32, SV)
    b.dia("en", "END?", 0.58, 3.12, 1.45, 0.54)
    b.box("enn", "19:00", 2.50, 3.22, 1.2, 0.32, SV)
    b.dia("iv", "간격?", 0.58, 3.82, 1.45, 0.54)
    b.box("ivn", "60분", 2.50, 3.92, 1.2, 0.32, SV)
    b.box("edit", "값 수정", 0.55, 4.55, 1.5, 0.34, UI)
    b.box("save", "설정 저장", 0.45, 5.05, 1.7, 0.34, UI)
    b.dia("both", "둘 다 값?", 0.45, 5.55, 1.7, 0.56)
    b.box("skip", "비교 생략", 2.55, 5.65, 1.55, 0.34, OK, 11)
    b.dia("cmp", "시작<종료?", 2.50, 6.22, 1.65, 0.52)
    b.box("bad", "시간 오류", 4.50, 6.30, 1.55, 0.34, ER, 11)
    b.box("pass", "비교 통과", 4.50, 5.65, 1.6, 0.34, OK, 11)
    b.dia("iv2", "간격 빈값?", 6.55, 5.45, 1.65, 0.54)
    b.box("null", "NULL", 8.55, 5.15, 1.35, 0.32, DB)
    b.box("num", "입력값", 8.55, 5.72, 1.35, 0.32, DB)
    b.box("done", "3건 저장", 6.70, 6.35, 1.8, 0.34, DB)

    b.edge("open", "q", "b", "t")
    b.edge("q", "st", "b", "t")
    b.edge("st", "stn", "r", "l", "없음", NO)
    b.edge("st", "en", "b", "t", "있음", YES)
    b.edge("stn", "en", "b", "r")
    b.edge("en", "enn", "r", "l", "없음", NO)
    b.edge("en", "iv", "b", "t", "있음", YES)
    b.edge("enn", "iv", "b", "r")
    b.edge("iv", "ivn", "r", "l", "없음", NO)
    b.edge("iv", "edit", "b", "t", "있음", YES)
    b.edge("ivn", "edit", "b", "r")
    b.edge("edit", "save", "b", "t")
    b.edge("save", "both", "b", "t")
    b.edge("both", "skip", "r", "l", "아니오", NO)
    b.edge("both", "cmp", "b", "l", "예", YES)
    b.edge("cmp", "bad", "r", "l", "아니오", NO)
    b.edge("cmp", "pass", "t", "b", "예", YES)
    b.edge("skip", "pass", "r", "l")
    b.edge("pass", "iv2", "r", "l")
    b.edge("iv2", "null", "r", "b", "예", YES)
    b.edge("iv2", "num", "r", "t", "아니오", NO)
    b.edge("null", "done", "l", "r")
    b.edge("num", "done", "l", "t")
    b.render(s)
    return s


def slide_schedule(prs):
    s = new_slide(prs)
    chrome(s, "동기화 실행 판단 분기")
    b = Board()
    # auto spine
    b.box("tick", "스케줄 틱", 0.35, 1.46, 1.7, 0.34, SV)
    b.box("read", "ENUM 읽기", 0.35, 1.95, 1.7, 0.34, DB)
    b.dia("st", "START?", 0.42, 2.42, 1.55, 0.54, 11)
    b.box("stn", "09:00", 2.30, 2.52, 1.15, 0.32, SV, 11)
    b.dia("en", "END?", 0.48, 3.10, 1.45, 0.54, 11)
    b.box("enn", "19:00", 2.30, 3.20, 1.15, 0.32, SV, 11)
    b.dia("iv", "간격?", 0.48, 3.78, 1.45, 0.54, 11)
    b.box("ivn", "60분", 2.30, 3.88, 1.15, 0.32, SV, 11)
    b.dia("before", "시작 전?", 0.40, 4.48, 1.6, 0.54, 11)
    b.box("stop_a", "미실행", 2.30, 4.56, 1.25, 0.34, ER, 11)
    b.dia("after", "종료 후?", 0.40, 5.16, 1.6, 0.54, 11)
    b.box("stop_b", "미실행", 2.30, 5.24, 1.25, 0.34, ER, 11)
    b.dia("prev", "이전 AUTO?", 0.35, 5.84, 1.7, 0.54, 10)
    b.dia("due", "간격 지남?", 2.35, 5.80, 1.7, 0.58, 10)
    b.box("stop_c", "미실행", 4.25, 5.92, 1.25, 0.34, ER, 11)
    # manual
    b.box("btn", "수동 클릭", 6.55, 1.46, 1.7, 0.36, UI)
    b.dia("login", "로그인?", 6.60, 2.10, 1.55, 0.58)
    b.box("noauth", "오류", 8.55, 2.20, 1.2, 0.36, ER)
    b.box("mode", "Manual", 6.70, 2.95, 1.45, 0.36, SV)
    b.box("user", "로그인 사용자", 6.40, 3.50, 2.0, 0.36, SV, 11)
    b.box("join", "대상 구성", 6.55, 6.35, 2.3, 0.40, EX)

    b.edge("tick", "read", "b", "t")
    b.edge("read", "st", "b", "t")
    b.edge("st", "stn", "r", "l", "없음", NO)
    b.edge("st", "en", "b", "t", "있음", YES)
    b.edge("stn", "en", "b", "r")
    b.edge("en", "enn", "r", "l", "없음", NO)
    b.edge("en", "iv", "b", "t", "있음", YES)
    b.edge("enn", "iv", "b", "r")
    b.edge("iv", "ivn", "r", "l", "없음", NO)
    b.edge("iv", "before", "b", "t", "있음", YES)
    b.edge("ivn", "before", "b", "r")
    b.edge("before", "stop_a", "r", "l", "예", NO)
    b.edge("before", "after", "b", "t", "아니오", YES)
    b.edge("after", "stop_b", "r", "l", "예", NO)
    b.edge("after", "prev", "b", "t", "아니오", YES)
    b.edge("prev", "due", "r", "l", "있음", YES)
    b.edge("prev", "join", "b", "l", "없음", NO)
    b.edge("due", "stop_c", "r", "l", "아니오", NO)
    b.edge("due", "join", "b", "t", "예", YES)
    b.edge("btn", "login", "b", "t")
    b.edge("login", "noauth", "r", "l", "아니오", NO)
    b.edge("login", "mode", "b", "t", "예", YES)
    b.edge("mode", "user", "b", "t")
    b.edge("user", "join", "b", "t")
    b.render(s)
    return s


def slide_item(prs):
    s = new_slide(prs)
    chrome(s, "전송 대상 건별 분기")
    b = Board()
    b.box("src", "원천 1건", 0.40, 1.48, 1.55, 0.34, SV)
    b.dia("hit", "제외 일치?", 0.32, 2.00, 1.7, 0.54)
    b.box("out", "SYNC 제외", 2.40, 2.10, 1.55, 0.32, ER, 11)
    b.dia("dev", "삭제?", 4.40, 2.00, 1.35, 0.54, 12)
    b.box("dq", "DELETE 큐", 6.15, 1.70, 1.55, 0.32, EX, 11)
    b.box("no", "삭제 없음", 6.15, 2.22, 1.55, 0.32, UI, 11)
    b.dia("zn", "구역 있음?", 0.32, 2.80, 1.7, 0.54)
    b.box("att", "ZONE 첨부", 2.40, 2.90, 1.55, 0.32, DB, 11)
    b.box("sq", "SYNC 큐", 4.40, 2.88, 1.5, 0.34, EX)
    b.dia("bare", "무구역?", 0.40, 3.60, 1.5, 0.54)
    b.box("keep", "ZONE 없이", 2.40, 3.50, 1.55, 0.32, SV, 11)
    b.box("drop", "건 스킵", 2.40, 4.05, 1.4, 0.32, UI, 11)
    b.dia("qs", "SYNC 큐?", 0.35, 4.55, 1.6, 0.50)
    b.box("snone", "SYNC 생략", 2.30, 4.62, 1.55, 0.32, UI, 11)
    b.box("scall", "SYNC 호출", 2.30, 5.15, 1.55, 0.30, EX, 11)
    b.dia("qd", "DELETE 큐?", 4.20, 4.52, 1.65, 0.52, 11)
    b.box("dnone", "DELETE 생략", 6.15, 4.60, 1.6, 0.32, UI, 10)
    b.box("dcall", "DELETE 호출", 6.10, 5.15, 1.7, 0.30, EX, 10)
    b.dia("ok", "성공?", 4.30, 5.55, 1.35, 0.50)
    b.box("fail", "FAILURE", 6.05, 5.62, 1.45, 0.30, ER, 11)
    b.box("suc", "SUCCESS", 4.25, 6.20, 1.45, 0.28, OK, 11)
    b.box("body", "전송 본문", 6.00, 6.18, 1.55, 0.30, DB, 11)
    b.box("msg", "사유 기록", 7.80, 5.62, 1.45, 0.30, ER, 11)
    b.box("row", "이력 1행", 7.70, 6.35, 1.7, 0.30, DB)

    b.edge("src", "hit", "b", "t")
    b.edge("hit", "out", "r", "l", "예", YES)
    b.edge("hit", "zn", "b", "t", "아니오", NO)
    b.edge("out", "dev", "r", "l")
    b.edge("dev", "dq", "r", "b", "예", YES)
    b.edge("dev", "no", "b", "t", "아니오", NO)
    b.edge("zn", "att", "r", "l", "예", YES)
    b.edge("zn", "bare", "b", "t", "아니오", NO)
    b.edge("att", "sq", "r", "l")
    b.edge("bare", "keep", "r", "l", "전송", YES)
    b.edge("bare", "drop", "b", "t", "제외", NO)
    b.edge("keep", "sq", "r", "b")
    b.edge("sq", "qs", "b", "r")
    b.edge("dq", "qd", "b", "t")
    b.edge("no", "qd", "b", "t")
    b.edge("qs", "snone", "r", "l", "없음", NO)
    b.edge("qs", "scall", "b", "l", "있음", YES)
    b.edge("snone", "qd", "b", "l")
    b.edge("scall", "qd", "r", "b")
    b.edge("qd", "dnone", "r", "l", "없음", NO)
    b.edge("qd", "dcall", "b", "l", "있음", YES)
    b.edge("dnone", "ok", "b", "l")
    b.edge("dcall", "ok", "r", "b")
    b.edge("ok", "fail", "r", "l", "아니오", NO)
    b.edge("ok", "suc", "b", "t", "예", YES)
    b.edge("suc", "body", "r", "l")
    b.edge("fail", "msg", "r", "l")
    b.edge("body", "row", "r", "l")
    b.edge("msg", "row", "b", "t")
    b.render(s)
    return s


def _filter_block(b, y, key, q_empty, empty_box, q_yes, yes_box, no_box, no_tone=DB):
    b.dia(key + "0", q_empty, 0.40, y, 1.6, 0.52, 11)
    b.box(key + "E", empty_box, 5.70, y + 0.08, 1.7, 0.34, SV, 12)
    b.dia(key + "1", q_yes, 0.48, y + 0.72, 1.45, 0.52, 12)
    b.box(key + "Y", yes_box, 5.70, y + 0.80, 1.9, 0.34, DB, 12)
    b.box(key + "N", no_box, 0.42, y + 1.42, 1.85, 0.34, no_tone, 12)
    b.edge(key + "0", key + "E", "r", "l", "없음", NO)
    b.edge(key + "0", key + "1", "b", "t", "있음", YES)
    b.edge(key + "1", key + "Y", "r", "l", "예", YES)
    b.edge(key + "1", key + "N", "b", "t", "아니오", NO)


def slide_history(prs):
    s = new_slide(prs)
    chrome(s, "이력 조건 분기  1")
    b = Board()
    b.box("go", "조회 클릭", 0.45, 1.46, 1.6, 0.34, UI)
    b.edge("go", "g0", "b", "t")
    _filter_block(b, 1.95, "g", "구분 값?", "구분 생략", "동기화?", "ACTION=SYNC", "ACTION=DELETE")
    b.edge("gE", "m0", "b", "t")
    b.edge("gY", "m0", "b", "t")
    b.edge("gN", "m0", "b", "t")
    _filter_block(b, 4.20, "m", "유형 값?", "유형 생략", "자동?", "AUTO", "Manual")
    b.render(s)
    return s


def slide_history_result(prs):
    s = new_slide(prs)
    chrome(s, "이력 조건 분기  2")
    b = Board()
    _filter_block(b, 1.46, "s", "상태 값?", "상태 생략", "성공?", "SUCCESS", "FAILURE", ER)
    b.dia("p", "기간 값?", 0.45, 3.40, 1.55, 0.54)
    b.box("poff", "기간 생략", 2.40, 3.20, 1.6, 0.32, SV, 11)
    b.box("pon", "STARTTIME", 2.40, 3.68, 1.7, 0.32, DB, 11)
    b.box("sql", "SELECT", 0.55, 4.20, 1.45, 0.34, DB)
    b.box("ord", "시작 DESC", 2.40, 4.20, 1.6, 0.34, SV, 11)
    b.dia("z", "0건?", 4.40, 4.08, 1.3, 0.54)
    b.box("empty", "빈 그리드", 6.15, 4.18, 1.55, 0.32, UI, 11)
    b.box("grid", "그리드", 4.50, 4.78, 1.35, 0.32, UI)
    b.box("c1", "번호·구분·유형", 0.40, 5.15, 2.4, 0.40, UI, 12)
    b.box("c2", "시작·종료·상태", 3.00, 5.15, 2.4, 0.40, UI, 12)
    b.box("c3", "본문·사용자", 5.60, 5.15, 2.2, 0.40, UI, 12)
    b.box("end", "종료", 8.05, 5.15, 1.4, 0.40, SV)
    b.edge("sE", "p", "b", "t")
    b.edge("sY", "p", "b", "t")
    b.edge("sN", "p", "b", "t")
    b.edge("p", "poff", "r", "l", "없음", NO)
    b.edge("p", "pon", "b", "l", "있음", YES)
    b.edge("poff", "sql", "b", "r")
    b.edge("pon", "sql", "b", "r")
    b.edge("sql", "ord", "r", "l")
    b.edge("ord", "z", "r", "l")
    b.edge("z", "empty", "r", "l", "예", NO)
    b.edge("z", "grid", "b", "t", "아니오", YES)
    b.edge("grid", "c1", "b", "t")
    b.edge("empty", "end", "b", "t")
    b.edge("c1", "c2", "r", "l")
    b.edge("c2", "c3", "r", "l")
    b.edge("c3", "end", "r", "l")
    b.render(s)
    return s


def reorder(prs):
    # new slides appended as 20..28
    order = [0, 20, 1, 2, 21, 22, 3, 4, 23, 24, 5, 6, 25, 26, 27, 28, 29] + list(range(7, 20))
    lst = prs.slides._sldIdLst
    items = list(lst)
    if len(items) != len(order):
        raise SystemExit(f"count {len(items)} != {len(order)}")
    for el in items:
        lst.remove(el)
    for i in order:
        lst.append(items[i])


def main():
    shutil.copyfile(SRC, DST)
    prs = Presentation(DST)
    slide_overview(prs)
    slide_query(prs, "제외 대상 조회 분기", "품번?", "PRODUCTNO", "변경코드?", "CHANGECODE", "ESLEXCEPTIONRULE")
    slide_save(prs, "제외 대상 저장 분기", "품번?", "변경코드?", "ESLEXCEPTIONRULE", "RULE HISTORY")
    slide_query(prs, "구역 표기 조회 분기", "품번?", "PRODUCTNO", "구역?", "ZONE", "ESLZONEMAPPING")
    slide_save(prs, "구역 표기 저장 분기", "품번?", "구역?", "ESLZONEMAPPING", "ZONE HISTORY")
    slide_setting(prs)
    slide_schedule(prs)
    slide_item(prs)
    slide_history(prs)
    slide_history_result(prs)
    reorder(prs)
    prs.save(DST)
    print("saved", len(prs.slides))


if __name__ == "__main__":
    main()
