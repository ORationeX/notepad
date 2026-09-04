(function (global) {
  const YELLOW = "FFFFFF00";
  const GREEN = "FF00B050";
  const NESTED_FILL = "FFD9D9D9";
  const WHITE = "FFFFFFFF";
  const BLACK = "FF000000";
  const RED = "FFFF0000";
  const FONT = "맑은 고딕";

  function thin() {
    const s = { style: "thin", color: { argb: BLACK } };
    return { top: s, left: s, bottom: s, right: s };
  }

  function mediumOuter(edges) {
    const m = { style: "medium", color: { argb: BLACK } };
    const t = { style: "thin", color: { argb: BLACK } };
    return {
      top: edges.top ? m : t,
      left: edges.left ? m : t,
      bottom: edges.bottom ? m : t,
      right: edges.right ? m : t
    };
  }

  function font(opts) {
    return Object.assign({ name: FONT, size: 11, color: { argb: BLACK } }, opts || {});
  }

  function fillArgb(argb) {
    return { type: "pattern", pattern: "solid", fgColor: { argb: argb } };
  }

  function apply(cell, style) {
    cell.font = font(style.font);
    if (style.fill) cell.fill = fillArgb(style.fill);
    cell.border = style.border || thin();
    cell.alignment = Object.assign({ vertical: "middle" }, style.align || {});
  }

  function colLetter(n) {
    let s = "";
    while (n > 0) {
      const m = (n - 1) % 26;
      s = String.fromCharCode(65 + m) + s;
      n = Math.floor((n - 1) / 26);
    }
    return s;
  }

  function merge(ws, r1, c1, r2, c2) {
    if (r1 === r2 && c1 === c2) return;
    ws.mergeCells(r1, c1, r2, c2);
  }

  function setWidths(ws, widths) {
    Object.keys(widths).forEach(function (col) {
      ws.getColumn(col).width = widths[col];
    });
  }

  function writeHeaderRow(ws, row, cols, values, lastCol) {
    values.forEach(function (v, i) {
      const cell = ws.getCell(row, cols[i]);
      cell.value = v;
      apply(cell, {
        fill: YELLOW,
        border: mediumOuter({
          top: true,
          bottom: true,
          left: i === 0,
          right: cols[i] === lastCol
        })
      });
    });
    for (let c = cols[0]; c <= lastCol; c++) {
      if (!ws.getCell(row, c).value && !(cols.indexOf(c) >= 0)) {
        apply(ws.getCell(row, c), { fill: YELLOW, border: thin() });
      }
    }
  }

  function writeTitle(ws, row, c1, c2, text, extra) {
    merge(ws, row, c1, row, c2);
    const cell = ws.getCell(row, c1);
    cell.value = text;
    apply(cell, Object.assign({
      font: { name: FONT, size: 11, bold: !!(extra && extra.bold), color: { argb: extra && extra.color ? extra.color : BLACK } },
      fill: extra && extra.fill,
      align: { horizontal: extra && extra.center ? "center" : "left", vertical: "middle" },
      border: mediumOuter({ top: true, left: true, right: true, bottom: extra && extra.bottom })
    }, {}));
    for (let c = c1 + 1; c <= c2; c++) {
      apply(ws.getCell(row, c), {
        fill: extra && extra.fill,
        border: mediumOuter({ top: true, right: c === c2, bottom: extra && extra.bottom })
      });
    }
  }

  function writeDataRow(ws, row, startCol, values, lastCol, opts) {
    opts = opts || {};
    values.forEach(function (v, i) {
      const cell = ws.getCell(row, startCol + i);
      cell.value = v == null ? "" : v;
      apply(cell, {
        font: { name: FONT, size: 11, color: { argb: opts.red ? RED : BLACK } },
        border: thin(),
        align: opts.wrap ? { wrapText: true, vertical: "top" } : { vertical: "middle" }
      });
    });
    for (let c = startCol + values.length; c <= lastCol; c++) {
      apply(ws.getCell(row, c), { border: thin() });
    }
  }

  function columnKeys(sector) {
    return sector.columns || ["name", "type", "description", "detail"];
  }

  function headerLabels(cols) {
    const map = { name: "이름", type: "타입", description: "설명", detail: "상세설명", required: "필수" };
    return cols.map(function (c) { return map[c] || c; });
  }

  function fieldCells(field, cols) {
    return cols.map(function (c) { return field[c] || ""; });
  }

  function writeFieldTable(ws, row, event, sectorId, def, lastCol) {
    const cols = def.columns || ["name", "type", "description"];
    writeHeaderRow(ws, row, cols.map(function (_, i) { return 2 + i; }), headerLabels(cols), lastCol);
    row += 1;
    (def.fields || []).forEach(function (field) {
      const resolved = MsgModel.resolvedField(event, sectorId, field);
      writeDataRow(ws, row, 2, fieldCells(resolved, cols), lastCol);
      row += 1;
    });
    return row;
  }

  function writeNestedBlocks(ws, row, sectors, event, sectorId, fields, lastCol) {
    (fields || []).forEach(function (field) {
      const nid = MsgModel.nestedIdOf(field);
      if (!nid) return;
      const inner = MsgModel.nestedFieldsOf(event, sectors, sectorId, nid);
      const title = MsgModel.nestedTitleOf(sectors, nid);
      const cols = MsgModel.nestedColumnsOf(sectors, nid);
      writeTitle(ws, row, 2, lastCol, title, { bold: true, color: GREEN, fill: NESTED_FILL, center: true, bottom: true });
      row += 1;
      if (inner.length > 1) {
        row = writeFieldTable(ws, row, event, sectorId, { columns: cols, fields: inner }, lastCol);
      } else {
        inner.forEach(function (child) {
          const resolved = MsgModel.resolvedField(event, sectorId, child);
          writeDataRow(ws, row, 2, fieldCells(resolved, cols), lastCol);
          row += 1;
        });
      }
      row = writeNestedBlocks(ws, row, sectors, event, sectorId, inner, lastCol);
    });
    return row;
  }

  function writeObjectSector(ws, row, sectors, event, sector, lastCol) {
    const fields = MsgModel.fieldsOf(event, sector);
    writeTitle(ws, row, 2, lastCol, sector.title);
    row += 1;
    row = writeFieldTable(ws, row, event, sector.id, { columns: sector.columns, fields: fields }, lastCol);
    row = writeNestedBlocks(ws, row, sectors, event, sector.id, fields, lastCol);
    return row + 1;
  }

  function writeKvSector(ws, row, event, sector, eventType, lastCol) {
    writeTitle(ws, row, 2, Math.max(3, lastCol > 4 ? 3 : lastCol), sector.title);
    row += 1;
    writeHeaderRow(ws, row, [2, 3], ["구분", "설명"], 3);
    row += 1;
    (sector.fields || []).forEach(function (field) {
      const fallback = (eventType.defaults || {})[field.key] || "";
      const value = MsgModel.kvValue(event, sector.id, field.key, fallback);
      writeDataRow(ws, row, 2, [field.label, value], 3);
      row += 1;
    });
    return row + 1;
  }

  const EXCEL_MAX_ROW_HEIGHT = 409;

  function exampleRowHeight(text) {
    const lines = String(text || "").split(/\r?\n/).length;
    return Math.min(EXCEL_MAX_ROW_HEIGHT, Math.max(60, lines * 15));
  }

  function writeExampleBox(ws, row, text, lastCol) {
    merge(ws, row, 2, row, lastCol);
    const cell = ws.getCell(row, 2);
    cell.value = text == null ? "" : text;
    apply(cell, { align: { wrapText: true, vertical: "top", horizontal: "left" }, fill: WHITE });
    for (let c = 3; c <= lastCol; c++) {
      apply(ws.getCell(row, c), { border: thin(), align: { wrapText: true, vertical: "top" }, fill: WHITE });
    }
    ws.getRow(row).height = exampleRowHeight(text);
    return row + 1;
  }

  function writeExampleSector(ws, row, sectors, event, sector, lastCol) {
    const built = MsgModel.buildExample(sectors, event, sector);
    const over = MsgModel.exampleOverride(event, sector.id);
    const req = over.request || built.request;
    const res = over.response || built.response;
    writeTitle(ws, row, 2, lastCol, sector.title);
    row += 1;
    writeTitle(ws, row, 2, lastCol, "요청", { fill: YELLOW });
    row += 1;
    row = writeExampleBox(ws, row, req, lastCol);
    writeTitle(ws, row, 2, lastCol, "응답", { fill: YELLOW });
    row += 1;
    row = writeExampleBox(ws, row, res, lastCol);
    return row + 1;
  }

  function writeRowsSector(ws, row, event, sector, startCol) {
    const cols = sector.columns || [];
    const lastCol = startCol + cols.length - 1;
    writeTitle(ws, row, startCol, lastCol, sector.title, { bold: true, color: GREEN, fill: NESTED_FILL, center: true, bottom: true });
    row += 1;
    writeHeaderRow(ws, row, cols.map(function (_, i) { return startCol + i; }), cols.map(function (c) { return c.header; }), lastCol);
    row += 1;
    const rows = MsgModel.rowsOf(event, sector.id, sector);
    if (!rows.length) {
      writeDataRow(ws, row, startCol, cols.map(function () { return ""; }), lastCol);
      row += 1;
    } else {
      rows.forEach(function (item) {
        writeDataRow(ws, row, startCol, cols.map(function (c) { return item[c.key] == null ? "" : item[c.key]; }), lastCol);
        row += 1;
      });
    }
    return row;
  }

  function sheetHyperlink(sheetName) {
    return "#'" + String(sheetName || "").replace(/'/g, "''") + "'!B2";
  }

  function writeSheetLink(cell, label, sheetName, opts) {
    opts = opts || {};
    cell.value = { text: label, hyperlink: sheetHyperlink(sheetName) };
    apply(cell, {
      font: {
        name: FONT,
        size: 11,
        color: { argb: opts.red ? RED : "FF0563C1" },
        underline: true,
        bold: !!opts.red
      },
      align: { horizontal: "center", vertical: "middle" }
    });
  }

  function addBackToToc(ws) {
    const cell = ws.getCell(1, 2);
    cell.value = { text: "◀ 목차", hyperlink: "#'목차'!B2" };
    cell.font = font({ color: { argb: "FF0563C1" }, underline: true });
  }

  function writeApiSheet(wb, sheetName, sectors, event, eventType) {
    const ws = wb.addWorksheet(sheetName);
    addBackToToc(ws);
    const hasSide = (eventType.sectors || []).some(function (id) {
      const s = MsgModel.sectorOf(sectors, id);
      return s && s.place === "side";
    });
    const lastCol = hasSide ? 5 : 5;
    setWidths(ws, hasSide
      ? { A: 3.7, B: 20.5, C: 32.5, D: 53.5, E: 24, F: 3, G: 18, H: 12, I: 12, J: 79.5 }
      : { A: 3.7, B: 19.2, C: 32.5, D: 53.5, E: 12.4 });
    ws.getColumn(1).width = 3.7;
    let row = 2;
    let sideRow = 0;
    (eventType.sectors || []).forEach(function (sid) {
      const sector = MsgModel.sectorOf(sectors, sid);
      if (!sector) return;
      if (sector.place === "side") {
        sideRow = writeRowsSector(ws, 18, event, sector, 7);
        return;
      }
      if (sector.kind === "kv") row = writeKvSector(ws, row, event, sector, eventType, lastCol);
      else if (sector.kind === "object") row = writeObjectSector(ws, row, sectors, event, sector, lastCol);
      else if (sector.kind === "example") row = writeExampleSector(ws, row, sectors, event, sector, lastCol);
      else if (sector.kind === "rows") row = writeRowsSector(ws, row, event, sector, 2);
    });
    void sideRow;
    return ws;
  }

  function writeTableSheet(wb, sheetName, sectors, event, eventType) {
    const ws = wb.addWorksheet(sheetName);
    addBackToToc(ws);
    setWidths(ws, { A: 3.7, B: 18, C: 14, D: 12, E: 79.5 });
    let row = 2;
    (eventType.sectors || []).forEach(function (sid) {
      const sector = MsgModel.sectorOf(sectors, sid);
      if (!sector) return;
      row = writeRowsSector(ws, row, event, sector, 2);
    });
    return ws;
  }

  function writeToc(wb, planned) {
    const ws = wb.addWorksheet("목차");
    setWidths(ws, { A: 3.7, B: 12.6, C: 18, D: 9.7, E: 16, F: 18, G: 12 });
    writeTitle(ws, 2, 2, 7, (planned.doc && planned.doc.title) || "설비 메시지 정의서", { center: true, fill: NESTED_FILL });
    writeHeaderRow(ws, 3, [2, 3, 4, 5, 6, 7], ["제품명", "공정 명", "설비 명", "설비 업체 명", "이벤트", "상세보기"], 7);
    let row = 4;
    (planned.entries || []).forEach(function (item) {
      const event = item.event;
      const process = item.process;
      const product = item.product;
      const eventType = item.eventType;
      const name = eventType ? eventType.name : event.typeId;
      writeDataRow(ws, row, 2, [
        product.name,
        process.name,
        process.equipmentName || "-",
        process.vendorName || "",
        name
      ], 7);
      const linkCell = ws.getCell(row, 7);
      if (process.manual) {
        if (item.sheetName) {
          writeSheetLink(linkCell, "매뉴얼", item.sheetName, { red: true });
        } else {
          linkCell.value = "매뉴얼";
          apply(linkCell, {
            font: { name: FONT, size: 11, color: { argb: RED }, bold: true },
            align: { horizontal: "center", vertical: "middle" }
          });
        }
      } else if (item.sheetName) {
        writeSheetLink(linkCell, "상세보기", item.sheetName);
      } else {
        linkCell.value = "";
        apply(linkCell, { align: { horizontal: "center", vertical: "middle" } });
      }
      row += 1;
    });
    return ws;
  }

  function planExport(doc, sectors, eventIds) {
    const allow = eventIds && eventIds.length ? eventIds.reduce(function (m, id) { m[id] = true; return m; }, {}) : null;
    const used = {};
    const entries = MsgModel.tocEntries(doc).filter(function (item) {
      return !allow || allow[item.event.id];
    }).map(function (item) {
      const eventType = MsgModel.findEventType(sectors, item.event.typeId);
      const sheetName = eventType && eventType.generateSheet
        ? MsgModel.uniqueSheetName(used, item.product, item.process, eventType)
        : "";
      return {
        product: item.product,
        process: item.process,
        event: item.event,
        eventType: eventType,
        sheetName: sheetName
      };
    });
    return { doc: doc, entries: entries };
  }

  async function exportWorkbook(doc, sectors, eventIds) {
    const wb = new ExcelJS.Workbook();
    wb.creator = "라인소프트 설비 메시지 정의서";
    const planned = planExport(doc, sectors, eventIds);
    writeToc(wb, planned);
    planned.entries.forEach(function (item) {
      if (!item.sheetName || !item.eventType) return;
      if (item.eventType.sheetKind === "table") writeTableSheet(wb, item.sheetName, sectors, item.event, item.eventType);
      else writeApiSheet(wb, item.sheetName, sectors, item.event, item.eventType);
    });
    return wb;
  }

  function downloadBlob(blob, filename) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      URL.revokeObjectURL(a.href);
      a.remove();
    }, 800);
  }

  async function exportXlsx(doc, sectors, eventIds) {
    const wb = await exportWorkbook(doc, sectors, eventIds);
    const buf = await wb.xlsx.writeBuffer();
    const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const filename = (doc.title || "설비메시지정의서") + "_" + stamp + ".xlsx";
    downloadBlob(new Blob([buf], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }), filename);
    return filename;
  }

  function cellStr(ws, r, c) {
    const v = ws.getCell(r, c).value;
    if (v == null) return "";
    if (typeof v === "object") {
      if (v.richText) return v.richText.map(function (x) { return x.text; }).join("");
      if (v.text) return v.text;
      if (v.result != null) return String(v.result);
    }
    return String(v);
  }

  function maxRow(ws) {
    return ws.actualRowCount || ws.rowCount || 0;
  }

  function parseToc(ws) {
    const rows = [];
    let header = 0;
    for (let r = 1; r <= Math.min(10, maxRow(ws)); r++) {
      if (cellStr(ws, r, 2).indexOf("제품") !== -1) { header = r; break; }
    }
    if (!header) header = 3;
    const hasDetail = cellStr(ws, header, 7).indexOf("상세정보") !== -1;
    const noteCol = hasDetail ? 7 : 0;
    const viewCol = hasDetail ? 8 : 7;
    for (let r = header + 1; r <= maxRow(ws); r++) {
      const product = cellStr(ws, r, 2).trim();
      if (!product) continue;
      const processRaw = cellStr(ws, r, 3).trim();
      const viewVal = cellStr(ws, r, viewCol);
      const noteVal = noteCol ? cellStr(ws, r, noteCol).trim() : "";
      const manual = /매뉴얼/.test(processRaw) || /매뉴얼/.test(noteVal) || /매뉴얼/.test(viewVal);
      rows.push({
        product: product,
        process: processRaw.replace(/\s*매뉴얼\s*$/, "").trim() || processRaw,
        equipmentName: cellStr(ws, r, 4).trim() || "-",
        vendorName: cellStr(ws, r, 5).trim(),
        eventName: cellStr(ws, r, 6).trim(),
        note: noteVal && noteVal !== "매뉴얼" ? noteVal : "",
        manual: manual
      });
    }
    return rows;
  }

  function findSheet(wb, name) {
    return wb.getWorksheet(name) || wb.worksheets.find(function (s) { return s.name === name; }) || null;
  }

  function parseKv(ws) {
    const out = {};
    const last = maxRow(ws);
    for (let r = 1; r <= last; r++) {
      const k = cellStr(ws, r, 2).trim();
      if (k === "EndPoint" || k === "Method" || k === "설명") {
        const key = k === "EndPoint" ? "endPoint" : k === "Method" ? "method" : "description";
        out[key] = cellStr(ws, r, 3);
      }
    }
    return out;
  }

  function parseFieldTable(ws, title) {
    const last = maxRow(ws);
    let start = 0;
    for (let r = 1; r <= last; r++) {
      if (cellStr(ws, r, 2).trim() === title) { start = r; break; }
    }
    if (!start) return { fields: {}, nested: {} };
    const fields = {};
    for (let r = start + 1; r <= last; r++) {
      const name = cellStr(ws, r, 2).trim();
      if (/^\d+\.\s/.test(name) || name === "요청" || name === "응답") break;
      if (!name || name === "이름" || name === "구분") continue;
      fields[name.replace(/\t/g, "")] = {
        name: name.replace(/\t/g, ""),
        type: cellStr(ws, r, 3),
        description: cellStr(ws, r, 4),
        detail: cellStr(ws, r, 5),
        required: cellStr(ws, r, 6)
      };
    }
    return { fields: fields };
  }

  function parseRows(ws, title, colMap, startCol) {
    const last = maxRow(ws);
    const sc = startCol || 2;
    let start = 0;
    for (let r = 1; r <= last; r++) {
      if (cellStr(ws, r, sc).trim() === title) { start = r; break; }
    }
    if (!start) return [];
    const rows = [];
    for (let r = start + 2; r <= last; r++) {
      const first = cellStr(ws, r, sc).trim();
      if (!first) continue;
      if (/^\d+\.\s/.test(first)) break;
      const item = {};
      colMap.forEach(function (key, i) {
        item[key] = ws.getCell(r, sc + i).value;
        if (item[key] == null) item[key] = "";
        else if (typeof item[key] === "object") item[key] = cellStr(ws, r, sc + i);
      });
      rows.push(item);
    }
    return rows;
  }

  function parseExample(ws) {
    const last = maxRow(ws);
    let req = "";
    let res = "";
    for (let r = 1; r <= last; r++) {
      const t = cellStr(ws, r, 2).trim();
      if (t === "요청") {
        for (let k = r + 1; k <= last; k++) {
          const v = cellStr(ws, k, 2);
          if (v.trim().indexOf("{") === 0) { req = v; break; }
          if (cellStr(ws, k, 2).trim() === "응답") break;
        }
      }
      if (t === "응답") {
        for (let k = r + 1; k <= last; k++) {
          const v = cellStr(ws, k, 2);
          if (v.trim().indexOf("{") === 0) { res = v; break; }
        }
      }
    }
    return { request: req, response: res };
  }

  function applyParsedFields(event, sectorId, parsed, sector, sectors) {
    if (!event.values) event.values = {};
    event.values[sectorId] = event.values[sectorId] || {};
    const names = Object.keys(parsed.fields || {});
    names.forEach(function (name) {
      const src = parsed.fields[name];
      event.values[sectorId][name] = {
        description: src.description || "",
        detail: src.detail || "",
        required: src.required || ""
      };
    });
    if (sector && sector.kind === "object") {
      const current = MsgModel.fieldsOf(event, sector);
      const byName = {};
      current.forEach(function (f) { byName[f.name] = f; });
      event.items[sectorId] = names.map(function (name) {
        const src = parsed.fields[name];
        const prev = byName[name] || {};
        return {
          name: name,
          type: src.type || prev.type || "",
          nested: prev.nested || MsgModel.nestedIdOf({ type: src.type || prev.type || "", nested: prev.nested }),
          description: src.description || prev.description || "",
          detail: src.detail || prev.detail || "",
          required: src.required || prev.required || "",
          example: prev.example || ""
        };
      });
      MsgModel.snapshotNestedFromFields(event, sectors, sectorId, event.items[sectorId]);
    }
  }

  async function importXlsx(buffer, sectors) {
    const wb = new ExcelJS.Workbook();
    await wb.xlsx.load(buffer);
    const tocSheet = findSheet(wb, "목차") || wb.worksheets[0];
    const toc = parseToc(tocSheet);
    const doc = MsgModel.emptyDoc();
    doc.title = cellStr(tocSheet, 2, 2) || "설비 메시지 정의서";
    const productMap = {};
    const processMap = {};
    toc.forEach(function (row) {
      if (!productMap[row.product]) {
        const p = MsgModel.addProduct(doc, row.product);
        productMap[row.product] = p;
      }
      const product = productMap[row.product];
      const pk = row.product + "\0" + row.process;
      if (!processMap[pk]) {
        const g = MsgModel.addProcess(product, row.process);
        g.equipmentName = row.equipmentName;
        g.vendorName = row.vendorName;
        processMap[pk] = g;
      }
      const process = processMap[pk];
      if (row.manual || /매뉴얼/.test(String(row.note || ""))) process.manual = true;
      const eventType = MsgModel.findEventType(sectors, row.eventName) || { id: row.eventName, name: row.eventName, generateSheet: false, sectors: [] };
      const event = MsgModel.addEvent(process, eventType, sectors, doc);
      event.note = row.note && row.note !== "매뉴얼" ? row.note : "";
      if (!eventType.generateSheet) return;
      const sheet = findSheet(wb, MsgModel.sheetNameOf(product, process, eventType));
      if (!sheet) return;
      if (eventType.sheetKind === "table") {
        const sector = MsgModel.sectorOf(sectors, (eventType.sectors || [])[0]);
        if (sector) event.rows[sector.id] = parseRows(sheet, sector.title, sector.columns.map(function (c) { return c.key; }), 2);
        return;
      }
      (eventType.sectors || []).forEach(function (sid) {
        const sector = MsgModel.sectorOf(sectors, sid);
        if (!sector) return;
        if (sector.kind === "kv") {
          event.values[sid] = parseKv(sheet);
        } else if (sector.kind === "object") {
          applyParsedFields(event, sid, parseFieldTable(sheet, sector.title), sector, sectors);
        } else if (sector.kind === "example") {
          event.values[sid] = parseExample(sheet);
        } else if (sector.kind === "rows") {
          const startCol = sector.place === "side" ? 7 : 2;
          event.rows[sid] = parseRows(sheet, sector.title, sector.columns.map(function (c) { return c.key; }), startCol);
        }
      });
    });
    MsgModel.materializeDoc(doc, sectors);
    return doc;
  }

  global.MsgExcel = {
    exportXlsx: exportXlsx,
    importXlsx: importXlsx,
    exportWorkbook: exportWorkbook
  };
})(window);
