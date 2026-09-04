(function (global) {
  const STORE_DOC = "linesoft.msg.doc";
  const STORE_SECTORS = "linesoft.msg.sectors";

  function clone(v) {
    return JSON.parse(JSON.stringify(v));
  }

  function uid(prefix) {
    return (prefix || "id") + "_" + Math.random().toString(36).slice(2, 10);
  }

  function defaultSectors() {
    return clone(global.MSG_DEFAULT_SECTORS);
  }

  function loadSectors() {
    try {
      const raw = localStorage.getItem(STORE_SECTORS);
      if (!raw) return defaultSectors();
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.events || !parsed.sectors) return defaultSectors();
      return parsed;
    } catch (e) {
      return defaultSectors();
    }
  }

  function saveSectors(sectors) {
    localStorage.setItem(STORE_SECTORS, JSON.stringify(sectors));
  }

  function emptyDoc() {
    return {
      title: "설비 메시지 정의서",
      versionLabel: "",
      products: [],
      tocOrder: []
    };
  }

  function loadDoc() {
    try {
      const raw = localStorage.getItem(STORE_DOC);
      if (!raw) return emptyDoc();
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.products)) return emptyDoc();
      return parsed;
    } catch (e) {
      return emptyDoc();
    }
  }

  function saveDoc(doc) {
    localStorage.setItem(STORE_DOC, JSON.stringify(doc));
  }

  function findEventType(sectors, idOrName) {
    const key = String(idOrName || "").trim();
    return (sectors.events || []).find(function (ev) {
      return ev.id === key || ev.name === key;
    }) || null;
  }

  function sectorOf(sectors, id) {
    return (sectors.sectors || {})[id] || null;
  }

  function nestedOf(sectors, id) {
    return (sectors.nested || {})[id] || null;
  }

  function nestedIdOf(field) {
    if (!field) return "";
    const t = String(field.type || "").trim();
    if (t.slice(-2) === "[]") return field.nested || t.slice(0, -2);
    return field.nested || "";
  }

  function nestedTitleOf(sectors, nestedId) {
    const def = nestedOf(sectors, nestedId);
    return (def && def.title) || nestedId;
  }

  function nestedColumnsOf(sectors, nestedId) {
    const def = nestedOf(sectors, nestedId);
    return (def && def.columns) || ["name", "type", "description", "detail"];
  }

  function nestedFieldsOf(event, sectors, sectorId, nestedId) {
    if (!nestedId) return [];
    if (!event.nestedItems) event.nestedItems = {};
    if (!event.nestedItems[sectorId]) event.nestedItems[sectorId] = {};
    if (!Array.isArray(event.nestedItems[sectorId][nestedId])) {
      const def = nestedOf(sectors, nestedId);
      event.nestedItems[sectorId][nestedId] = clone((def && def.fields) || []);
    }
    return event.nestedItems[sectorId][nestedId];
  }

  function syncFieldNested(event, sectors, sectorId, field) {
    const nid = nestedIdOf(field);
    if (nid) {
      field.nested = nid;
      nestedFieldsOf(event, sectors, sectorId, nid);
    } else {
      delete field.nested;
    }
    return nid;
  }

  function snapshotNestedFromFields(event, sectors, sectorId, fields) {
    (fields || []).forEach(function (field) {
      const nid = nestedIdOf(field);
      if (!nid) return;
      field.nested = nid;
      const inner = nestedFieldsOf(event, sectors, sectorId, nid);
      snapshotNestedFromFields(event, sectors, sectorId, inner);
    });
  }

  function eventIndex(doc) {
    const map = {};
    (doc.products || []).forEach(function (product) {
      (product.processes || []).forEach(function (process) {
        (process.events || []).forEach(function (event) {
          map[event.id] = { product: product, process: process, event: event };
        });
      });
    });
    return map;
  }

  function treeEventIds(doc) {
    const ids = [];
    (doc.products || []).forEach(function (product) {
      (product.processes || []).forEach(function (process) {
        (process.events || []).forEach(function (event) {
          ids.push(event.id);
        });
      });
    });
    return ids;
  }

  function ensureTocOrder(doc) {
    const existing = eventIndex(doc);
    const next = [];
    const seen = {};
    (doc.tocOrder || []).forEach(function (id) {
      if (existing[id] && !seen[id]) {
        next.push(id);
        seen[id] = true;
      }
    });
    treeEventIds(doc).forEach(function (id) {
      if (!seen[id]) {
        next.push(id);
        seen[id] = true;
      }
    });
    doc.tocOrder = next;
    return next;
  }

  function tocEntries(doc) {
    const map = eventIndex(doc);
    return ensureTocOrder(doc).map(function (id) { return map[id]; }).filter(Boolean);
  }

  function moveAt(arr, from, to) {
    if (from < 0 || to < 0 || from === to) return false;
    const item = arr.splice(from, 1)[0];
    if (from < to) to -= 1;
    arr.splice(to, 0, item);
    return true;
  }

  function moveById(arr, fromId, toId) {
    return moveAt(arr, (arr || []).findIndex(function (x) { return x.id === fromId; }), (arr || []).findIndex(function (x) { return x.id === toId; }));
  }

  function moveId(arr, fromId, toId) {
    return moveAt(arr, (arr || []).indexOf(fromId), (arr || []).indexOf(toId));
  }

  function rebuildTocFromTree(doc) {
    doc.tocOrder = treeEventIds(doc);
    return doc.tocOrder;
  }

  function detailNote(process, event) {
    if (process && process.manual) return "매뉴얼";
    return String((event && event.note) || "").trim();
  }

  function moveToc(doc, eventId, delta) {
    const order = ensureTocOrder(doc);
    const i = order.indexOf(eventId);
    if (i < 0) return false;
    const j = i + delta;
    if (j < 0 || j >= order.length) return false;
    const tmp = order[i];
    order[i] = order[j];
    order[j] = tmp;
    return true;
  }

  function moveTocTo(doc, eventId, targetIndex) {
    const order = ensureTocOrder(doc);
    const i = order.indexOf(eventId);
    if (i < 0) return false;
    const j = Math.max(0, Math.min(order.length - 1, targetIndex));
    if (i === j) return false;
    order.splice(i, 1);
    order.splice(j, 0, eventId);
    return true;
  }

  function uniqueSheetName(used, product, process, eventType) {
    let name = sheetNameOf(product, process, eventType);
    if (!name) return "";
    let n = 2;
    let candidate = name;
    while (used[candidate]) {
      candidate = (name.slice(0, 28) + "_" + n).slice(0, 31);
      n += 1;
    }
    used[candidate] = true;
    return candidate;
  }

  function addProduct(doc, name) {
    const product = { id: uid("prd"), name: name || "새 제품", processes: [] };
    doc.products.push(product);
    return product;
  }

  function addProcess(product, name) {
    const process = {
      id: uid("prc"),
      name: name || "새 공정",
      equipmentName: "-",
      vendorName: "",
      sheetPrefix: "",
      manual: false,
      events: []
    };
    product.processes.push(process);
    return process;
  }

  function snapshotFields(event, sector) {
    return (sector.fields || []).map(function (field) {
      const over = fieldValue(event, sector.id, field.name);
      return {
        name: field.name,
        type: field.type || "",
        nested: field.nested,
        description: over.description != null && over.description !== "" ? over.description : (field.description || ""),
        detail: over.detail != null && over.detail !== "" ? over.detail : (field.detail || ""),
        required: over.required != null && over.required !== "" ? over.required : (field.required || ""),
        example: over.example != null && over.example !== "" ? over.example : (field.example != null ? field.example : "")
      };
    });
  }

  function fieldsOf(event, sector) {
    if (!event.items) event.items = {};
    if (!Array.isArray(event.items[sector.id])) {
      event.items[sector.id] = snapshotFields(event, sector);
    }
    return event.items[sector.id];
  }

  function materializeEvent(event, sectors) {
    const eventType = findEventType(sectors, event.typeId);
    if (!event.items) event.items = {};
    if (!event.rows) event.rows = {};
    if (!event.values) event.values = {};
    if (!eventType) return event;
    (eventType.sectors || []).forEach(function (sid) {
      const sector = sectorOf(sectors, sid);
      if (!sector) return;
      if (sector.kind === "object") snapshotNestedFromFields(event, sectors, sid, fieldsOf(event, sector));
      if (sector.kind === "rows") rowsOf(event, sid, sector);
    });
    return event;
  }

  function materializeDoc(doc, sectors) {
    (doc.products || []).forEach(function (product) {
      (product.processes || []).forEach(function (process) {
        (process.events || []).forEach(function (event) {
          materializeEvent(event, sectors);
        });
      });
    });
    ensureTocOrder(doc);
    return doc;
  }

  function addEvent(process, eventType, sectors) {
    const ev = {
      id: uid("evt"),
      typeId: eventType.id,
      note: "",
      values: {},
      rows: {},
      items: {}
    };
    const src = sectors || loadSectors();
    (eventType.sectors || []).forEach(function (sid) {
      const sector = sectorOf(src, sid);
      if (!sector) return;
      if (sector.kind === "rows") {
        ev.rows[sid] = clone(sector.defaultRows || []);
      }
      if (sector.kind === "object") {
        ev.items[sid] = snapshotFields(ev, sector);
        snapshotNestedFromFields(ev, src, sid, ev.items[sid]);
      }
    });
    process.events.push(ev);
    const doc = arguments[3];
    if (doc) {
      ensureTocOrder(doc);
      if (doc.tocOrder.indexOf(ev.id) === -1) doc.tocOrder.push(ev.id);
    }
    return ev;
  }

  function uniquifyDocIds(doc) {
    const used = {};
    let reissued = 0;
    function take(id, prefix) {
      const cur = String(id || "").trim();
      if (cur && !used[cur]) {
        used[cur] = true;
        return cur;
      }
      let next;
      do {
        next = uid(prefix);
      } while (used[next]);
      used[next] = true;
      reissued += 1;
      return next;
    }
    (doc.products || []).forEach(function (product) {
      product.id = take(product.id, "prd");
      (product.processes || []).forEach(function (process) {
        process.id = take(process.id, "prc");
        (process.events || []).forEach(function (event) {
          event.id = take(event.id, "evt");
        });
      });
    });
    rebuildTocFromTree(doc);
    return reissued;
  }

  function toBundle(doc, sectors) {
    uniquifyDocIds(doc);
    return {
      kind: "linesoft.msg.bundle",
      version: 1,
      title: doc.title,
      versionLabel: doc.versionLabel,
      products: doc.products,
      tocOrder: doc.tocOrder,
      sectors: sectors
    };
  }

  function fromBundle(parsed, currentSectors) {
    if (!parsed || typeof parsed !== "object") throw new Error("JSON 형식이 올바르지 않습니다.");
    if (parsed.kind === "linesoft.msg.bundle" || (Array.isArray(parsed.products) && parsed.sectors && parsed.sectors.events)) {
      const doc = {
        title: parsed.title || "설비 메시지 정의서",
        versionLabel: parsed.versionLabel || "",
        products: parsed.products || [],
        tocOrder: parsed.tocOrder || []
      };
      const sectors = parsed.sectors && parsed.sectors.events ? parsed.sectors : (currentSectors || defaultSectors());
      const reissued = uniquifyDocIds(doc);
      materializeDoc(doc, sectors);
      return { doc: doc, sectors: sectors, reissued: reissued };
    }
    if (Array.isArray(parsed.products)) {
      const sectors = currentSectors || defaultSectors();
      const reissued = uniquifyDocIds(parsed);
      materializeDoc(parsed, sectors);
      return { doc: parsed, sectors: sectors, reissued: reissued };
    }
    throw new Error("products 배열이 없습니다.");
  }

  function findById(list, id) {
    return (list || []).find(function (x) { return x.id === id; }) || null;
  }

  function removeById(list, id) {
    const idx = (list || []).findIndex(function (x) { return x.id === id; });
    if (idx >= 0) list.splice(idx, 1);
    return idx >= 0;
  }

  function countEventTypeUsage(doc, typeId) {
    let n = 0;
    (doc.products || []).forEach(function (product) {
      (product.processes || []).forEach(function (process) {
        (process.events || []).forEach(function (event) {
          if (event.typeId === typeId) n += 1;
        });
      });
    });
    return n;
  }

  function renameEventTypeId(doc, sectors, oldId, newId) {
    const ev = findEventType(sectors, oldId);
    if (!ev || !newId || oldId === newId) return false;
    ev.id = newId;
    (doc.products || []).forEach(function (product) {
      (product.processes || []).forEach(function (process) {
        (process.events || []).forEach(function (event) {
          if (event.typeId === oldId) event.typeId = newId;
        });
      });
    });
    return true;
  }

  function removeEventType(sectors, id) {
    const list = sectors.events || [];
    const i = list.findIndex(function (ev) { return ev.id === id; });
    if (i < 0) return false;
    list.splice(i, 1);
    return true;
  }

  function sheetPrefixOf(product, process) {
    if (process.sheetPrefix) return process.sheetPrefix;
    const p = String(product.name || "").replace(/\([^)]*\)/g, "").replace(/\s+/g, "");
    const g = String(process.name || "")
      .replace(/IR_Filter\s*Attach/i, "IFA")
      .replace(/\s+/g, "");
    return (p + "_" + g).slice(0, 22);
  }

  function eventSheetSuffix(eventType) {
    return String(eventType.name || eventType.id || "").replace(/\s+/g, "_");
  }

  function sheetNameOf(product, process, eventType) {
    if (!eventType.generateSheet) return "";
    const name = sheetPrefixOf(product, process) + "(" + eventSheetSuffix(eventType) + ")";
    return name.slice(0, 31);
  }

  function fieldValue(event, sectorId, fieldName) {
    const bag = ((event.values || {})[sectorId] || {})[fieldName] || {};
    return bag;
  }

  function setFieldValue(event, sectorId, fieldName, key, value) {
    if (!event.values) event.values = {};
    if (!event.values[sectorId]) event.values[sectorId] = {};
    if (!event.values[sectorId][fieldName]) event.values[sectorId][fieldName] = {};
    event.values[sectorId][fieldName][key] = value;
  }

  function kvValue(event, sectorId, key, fallback) {
    const bag = (event.values || {})[sectorId] || {};
    if (bag[key] === undefined || bag[key] === "") return fallback == null ? "" : fallback;
    return bag[key];
  }

  function setKvValue(event, sectorId, key, value) {
    if (!event.values) event.values = {};
    if (!event.values[sectorId]) event.values[sectorId] = {};
    event.values[sectorId][key] = value;
  }

  function rowsOf(event, sectorId, sector) {
    if (!event.rows) event.rows = {};
    if (!Array.isArray(event.rows[sectorId])) {
      event.rows[sectorId] = clone((sector && sector.defaultRows) || []);
    }
    return event.rows[sectorId];
  }

  function resolvedField(event, sectorId, field) {
    const over = fieldValue(event, sectorId, field.name);
    return {
      name: field.name,
      type: field.type,
      nested: field.nested,
      description: over.description != null && over.description !== "" ? over.description : (field.description || ""),
      detail: over.detail != null && over.detail !== "" ? over.detail : (field.detail || ""),
      required: over.required != null && over.required !== "" ? over.required : (field.required || ""),
      example: over.example != null && over.example !== "" ? over.example : (field.example != null ? field.example : "")
    };
  }

  function buildObjectFromFields(sectors, event, sectorId, fields, itemRows) {
    const obj = {};
    (fields || []).forEach(function (field) {
      const resolved = resolvedField(event, sectorId, field);
      const nid = nestedIdOf(field);
      if (nid) {
        const inner = nestedFieldsOf(event, sectors, sectorId, nid);
        if (String(field.type || "").indexOf("[]") !== -1) {
          if (nid === "ITEM" && itemRows && itemRows.length) {
            obj[field.name] = itemRows.map(function (row) {
              return {
                item: row.item || "",
                site: row.site || "",
                value: "{{" + (row.item || "value") + "}}"
              };
            });
          } else {
            obj[field.name] = [buildObjectFromFields(sectors, event, sectorId, inner, itemRows)];
          }
        } else {
          obj[field.name] = buildObjectFromFields(sectors, event, sectorId, inner, itemRows);
        }
      } else {
        obj[field.name] = resolved.example;
      }
    });
    return obj;
  }

  function buildExample(sectors, event, exampleSector) {
    const itemRows = exampleSector.itemListFrom ? rowsOf(event, exampleSector.itemListFrom, sectorOf(sectors, exampleSector.itemListFrom)) : [];
    const reqSec = sectorOf(sectors, exampleSector.requestSector);
    const resSec = sectorOf(sectors, exampleSector.responseSector);
    const request = reqSec ? buildObjectFromFields(sectors, event, reqSec.id, fieldsOf(event, reqSec), itemRows) : {};
    const response = resSec ? buildObjectFromFields(sectors, event, resSec.id, fieldsOf(event, resSec), itemRows) : {};
    return {
      request: JSON.stringify(request, null, 2),
      response: JSON.stringify(response, null, 2)
    };
  }

  function exampleOverride(event, sectorId) {
    return ((event.values || {})[sectorId] || {});
  }

  global.MsgModel = {
    clone: clone,
    uid: uid,
    defaultSectors: defaultSectors,
    loadSectors: loadSectors,
    saveSectors: saveSectors,
    emptyDoc: emptyDoc,
    loadDoc: loadDoc,
    saveDoc: saveDoc,
    findEventType: findEventType,
    sectorOf: sectorOf,
    nestedOf: nestedOf,
    nestedIdOf: nestedIdOf,
    nestedTitleOf: nestedTitleOf,
    nestedColumnsOf: nestedColumnsOf,
    nestedFieldsOf: nestedFieldsOf,
    syncFieldNested: syncFieldNested,
    snapshotNestedFromFields: snapshotNestedFromFields,
    addProduct: addProduct,
    addProcess: addProcess,
    addEvent: addEvent,
    fieldsOf: fieldsOf,
    materializeEvent: materializeEvent,
    materializeDoc: materializeDoc,
    toBundle: toBundle,
    fromBundle: fromBundle,
    uniquifyDocIds: uniquifyDocIds,
    findById: findById,
    removeById: removeById,
    countEventTypeUsage: countEventTypeUsage,
    renameEventTypeId: renameEventTypeId,
    removeEventType: removeEventType,
    sheetPrefixOf: sheetPrefixOf,
    sheetNameOf: sheetNameOf,
    fieldValue: fieldValue,
    setFieldValue: setFieldValue,
    kvValue: kvValue,
    setKvValue: setKvValue,
    rowsOf: rowsOf,
    resolvedField: resolvedField,
    buildExample: buildExample,
    exampleOverride: exampleOverride,
    tocEntries: tocEntries,
    ensureTocOrder: ensureTocOrder,
    moveToc: moveToc,
    moveTocTo: moveTocTo,
    moveById: moveById,
    moveId: moveId,
    rebuildTocFromTree: rebuildTocFromTree,
    detailNote: detailNote,
    uniqueSheetName: uniqueSheetName
  };
})(window);
