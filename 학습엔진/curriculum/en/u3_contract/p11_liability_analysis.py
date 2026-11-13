# -*- coding: utf-8 -*-
"""Phase 11: 의무와 책임 분석 (weeks 131–143)."""
from curriculum.common import phase
from curriculum.en.resources import DRAFT
from curriculum.en.templates import bind_writer

W = bind_writer("의무와 책임 분석")

PHASE = phase("의무와 책임 분석", 131, 143, "구조", "책임", "진술·보장·면책(Indemnity)·책임제한(Cap)·지식재산·해지 조항의 위험 분배 구조를 문장 단위로 분석한다.", DRAFT, [
W("진술·보장과 면책", "warrant", "disclaimer", "Provider warrants that Deliverables will conform to Exhibit A for 90 days.", "사실 진술(represents), 일정 기간 품질 보장(warrants), 묵시적 보증 부인(AS IS / Disclaimer)의 범위를 나눈다.", "보증 기간 없이 영구 무하자 보장을 하거나 대문자 Disclaimer 문구의 범위를 놓치지 않는다."),
W("제3자 청구와 면책", "indemnify", "defend", "Provider shall indemnify and defend Client against third-party IP infringement claims.", "Indemnify(손해배상), Defend(방어 비용·소송 수행), Hold Harmless의 대상 청구 범위와 통지·통제 조건을 읽는다.", "배상 주체가 소송 방어 통제권이나 상대 과실 예외 없이 무한 책임을 지는 문장을 놓치지 않는다."),
W("직접·간접 손해 구분", "consequential", "exclude", "Neither party is liable for lost profits or indirect, consequential damages.", "직접 손해와 간접·결과적·일실이익(lost profits) 배제의 연결 방식과, 배상(Indemnity)이 여기서 빠지는지 확인한다.", "면책(Indemnity) 청구까지 결과적 손해 배제에 묶이는지 예외로 풀리는지 문장 구조를 안 보고 넘기지 않는다."),
W("책임 상한(Cap)과 초상한", "cap", "supercap", "Aggregate liability is capped at fees paid in the prior 12 months, except for IP indemnity.", "일반 책임 상한(Cap), 무제한 또는 2~3배 상한이 적용되는 예외(Uncapped/Super-cap: 고의·비밀·IP)를 대조한다.", "상한 문장만 읽고 뒤에 붙은 'Notwithstanding anything to the contrary' 예외 조항을 놓치지 않는다."),
W("배타적 구제수단", "sole", "remedy", "Re-performance or refund of the defective milestone fee is Client's exclusive remedy.", "sole and exclusive remedy 문구가 추가 손해배상이나 해지 청구를 어떻게 제한하는지 분석한다.", "하자 수정 후 환불만 가능하다고 적혀 있는데 일반적인 모든 손해배상이 가능한 것처럼 읽지 않는다."),
W("지식재산: 결과물 vs 배경기술", "foreground", "background", "Client owns Deliverables upon full payment; Provider retains all Background IP.", "신규 창출 IP(Foreground) 이전 시점(지급 완료 시 vs 생성 시)과 기존 도구·라이브러리(Background IP) 라이선스를 분리한다.", "기존 회사 공통 프레임워크까지 고객 소유로 넘어가는 'All Work Product' 문장을 그대로 두지 않는다."),
W("오픈소스·제3자 요소", "third-party", "license", "Provider shall disclose any copyleft open-source components prior to integration.", "결과물에 포함되는 제3자 SDK·오픈소스 라이선스(MIT vs GPL) 고지 및 사전 승인 문장을 점검한다.", "라이선스 조건 확인 없이 상용 고객 코드에 강한 카피레프트가 섞이는 위험을 방치하지 않는다."),
W("해지 권리와 치유 기간", "cure", "convenience", "Either party may terminate for material breach uncured 30 days after written notice.", "편의 해지(for convenience) 통지 기간과 중대 위반 해지(for cause) 시 치유 기간(cure period) 및 정산 의무를 비교한다.", "단순 1일 지연까지 즉시 해지 사유가 되거나 해지 시 기수행 작업 대금 정산 조항이 빠지지 않게 한다."),
W("존속 조항(Survival)", "survive", "종료", "Confidentiality, indemnity, and liability caps survive termination of this Agreement.", "계약이 만료되거나 해지된 뒤에도 계속 살아남는 조항 목록과 비밀유지 존속 기간의 적정성을 확인한다.", "해지와 동시에 책임 제한이나 비밀유지 의무까지 사라지도록 Survival에서 누락하지 않는다."),
W("불가항력(Force Majeure)", "excuse", "연장", "Neither party is liable for delays caused by events beyond its reasonable control, excluding payment.", "불가항력 면책 범위, 통지·경감 노력 의무, 장기 지속 시 해지 권리, 지급 의무 예외 여부를 읽는다.", "단순 외주사 인력 부족이나 공급망 실수가 불가항력으로 면책되도록 넓게 열린 문장을 놓치지 않는다."),
W("듣기: 위험 조항 협상 브리핑", "브리핑", "핵심", "Our primary concern is the uncapped indemnity for consequential damages.", "원어민 법무/사업 담당자의 3분 계약 리스크 요약 오디오를 듣고 쟁점별 우려와 대안을 받아쓴다.", "세부 수식어를 놓쳐 '상한 있음'을 '상한 없음'으로 반대로 받아 적지 않는다.", mode="listen"),
W("실제 SEC 계약 위험 매핑", "EDGAR", "매핑", "Section 9.2 carves out confidentiality breaches from the 12-month fee cap.", "공개된 실제 영문 MSA/라이선스 계약(5~8쪽)에서 진술·면책·책임제한·해지·IP 5개 조항을 추출해 리스크 표를 만든다.", "조항 요약에 자신의 추측이나 법률 자문 결론을 섞지 않고 원문 조항 번호와 문구만 적는다.", mode="read"),
W("위험 분배 점검", "균형", "대조", "Liability cap, carve-outs, IP carve-backs, and cure periods are mapped with zero contradictions.", "작성한 리스크 표와 수정 문장을 놓고 양 당사자 중 어느 쪽에 어떤 위험이 쏠려 있는지 구두로 설명한다.", "예외 조항과 책임 상한의 연결 관계를 놓쳤다면 다시 분석한다."),
])
