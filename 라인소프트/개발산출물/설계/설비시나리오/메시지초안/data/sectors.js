window.MSG_DEFAULT_SECTORS = {
  version: 1,
  events: [
    {
      id: "STDTrackIn",
      name: "STDTrackIn",
      generateSheet: true,
      sheetKind: "api",
      sectors: ["in_meta", "in_request", "in_response", "in_example"],
      defaults: {
        endPoint: "/ISMMES/tracking/eapSTDTrackIn",
        method: "POST",
        description: "공정 시작을 요청한다."
      }
    },
    {
      id: "STDTrackOut",
      name: "STDTrackOut",
      generateSheet: true,
      sheetKind: "api",
      sectors: ["out_meta", "out_request", "out_item_desc", "out_response", "out_example"],
      defaults: {
        endPoint: "/ISMMES/tracking/eapSTDTrackOut",
        method: "POST",
        description: "공정 완료를 요청한다."
      }
    },
    {
      id: "DB_to_DB",
      name: "DB to DB",
      generateSheet: true,
      sheetKind: "table",
      sectors: ["db_to_db"]
    },
    {
      id: "BatchTrackIn",
      name: "BatchTrackIn",
      generateSheet: false,
      sheetKind: "none",
      sectors: []
    },
    {
      id: "BatchTrackOut",
      name: "BatchTrackOut",
      generateSheet: false,
      sheetKind: "none",
      sectors: []
    }
  ],
  sectors: {
    in_meta: {
      id: "in_meta",
      kind: "kv",
      title: "1. 설명",
      fields: [
        { key: "endPoint", label: "EndPoint" },
        { key: "method", label: "Method" },
        { key: "description", label: "설명" }
      ]
    },
    in_request: {
      id: "in_request",
      kind: "object",
      title: "2. 요청",
      columns: ["name", "type", "description", "detail"],
      fields: [
        { name: "factoryID", type: "String", description: "공장 ID", example: "VTMC01" },
        { name: "lineID", type: "String", description: "LINE ID", example: "" },
        { name: "equipmentID", type: "String", description: "설비 ID", example: "ASM81ACTAG01" },
        { name: "recipeID", type: "String", description: "레시피 ID", example: "RECIPEID" },
        { name: "lotID", type: "String", description: "PCB ID", detail: "대표 바코드", example: "LOTID" },
        { name: "boatID", type: "String", description: "AA 보트 ID", example: "BOATID" },
        { name: "bulkConsumableList", type: "BulkConsumableList[]", description: "소모자재 ID 리스트", nested: "BulkConsumableList" },
        { name: "bulkDurableList", type: "BulkDurableList[]", description: "장착자재 ID 리스트", nested: "BulkDurableList" }
      ]
    },
    in_response: {
      id: "in_response",
      kind: "object",
      title: "3. 응답",
      columns: ["name", "type", "description"],
      fields: [
        { name: "status", type: "String", description: "응답에 대한 상태 메시지(“OK”, “Internal Server Error”, …)", example: "OK" },
        { name: "message", type: "String", description: "응답에 대한 메시지", example: "Successfully processed." },
        { name: "data", type: "DATA", description: "응답 데이터", nested: "TrackInData" }
      ]
    },
    in_example: {
      id: "in_example",
      kind: "example",
      title: "4. 예시",
      requestSector: "in_request",
      responseSector: "in_response"
    },
    out_meta: {
      id: "out_meta",
      kind: "kv",
      title: "1. 설명",
      fields: [
        { key: "endPoint", label: "EndPoint" },
        { key: "method", label: "Method" },
        { key: "description", label: "설명" }
      ]
    },
    out_request: {
      id: "out_request",
      kind: "object",
      title: "2. 요청",
      columns: ["name", "type", "description", "detail"],
      fields: [
        { name: "factoryID", type: "String", description: "공장 ID", example: "VTMC01" },
        { name: "lineID", type: "String", description: "LINE ID", example: "" },
        { name: "equipmentID", type: "String", description: "설비 ID", example: "ASM81ACTAG01" },
        { name: "recipeID", type: "String", description: "레시피 ID", example: "RECIPEID" },
        { name: "lotID", type: "String", description: "PCB ID", detail: "대표 바코드", example: "LOTID" },
        { name: "itemList", type: "ITEM[]", description: "ITEM", nested: "ITEM" },
        { name: "bulkConsumableList", type: "BulkConsumableList[]", description: "소모자재 ID 리스트", nested: "BulkConsumableList" },
        { name: "bulkDurableList", type: "BulkDurableList[]", description: "장착자재 ID 리스트", nested: "BulkDurableList" }
      ]
    },
    out_item_desc: {
      id: "out_item_desc",
      kind: "rows",
      title: "ITEM 설명",
      place: "side",
      columns: [
        { key: "item", header: "item" },
        { key: "site", header: "site" },
        { key: "desc", header: "설명" }
      ],
      defaultRows: [
        { item: "resultStatus", site: "", desc: "설비에서 작업한 결과 상태를 표시 (OK,NG…)" },
        { item: "resultMessage", site: "", desc: "설비에서 작업한 결과 상태에 대한 메시지" },
        { item: "lensID", site: "", desc: "렌즈 개별 바코드" },
        { item: "sensorID", site: "", desc: "Sensor ID" },
        { item: "boatID", site: "", desc: "AA 보트 ID" },
        { item: "zone", site: "", desc: "작업구역(단일 작업구역일 경우 A)" },
        { item: "defectQuantity", site: "", desc: "불량 발생 총 Unit 수량" },
        { item: "defectCode", site: "", desc: "불량 발생시 코드 ID" },
        { item: "defectName", site: "", desc: "불량코드 ID의 명칭" }
      ]
    },
    out_response: {
      id: "out_response",
      kind: "object",
      title: "3. 응답",
      columns: ["name", "type", "description"],
      fields: [
        { name: "status", type: "String", description: "응답에 대한 상태 메시지(“OK”, “Internal Server Error”, …)", example: "OK" },
        { name: "message", type: "String", description: "응답에 대한 메시지", example: "Successfully processed." },
        { name: "data", type: "DATA", description: "응답 데이터", nested: "TrackOutData" }
      ]
    },
    out_example: {
      id: "out_example",
      kind: "example",
      title: "4. 예시",
      requestSector: "out_request",
      responseSector: "out_response",
      itemListFrom: "out_item_desc"
    },
    db_to_db: {
      id: "db_to_db",
      kind: "rows",
      title: "DB to DB 항목(프로시저 기반 호출)",
      columns: [
        { key: "item", header: "item" },
        { key: "site", header: "site" },
        { key: "value", header: "value" },
        { key: "desc", header: "설명" }
      ]
    }
  },
  nested: {
    BulkDurableList: {
      title: "BulkDurableList",
      columns: ["name", "type", "description", "detail"],
      fields: [
        { name: "bulkDurableID", type: "String", description: "장착 자재 ID", detail: "에폭시 ID", example: "EPOXY ID", required: "O" }
      ]
    },
    BulkConsumableList: {
      title: "BulkConsumableList",
      columns: ["name", "type", "description", "detail"],
      fields: [
        { name: "bulkConsumableID", type: "String", description: "소모 자재 ID", detail: "렌즈 자재 ID", example: "LENS CONSUMABLE ID", required: "O" }
      ]
    },
    ITEM: {
      title: "ITEM",
      columns: ["name", "type", "description", "required"],
      fields: [
        { name: "item", type: "String", description: "계측 항목", required: "O" },
        { name: "site", type: "String", description: "계측 항목별 SITE(위치)", required: "O" },
        { name: "value", type: "String", description: "측정 결과값", required: "O" }
      ]
    },
    TrackInData: {
      title: "DATA",
      columns: ["name", "type", "description"],
      fields: [
        { name: "factoryID", type: "String", description: "공장 ID", example: "VTMC01" },
        { name: "lineID", type: "String", description: "LINE ID", example: "" },
        { name: "equipmentID", type: "String", description: "설비 ID", example: "ASM81ACTAG01" },
        { name: "recipeID", type: "String", description: "레시피 ID", example: "RECIPEID" },
        { name: "lotID", type: "String", description: "PCB ID", example: "LOTID" },
        { name: "boatID", type: "String", description: "AA 보트 ID", example: "BOATID" },
        { name: "bulkConsumableList", type: "BulkConsumableList[]", description: "소모자재 ID 리스트", nested: "BulkConsumableList" },
        { name: "bulkDurableList", type: "BulkDurableList[]", description: "장착자재 ID 리스트", nested: "BulkDurableList" }
      ]
    },
    TrackOutData: {
      title: "DATA",
      columns: ["name", "type", "description"],
      fields: [
        { name: "factoryID", type: "String", description: "공장 ID", example: "VTMC01" },
        { name: "lineID", type: "String", description: "LINE ID", example: "" },
        { name: "equipmentID", type: "String", description: "설비 ID", example: "ASM81ACTAG01" },
        { name: "recipeID", type: "String", description: "레시피 ID", example: "RECIPEID" },
        { name: "lotID", type: "String", description: "PCB ID", example: "LOTID" },
        { name: "itemList", type: "ITEM[]", description: "UNIT 단위 검사결과", nested: "ITEM" },
        { name: "bulkConsumableList", type: "BulkConsumableList[]", description: "소모자재 ID 리스트", nested: "BulkConsumableList" },
        { name: "bulkDurableList", type: "BulkDurableList[]", description: "장착자재 ID 리스트", nested: "BulkDurableList" }
      ]
    }
  }
};
