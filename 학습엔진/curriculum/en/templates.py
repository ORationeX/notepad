# -*- coding: utf-8 -*-
"""Shared speak/write task templates for intermediate and C1 English phases."""
from curriculum.common import E

SPEAK = {
    "가정과 소리": "{pattern} 현실과 다른 가정이나 시제 추측 세 가지를 대본 없이 말한다. 첫 문장: {model}",
    "실무 글쓰기와 논증": "{pattern} 업무 현황·정책·원인 비교를 구조에 맞춰 대본 없이 브리핑한다. 기준 문장: {model}",
    "고급 독해와 문체 전환": "{pattern} 고급 논증문의 글 구조와 문체 전환 핵심을 대본 없이 요약·비평한다. 기준 문장: {model}",
    "계약 초안과 구조": "{pattern} 실무 계약의 조항 구조·당사자·기간·대금 설계를 소리 내어 설명한다. 기준 문장: {model}",
    "의무와 책임 분석": "{pattern} 조항 속 의무(shall/must)·재량(may)·조건·책임 한도 차이를 분석해 말한다. 기준 문장: {model}",
    "협상과 조항 수정": "{pattern} 양보 조건·대안·수정 사유를 상대에게 설득하는 협상 발언을 대본 없이 말한다. 시작 문장: {model}",
    "복잡 조항과 정의": "{pattern} 교차 참조·예외 절(except/notwithstanding)·정의 용어 충돌을 짚어 설명한다. 정의: {model}",
    "문장 수정과 레드라인": "{pattern} 수정 묶음의 위험 분석과 대체 문장의 근거를 대본 없이 말한다. 고친 문장: {model}",
    "실전 계약 검토": "{pattern} 실제 SEC EDGAR/공개 MSA·NDA 조항에서 모호함·독소 경계를 찾아 브리핑한다. 문장: {model}",
    "명료한 설명문": "{pattern} 기술·업무 독자에게 절차나 원리를 명료하게 설명한다. 기준 문장: {model}",
    "문장 호흡과 응집": "{pattern} 원문 모범 단락을 분석한 뒤 고친 문장의 정보 흐름과 리듬을 설명한다. 기준 문장: {model}",
    "단락 설계와 전개": "{pattern} 단락의 논리 전개 구조(Claim-Evidence-Warrant)를 설명한다. 기준 문장: {model}",
    "장면과 사례 묘사": "{pattern} 에세이·보고서 속에 들어가는 구체적 관찰 사례(장면)를 생생하게 묘사한다. 장면 문장: {model}",
    "화자와 레지스터": "{pattern} 청자와 목적에 맞는 일관된 화자 거리와 격식(Register)으로 말한다. 기준 문장: {model}",
    "논증과 반론 처리": "{pattern} 핵심 주장, 근거, 반론 수용 및 재반박을 논리적으로 말한다. 문장: {model}",
    "어휘 정밀도와 뉘앙스": "{pattern} 미묘한 동의어 차이와 추상어의 구체적 치환 근거를 설명한다. 문장: {model}",
    "구조적 퇴고": "{pattern} 하루 묵힌 초고에서 구조·논리·문장 단위로 무엇을 왜 걷어냈는지 설명한다. 문장: {model}",
    "긴 글 아키텍처": "{pattern} 장문 글의 핵심 질문과 장·절 배치를 대본 없이 설명한다. 문장: {model}",
    "서사적 논픽션": "{pattern} 실제 사건·갈등·전환점이 담긴 장문 내러티브 논픽션 한 대목을 낭독·해설한다. 문장: {model}",
    "세 장르 통합 집필": "{pattern} 기술 설명문, 설득 비평문, 내러티브 에세이 세 편의 목적과 문체 차이를 비교 설명한다. 문장: {model}",
    "C1 글 포트폴리오": "{pattern} 완성한 최종 3편 선집의 공통 질문, 교정 이력, 핵심 논지를 대본 없이 발표한다. 문장: {model}",
}

