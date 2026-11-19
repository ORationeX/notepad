# EAP 공정별 메시지 양식 (운영)

- 작성일시: 2026-11-19 00:01:30 KST
- 기준: 운영 DB `14.252.196.10:1521/ORCL`, 계정 `ISM`, 서버 `db01`, 공장 `VTMC01`
- 조회: SELECT만 수행했다. 데이터는 바꾸지 않았다.
- 시각: LOT 마지막 이벤트 `2026-11-18 22:00:08`, 공정 사양 `2026-08-05`, 공정 흐름 `2026-07-31`, 설비 `2025-10-15`
- 주소: 설비 → EAP `POST /ISMMES/tracking/eapSTDTrackIn` 또는 `eapSTDTrackOut`. EAP → MES `POST /V4/tracking/...` 같은 JSON.

## 1. 지금 배포된 흐름

출하(`PKGSHP`)를 빼면 공정 마스터에 생산 공정이 있다. 배포된 흐름에 실제로 들어 있는 단계는 6개다. Wet Clean(`PKGWCL01`)은 공정 행과 설비 16대가 있으나, `PSFLOWCONTENT`가 0건이고 LOT도 0건이다. 운영 메시지 양식은 만들지 않았다.

최근 30일 LOT이 있는 순서다.

| 순서 | 공정 ID | 공정 | 설비 상세타입 | 대표 설비 | 라인 | LOT | 추적 유형 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SMTLMK01 | Laser marker 01 | LASERMRK | LASMAO531001 | SMT | ArrayLot | Standard, 서브로트 생성 Y |
| 2 | SMTSMD01 | SMD Lines 01 | SMDLINES | SMDLNK030001 | SMT | ArrayLot | TrackInOut, 완료 Y |
| 3 | SMTREC01 | PCB Recon 01 | PCBRECON | PCBREO101001 | SMT | CarrierLot 시작 | PCB Recon |
| 4 | PKGDIB01 | Die Bonder 01 | DIEBONDR | DIEBOA031009 | PKG | CarrierLot | Standard |
| 5 | PKGWIB01 | Wire Bonder 01 | WIREBOND | WIREBA005008 | PKG | CarrierLot | Standard |
| 6 | PKGHAT01 | Housing Attacher 01 | HOATTACH | HOUSIA156010 | PKG | CarrierLot | Standard |

공정 상세타입과 설비 상세타입이 같다. 개발 DB에서 나던 `SPINSPEC`/`SMDLINES`, `HSATTACH`/`HOATTACH` 불일치는 운영에 없다.

흐름 이름은 두 갈래다.

- `PKG_WET_N_Flow`: 공정 사양 21개. Die Bond, Wire Bond, Housing Attach. Wet Clean이 없다.
- `PKG_WB_N_Flow`: 공정 사양 6개. Die Bond 다음 Housing Attach. Wire Bond와 Wet Clean이 없다. 예: `GH96-18522A`.
- SMT는 공통 `SMTLine_Flow`: Laser, SMD Lines, PCB Recon.

## 2. 공통 규칙

- `factoryID`는 `VTMC01`이다.
- `recipeID`가 없으면 `""`다.
- SMT Laser와 SMD의 `lotID`는 ArrayLot이다. 최근 형식은 `17822B61G0YPK`처럼 품번 뒤 자리와 알파벳이 섞인다. 아래 JSON의 `17822B61G0001`은 자릿수 예시다.
- PKG와 PCB Recon의 `lotID`는 Carrier QR이다. 운영 값은 `ISM` + 날짜 + 일련번호다. 예: `ISM26031700256`. JSON의 `ISM26000000001`은 형식 예시다. MES LOT ID는 `Z67LA03UE` 형식이고, 메시지에는 넣지 않는다.
- `lineID`가 `PKG`인 설비는 TrackIn·TrackOut의 `lotID`를 Carrier QR로 찾는다. PCB Recon 설비 라인은 SMT이고, 설비 상세타입이 `PCBRECON`이라 TrackOut도 `lotID`를 Carrier QR로 본다.
- 서브로트는 마킹 PCB QR이다. `PV`로 시작한다. 예: `PVRIR00000C00HK`. JSON의 두 건은 형식이다. 운영 ArrayLot 수량은 최근 30일 64에서 276이고, CarrierLot 수량은 21 또는 32가 많다.
- TrackInOut인 SMD Lines는 TrackIn 또는 TrackOut 중 한 주소만 쓴다.
- 성공 응답은 `status` `OK`, `message`는 `INF_COMM_0023`, `data`는 요청 본문이다. PCB Recon TrackOut만 `subLotIDList`의 `defectResult`를 판정으로 바꿔 돌려준다.

## 3. 공정별 본문

JSON은 이 폴더에 있다. 본문 키는 개발 양식과 같고, 공정 ID·Carrier QR 형식·2번 공정 이름이 다르다.

### 3.1 Laser Marking

`01_LaserMarking_TrackIn.json`, `01_LaserMarking_TrackOut.json`

TrackIn 후 TrackOut. TrackOut의 `subLotIDList` 건수가 LOT 수량이 된다.

### 3.2 SMD Lines

`02_SMDLines_TrackInOut.json`

개발의 Screen Printer Inspection 자리에 있다. 공정 ID `SMTSMD01`, 상세타입 `SMDLINES`. 본문 하나로 투입과 완료가 되고 ArrayLot이 끝난다.

### 3.3 PCB Recon

`03_PCBRecon_TrackIn.json`, `03_PCBRecon_TrackOut.json`

TrackIn은 `productID`, `quantity`, `firstSubLotID`가 필요하다. `lotID`는 Carrier QR이다. TrackOut은 PCB 목록이다.

### 3.4 Die Bond

`04_DieBond_TrackIn.json`, `04_DieBond_TrackOut.json`

Standard. `lineID`는 `PKG`, `lotID`는 Carrier QR. TrackOut 본문은 TrackIn과 같고 주소만 `eapSTDTrackOut`이다.

### 3.5 Wire Bond

`05_WireBond_TrackIn.json`, `05_WireBond_TrackOut.json`

Die Bond와 같은 본문이다. `PKG_WB_N_Flow` 품번은 이 메시지를 보내지 않는다.

### 3.6 Housing Attach

`06_HousingAttach_TrackIn.json`, `06_HousingAttach_TrackOut.json`

Standard. 설비 상세타입 `HOATTACH`와 공정 상세타입 `HOATTACH`가 같다.

## 4. Wet Clean

설비 `WETCLEAN` 16대, 공정 `PKGWCL01`은 있다. 배포 흐름과 LOT 이력이 없어서 TrackInOut 본문을 운영 양식으로 두지 않았다.
