# -*- coding: utf-8 -*-
"""Major unit u4: 분산 아키텍처·동시성과 복원력 설계."""
from curriculum.sw.u4_distributed.p21_layered_vs_vertical import PHASE as _P21_LAYERED_VS_VERTICAL
from curriculum.sw.u4_distributed.p22_domain_vs_data_model import PHASE as _P22_DOMAIN_VS_DATA_MODEL
from curriculum.sw.u4_distributed.p23_sync_vs_async import PHASE as _P23_SYNC_VS_ASYNC
from curriculum.sw.u4_distributed.p24_mutable_concurrency import PHASE as _P24_MUTABLE_CONCURRENCY
from curriculum.sw.u4_distributed.p25_resilience_isolation import PHASE as _P25_RESILIENCE_ISOLATION
from curriculum.sw.u4_distributed.p26_evolutionary_arch import PHASE as _P26_EVOLUTIONARY_ARCH

UNIT_META = {
    "id": "u4",
    "title": "분산 아키텍처·동시성과 복원력 설계",
    "summary": "계층 vs 수직 슬라이스, 도메인·데이터 모델 간극, 동기·비동기, 동시성, 복원력과 진화적 아키텍처를 대조한다.",
}

PHASES = [_P21_LAYERED_VS_VERTICAL, _P22_DOMAIN_VS_DATA_MODEL, _P23_SYNC_VS_ASYNC, _P24_MUTABLE_CONCURRENCY, _P25_RESILIENCE_ISOLATION, _P26_EVOLUTIONARY_ARCH]
