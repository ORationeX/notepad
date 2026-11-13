# -*- coding: utf-8 -*-
"""Major unit u3: 계약 영어 독해와 협상."""
from curriculum.en.u3_contract.p09_reading_contracts import PHASE as _P09_READING_CONTRACTS
from curriculum.en.u3_contract.p10_contract_structure import PHASE as _P10_CONTRACT_STRUCTURE
from curriculum.en.u3_contract.p11_liability_analysis import PHASE as _P11_LIABILITY_ANALYSIS
from curriculum.en.u3_contract.p12_negotiation_redlines import PHASE as _P12_NEGOTIATION_REDLINES
from curriculum.en.u3_contract.p13_complex_clauses import PHASE as _P13_COMPLEX_CLAUSES
from curriculum.en.u3_contract.p14_clause_refactoring import PHASE as _P14_CLAUSE_REFACTORING
from curriculum.en.u3_contract.p15_full_contract_review import PHASE as _P15_FULL_CONTRACT_REVIEW

UNIT_META = {
    "id": "u3",
    "title": "계약 영어 독해와 협상",
    "summary": "계약 조항 읽기부터 초안 구조, 의무·책임 분석, 레드라인 수정, 실제 MSA·NDA 협상 검토까지 훈련한다.",
}

PHASES = [_P09_READING_CONTRACTS, _P10_CONTRACT_STRUCTURE, _P11_LIABILITY_ANALYSIS, _P12_NEGOTIATION_REDLINES, _P13_COMPLEX_CLAUSES, _P14_CLAUSE_REFACTORING, _P15_FULL_CONTRACT_REVIEW]