WRITE = {
    "가정과 소리": "{trap} 잘못된 문법이나 혼동된 구조를 바른 문장 네 개로 고치고, 핵심 동사·절 경계에 밑줄을 긋는다.",
    "실무 글쓰기와 논증": "{trap} 빈약하거나 모호한 초고를 고쳐 명확한 근거와 다음 행동이 담긴 여덟 줄의 보고서·메일로 작성한다. 포함할 문장: {model}",
    "고급 독해와 문체 전환": "{trap} 명사화와 모호한 수식어를 행동 동사와 분명한 논리 표지로 고쳐 여덟 줄을 작성한다. 포함할 문장: {model}",
    "계약 초안과 구조": "{trap} 모호한 표현과 빈칸을 없앤 실제 계약 조항 여섯 줄을 작성한다. 포함할 문장: {model}",
    "의무와 책임 분석": "{trap} 모호하거나 불리하게 열린 표현을 대체 조항 여섯 줄로 고쳐 쓴다. 포함할 문장: {model}",
    "협상과 조항 수정": "{trap} 삭제·삽입·사유·대체 문장이 담긴 레드라인 수정안과 협상 메일 여덟 줄을 쓴다. 기준 문장: {model}",
    "복잡 조항과 정의": "{trap} 정의 용어·참조 조항·예외 범위가 모순 없이 맞물리는 여섯 줄을 쓴다. 바로잡을 문장: {model}",
    "문장 수정과 레드라인": "{trap} 삭제한 표현, 새로 넣은 표현, 위험 완화 사유를 여덟 줄로 적는다. 대상 문장: {model}",
    "실전 계약 검토": "{trap} 모호한 단어를 구체적 수치·절차·책임 경계로 바꾼 검토 메모와 대체 조항 여섯 줄을 쓴다. 연습 문장: {model}",
    "명료한 설명문": "{trap} 독자 수준에 맞춰 모호함과 명사화를 없앤 설명문 초고(이번 주 목표 분량)를 쓴다. 포함할 문장: {model}",
    "문장 호흡과 응집": "{trap} Old-New 흐름과 행동 동사 원칙에 따라 두 문단을 다시 쓴다. 재료: {model}",
    "단락 설계와 전개": "{trap} 개요의 논리 순서에 맞춰 세 단락 연결 초고를 쓴다. 기준: {model}",
    "장면과 사례 묘사": "{trap} 추상적 일반론 대신 구체적 인물·장소·수치·행동이 보이는 사례 문단(이번 주 목표 분량)을 쓴다. 남길 문장: {model}",
    "화자와 레지스터": "{trap} 어조가 어긋나거나 과장된 표현을 일관된 전문 산문 어조로 고쳐 목표 분량 초고를 쓴다. 기준: {model}",
    "논증과 반론 처리": "{trap} 반론 처리(Concession-Refutation)와 증거 출처가 포함된 논증 에세이 구간(목표 분량)을 쓴다. 주장: {model}",
    "어휘 정밀도와 뉘앙스": "{trap} 추상어·진부어를 정밀한 동사와 구체어·연어로 고쳐 목표 분량 글을 쓴다. 대상: {model}",
    "구조적 퇴고": "{trap} 삭제 근거, 문단 재배치 이유, 수정 전후 대조를 교정 노트(이번 주 목표 분량)로 작성한다. 대상: {model}",
    "긴 글 아키텍처": "{trap} 장별 핵심 질문, 독자 약속, 증거 배치 지도를 구조 설계서(이번 주 목표 분량)로 쓴다. 기준: {model}",
    "서사적 논픽션": "{trap} 구체적 인물·장애·선택·통찰이 살아 있는 내러티브 한 장면(목표 분량)을 쓴다. 재료: {model}",
    "세 장르 통합 집필": "{trap} 세 장르 중 선택한 한 편의 초고(이번 주 목표 분량 또는 핵심 3단락)를 쓴다. 기준: {model}",
    "C1 글 포트폴리오": "{trap} 선집의 서문, 글별 역할 요약, 전후 퇴고 대조표와 최종 에세이 개정본을 완성한다. 기준: {model}",
}


def fill(template, **kw):
    """Replace `{key}` placeholders sequentially without interpreting literal braces."""
    out = template
    for key, value in kw.items():
        out = out.replace("{" + key + "}", value)
    return out


def bind_writer(phase_kind):
    """Return a pure week builder bound to the phase's SPEAK/WRITE template."""
    if phase_kind not in SPEAK or phase_kind not in WRITE:
        raise SystemExit(f"no english task for {phase_kind}")

    def _write(title, lab2, lab3, model, pattern, trap, mode=None):
        speak = fill(SPEAK[phase_kind], title=title, model=model, pattern=pattern, trap=trap)
        write = fill(WRITE[phase_kind], title=title, model=model, pattern=pattern, trap=trap)
        if speak == write or "기준 문장을 넣어 60초" in speak:
            raise SystemExit(f"cloned task: {title}")
        return E(title, lab2, lab3, model, pattern, trap, speak, write, mode=mode)

    return _write

