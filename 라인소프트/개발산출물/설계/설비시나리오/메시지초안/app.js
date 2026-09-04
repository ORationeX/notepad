(function (global) {
  const M = global.MsgModel;

  const state = {
    doc: M.loadDoc(),
    sectors: M.loadSectors(),
    tab: "edit",
    sel: { productId: "", processId: "", eventId: "" },
    checked: {},
    masterEventId: "",
    vendorFilter: "",
    newEventTypeId: "",
    collapsed: loadCollapsed(),
    msg: "",
    msgType: ""
  };

  function $(id) { return document.getElementById(id); }

  function collapsedStoreKey() { return "linesoft.msg.collapsed"; }

  function loadCollapsed() {
    try {
      const raw = sessionStorage.getItem(collapsedStoreKey());
      const parsed = raw ? JSON.parse(raw) : {};
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (e) {
      return {};
    }
  }

  function saveCollapsed() {
    try { sessionStorage.setItem(collapsedStoreKey(), JSON.stringify(state.collapsed)); } catch (e) {}
  }

  function collapseKey(kind, id) { return kind + ":" + id; }

  function isCollapsed(kind, id) { return !!state.collapsed[collapseKey(kind, id)]; }

  function setCollapsed(kind, id, on) {
    const key = collapseKey(kind, id);
    if (on) state.collapsed[key] = true;
    else delete state.collapsed[key];
    saveCollapsed();
  }

  function foldBtn(act, collapsed, attrs) {
    return '<button type="button" class="tree-fold" draggable="false" data-act="' + act + '" ' + attrs +
      ' title="' + (collapsed ? "펼치기" : "접기") + '" aria-expanded="' + (collapsed ? "false" : "true") + '">' +
      (collapsed ? "▶" : "▼") + "</button>";
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  function persist() {
    M.saveDoc(state.doc);
    M.saveSectors(state.sectors);
  }

  function flash(text, type) {
    state.msg = text;
    state.msgType = type || "";
    const el = $("app-msg");
    if (!el) return;
    el.className = "msg " + (type || "");
    el.textContent = text;
  }

  function selected() {
    const product = M.findById(state.doc.products, state.sel.productId);
    const process = product ? M.findById(product.processes, state.sel.processId) : null;
    const event = process ? M.findById(process.events, state.sel.eventId) : null;
    return { product: product, process: process, event: event };
  }

  function ensureSelection() {
    if (!state.doc.products.length) return;
    if (!M.findById(state.doc.products, state.sel.productId)) {
      state.sel.productId = state.doc.products[0].id;
      state.sel.processId = "";
      state.sel.eventId = "";
    }
    const product = M.findById(state.doc.products, state.sel.productId);
    if (product && product.processes.length && !M.findById(product.processes, state.sel.processId)) {
      state.sel.processId = "";
      state.sel.eventId = "";
    }
  }

  function selectProduct(id) {
    state.sel = { productId: id, processId: "", eventId: "" };
    state.tab = "edit";
    render();
  }

  function selectProcess(productId, processId) {
    state.sel = { productId: productId, processId: processId, eventId: "" };
    state.tab = "edit";
    render();
  }

  function selectEvent(productId, processId, eventId) {
    state.sel = { productId: productId, processId: processId, eventId: eventId };
    state.tab = "edit";
    render();
  }

  function bindTree() {
    $("tree").onclick = function (e) {
      const btn = e.target.closest("[data-act]");
      if (!btn) return;
      const act = btn.getAttribute("data-act");
      const pid = btn.getAttribute("data-product");
      const gid = btn.getAttribute("data-process");
      const eid = btn.getAttribute("data-event");
      if (act === "toggle-product") {
        setCollapsed("prd", pid, !isCollapsed("prd", pid));
        renderTree();
        return;
      }
      if (act === "toggle-process") {
        setCollapsed("prc", gid, !isCollapsed("prc", gid));
        renderTree();
        return;
      }
      if (act === "sel-product") selectProduct(pid);
      if (act === "sel-process") selectProcess(pid, gid);
      if (act === "sel-event") selectEvent(pid, gid, eid);
      if (act === "check-product") {
        const product = M.findById(state.doc.products, pid);
        setGroupChecked(eventIdsOfProduct(product), !groupAllChecked(eventIdsOfProduct(product)));
        render();
        return;
      }
      if (act === "check-process") {
        const product = M.findById(state.doc.products, pid);
        const process = product ? M.findById(product.processes, gid) : null;
        setGroupChecked(eventIdsOfProcess(process), !groupAllChecked(eventIdsOfProcess(process)));
        render();
        return;
      }
      if (act === "check-event") {
        state.checked[eid] = !state.checked[eid];
        render();
        return;
      }
      if (act === "add-product") {
        const p = M.addProduct(state.doc, "새 제품");
        persist();
        selectProduct(p.id);
      }
      if (act === "add-process") {
        const product = M.findById(state.doc.products, pid);
        if (!product) return;
        const g = M.addProcess(product, "새 공정");
        if (state.vendorFilter && state.vendorFilter !== "(미입력)") g.vendorName = state.vendorFilter;
        setCollapsed("prd", product.id, false);
        persist();
        selectProcess(product.id, g.id);
      }
      if (act === "add-event") {
        const product = M.findById(state.doc.products, pid);
        const process = product ? M.findById(product.processes, gid) : null;
        if (!process) return;
        const typeSel = $("new-event-type");
        const typeId = (typeSel && typeSel.value) || state.newEventTypeId;
        const eventType = M.findEventType(state.sectors, typeId);
        if (!eventType) return;
        const ev = M.addEvent(process, eventType, state.sectors, state.doc);
        setCollapsed("prd", product.id, false);
        setCollapsed("prc", process.id, false);
        persist();
        selectEvent(product.id, process.id, ev.id);
      }
    };

    bindTreeDrag();
  }

  function bindTreeDrag() {
    const tree = $("tree");
    if (!tree || tree.dataset.dragBound) return;
    tree.dataset.dragBound = "1";
    let drag = null;
    let blockDrag = false;

    tree.addEventListener("mousedown", function (e) {
      const el = eventEl(e);
      blockDrag = !!(el && el.closest("input, select, .tree-mini, .btn, button"));
    });

    tree.addEventListener("dragstart", function (e) {
      if (blockDrag) {
        e.preventDefault();
        return;
      }
      const el = eventEl(e);
      const row = el && el.closest("[data-drag]");
      if (!row) return;
      e.stopPropagation();
      drag = {
        type: row.getAttribute("data-drag"),
        product: row.getAttribute("data-product") || "",
        process: row.getAttribute("data-process") || "",
        event: row.getAttribute("data-event") || ""
      };
      row.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      try { e.dataTransfer.setData("text/plain", drag.type); } catch (err) {}
    });

    tree.addEventListener("dragover", function (e) {
      const row = compatibleDropRow(e.target, drag);
      if (!row) return;
      e.preventDefault();
      tree.querySelectorAll(".drag-over").forEach(function (el) { el.classList.remove("drag-over"); });
      if (row !== tree.querySelector(".dragging")) row.classList.add("drag-over");
    });

    tree.addEventListener("dragleave", function (e) {
      const row = e.target.closest("[data-drag]");
      if (row) row.classList.remove("drag-over");
    });

    tree.addEventListener("drop", function (e) {
      const row = compatibleDropRow(e.target, drag);
      if (!row || !drag) return;
      e.preventDefault();
      applyTreeDrop(drag, row);
      drag = null;
      persist();
      render();
    });

    tree.addEventListener("dragend", function () {
      drag = null;
      clearDragOver(tree);
    });
  }

  function clearDragOver(root) {
    root.querySelectorAll(".drag-over, .dragging").forEach(function (el) {
      el.classList.remove("drag-over");
      el.classList.remove("dragging");
    });
  }

  function eventEl(e) {
    const t = e.target;
    return t && t.nodeType === 1 ? t : (t && t.parentElement);
  }

  function compatibleDropRow(target, drag) {
    if (!drag || !target) return null;
    const el = target.nodeType === 1 ? target : target.parentElement;
    if (!el || !el.closest) return null;
    if (drag.type === "product") {
      const wrap = el.closest(".tree-product");
      return wrap ? wrap.querySelector('[data-drag="product"]') : null;
    }
    if (drag.type === "process") {
      const wrap = el.closest(".tree-process");
      if (!wrap) return null;
      const row = wrap.querySelector('[data-drag="process"]');
      if (!row || row.getAttribute("data-product") !== drag.product) return null;
      return row;
    }
    const row = el.closest('[data-drag="event"]');
    if (!row) return null;
    if (row.getAttribute("data-product") !== drag.product || row.getAttribute("data-process") !== drag.process) return null;
    return row;
  }

  function applyTreeDrop(drag, row) {
    if (drag.type === "product") {
      M.moveById(state.doc.products, drag.product, row.getAttribute("data-product"));
    } else if (drag.type === "process") {
      const product = M.findById(state.doc.products, drag.product);
      if (product) M.moveById(product.processes, drag.process, row.getAttribute("data-process"));
    } else if (drag.type === "event") {
      const product = M.findById(state.doc.products, drag.product);
      const process = product ? M.findById(product.processes, drag.process) : null;
      if (process) M.moveById(process.events, drag.event, row.getAttribute("data-event"));
    }
    M.rebuildTocFromTree(state.doc);
  }

  function vendorKey(process) {
    const v = String((process && process.vendorName) || "").trim();
    return v || "(미입력)";
  }

  function vendorList() {
    const map = {};
    (state.doc.products || []).forEach(function (product) {
      (product.processes || []).forEach(function (process) {
        map[vendorKey(process)] = true;
      });
    });
    return Object.keys(map).sort(function (a, b) {
      if (a === "(미입력)") return 1;
      if (b === "(미입력)") return -1;
      return a.localeCompare(b, "ko");
    });
  }

  function processVisible(process) {
    return !state.vendorFilter || vendorKey(process) === state.vendorFilter;
  }

  function productVisible(product) {
    if (!state.vendorFilter) return true;
    const processes = product.processes || [];
    if (!processes.length) return true;
    return processes.some(processVisible);
  }

  function treeListEl() {
    const tree = $("tree");
    return tree ? tree.querySelector(".tree-list") : null;
  }

  function saveTreeScroll() {
    const list = treeListEl();
    return {
      list: list ? list.scrollTop : 0,
      tree: $("tree") ? $("tree").scrollTop : 0,
      win: window.pageYOffset || document.documentElement.scrollTop || 0
    };
  }

  function restoreTreeScroll(saved) {
    function apply() {
      const list = treeListEl();
      if (list) list.scrollTop = saved.list;
      if ($("tree")) $("tree").scrollTop = saved.tree;
      window.scrollTo(0, saved.win);
    }
    apply();
    requestAnimationFrame(apply);
  }

  function renderTree() {
    const savedScroll = saveTreeScroll();
    const s = selected();
    const vendors = vendorList();
    if (state.vendorFilter && vendors.indexOf(state.vendorFilter) < 0) state.vendorFilter = "";
    let html = '<div class="tree-sticky-head">';
    html += '<div class="tree-head"><strong>제품 / 공정 / 이벤트</strong><button class="btn" type="button" data-act="add-product">제품 추가</button></div>';
    html += '<div class="tree-filter"><label for="vendor-filter">설비 업체 명</label>';
    html += '<select id="vendor-filter">';
    html += '<option value="">전체</option>';
    vendors.forEach(function (name) {
      html += '<option value="' + esc(name) + '"' + (state.vendorFilter === name ? " selected" : "") + ">" + esc(name) + "</option>";
    });
    html += "</select></div></div>";
    html += '<div class="tree-list">';
    const visibleProducts = (state.doc.products || []).filter(productVisible);
    if (!state.doc.products.length) {
      html += '<p class="tree-empty">제품을 추가하거나 샘플·엑셀을 불러오세요.</p>';
    } else if (!visibleProducts.length) {
      html += '<p class="tree-empty">선택한 설비 업체의 공정이 없습니다.</p>';
    }
    visibleProducts.forEach(function (product) {
      const productIds = (product.processes || []).filter(processVisible).reduce(function (ids, process) {
        return ids.concat(eventIdsOfProcess(process));
      }, []);
      const processes = (product.processes || []).filter(processVisible);
      const productCollapsed = isCollapsed("prd", product.id);
      html += '<div class="tree-product' + (s.product && s.product.id === product.id && !s.process ? " on" : "") + (productCollapsed ? " collapsed" : "") + '">';
      html += '<div class="tree-node-row" draggable="true" data-drag="product" data-product="' + product.id + '">';
      html += parentCheckHtml("check-product", productIds, 'data-product="' + product.id + '"');
      html += processes.length
        ? foldBtn("toggle-product", productCollapsed, 'data-product="' + product.id + '"')
        : '<span class="tree-fold-spacer"></span>';
      html += '<span class="drag-handle" title="드래그해서 순서 변경" aria-hidden="true"></span>';
      html += '<span class="tree-kind product">제품</span>';
      html += '<span class="tree-item product" data-act="sel-product" data-product="' + product.id + '">' + esc(product.name || "제품") + "</span>";
      html += '<button type="button" class="tree-mini" draggable="false" data-act="add-process" data-product="' + product.id + '">공정 +</button>';
      html += "</div>";
      html += '<div class="tree-children">';
      if (!processes.length) html += '<p class="tree-empty nested">공정이 없습니다. 공정 + 로 추가하세요.</p>';
      processes.forEach(function (process) {
        const processIds = eventIdsOfProcess(process);
        const events = process.events || [];
        const processCollapsed = isCollapsed("prc", process.id);
        html += '<div class="tree-process' + (s.process && s.process.id === process.id && !s.event ? " on" : "") + (processCollapsed ? " collapsed" : "") + '">';
        html += '<div class="tree-node-row" draggable="true" data-drag="process" data-product="' + product.id + '" data-process="' + process.id + '">';
        html += parentCheckHtml("check-process", processIds, 'data-product="' + product.id + '" data-process="' + process.id + '"');
        html += events.length
          ? foldBtn("toggle-process", processCollapsed, 'data-product="' + product.id + '" data-process="' + process.id + '"')
          : '<span class="tree-fold-spacer"></span>';
        html += '<span class="drag-handle" title="드래그해서 순서 변경" aria-hidden="true"></span>';
        html += '<span class="tree-kind process">공정</span>';
        html += '<span class="tree-item process" data-act="sel-process" data-product="' + product.id + '" data-process="' + process.id + '">' + esc(process.name || "공정") + (process.manual ? '<span class="badge-manual">매뉴얼</span>' : "") + "</span>";
        html += '<button type="button" class="tree-mini" draggable="false" data-act="add-event" data-product="' + product.id + '" data-process="' + process.id + '">이벤트 +</button>';
        html += "</div>";
        html += '<div class="tree-event-list">';
        if (!events.length) html += '<p class="tree-empty nested">이벤트가 없습니다. 아래 종류를 고른 뒤 이벤트 + 를 누르세요.</p>';
        events.forEach(function (event) {
          const t = M.findEventType(state.sectors, event.typeId);
          const label = t ? t.name : event.typeId;
          html += '<div class="tree-event-row" draggable="true" data-drag="event" data-product="' + product.id + '" data-process="' + process.id + '" data-event="' + event.id + '">';
          html += '<input type="checkbox" data-act="check-event" data-product="' + product.id + '" data-process="' + process.id + '" data-event="' + event.id + '"' + (state.checked[event.id] ? " checked" : "") + ">";
          html += '<span class="drag-handle" title="드래그해서 순서 변경" aria-hidden="true"></span>';
          html += '<span class="tree-kind event">이벤트</span>';
          html += '<span class="tree-item event' + (s.event && s.event.id === event.id ? " on" : "") + '" data-act="sel-event" data-product="' + product.id + '" data-process="' + process.id + '" data-event="' + event.id + '">' + esc(label) + "</span>";
          html += "</div>";
        });
        html += "</div></div>";
      });
      html += "</div></div>";
    });
    html += "</div>";
    html += '<div class="tree-sticky-foot"><div class="tree-add-event"><label for="new-event-type">추가할 이벤트</label><select id="new-event-type">';
    (state.sectors.events || []).forEach(function (ev) {
      const sel = (state.newEventTypeId || (state.sectors.events[0] && state.sectors.events[0].id)) === ev.id;
      html += '<option value="' + esc(ev.id) + '"' + (sel ? " selected" : "") + ">" + esc(ev.name) + "</option>";
    });
    html += '</select><p class="hint">공정 옆 이벤트 + 로 추가합니다. 이름을 드래그하면 순서가 바뀝니다.</p></div></div>';
    $("tree").innerHTML = html;
    const vendorSel = $("vendor-filter");
    if (vendorSel) {
      vendorSel.onchange = function () {
        state.vendorFilter = this.value;
        renderTree();
      };
    }
    const typeSel = $("new-event-type");
    if (typeSel) {
      typeSel.onchange = function () { state.newEventTypeId = this.value; };
    }
    applyParentChecks();
    restoreTreeScroll(savedScroll);
  }

  function eventIdsOfProcess(process) {
    return ((process && process.events) || []).map(function (event) { return event.id; });
  }

  function eventIdsOfProduct(product) {
    const ids = [];
    ((product && product.processes) || []).forEach(function (process) {
      eventIdsOfProcess(process).forEach(function (id) { ids.push(id); });
    });
    return ids;
  }

  function groupAllChecked(ids) {
    return ids.length > 0 && ids.every(function (id) { return state.checked[id]; });
  }

  function groupSomeChecked(ids) {
    return ids.some(function (id) { return state.checked[id]; });
  }

  function setGroupChecked(ids, on) {
    ids.forEach(function (id) { state.checked[id] = !!on; });
  }

  function parentCheckHtml(act, ids, attrs) {
    const all = groupAllChecked(ids);
    const some = groupSomeChecked(ids);
    return '<input type="checkbox" data-act="' + act + '" ' + attrs + (all ? " checked" : "") + (some && !all ? ' data-indeterminate="1"' : "") + ">";
  }

  function applyParentChecks() {
    $("tree").querySelectorAll("input[data-indeterminate]").forEach(function (el) {
      el.indeterminate = true;
    });
  }

  function selectedEventIds() {
    return Object.keys(state.checked).filter(function (id) { return state.checked[id]; });
  }

  function renderToc() {
    M.ensureTocOrder(state.doc);
    const entries = M.tocEntries(state.doc);
    let html = '<div class="editor-head"><h2>목차 순서</h2></div>';
    html += '<p class="hint">행을 드래그해서 목차·엑셀 시트 순서를 바꿉니다. 왼쪽 트리에서도 제품·공정·이벤트를 드래그할 수 있습니다.</p>';
    html += '<div class="toolbar"><button class="btn" type="button" id="toc-all">모두 선택</button><button class="btn" type="button" id="toc-none">선택 해제</button></div>';
    html += '<div class="table-wrap"><table class="grid toc-table"><thead><tr><th></th><th>순서</th><th>제품명</th><th>공정 명</th><th>이벤트</th><th></th></tr></thead><tbody>';
    entries.forEach(function (item, idx) {
      const t = M.findEventType(state.sectors, item.event.typeId);
      const label = t ? t.name : item.event.typeId;
      html += "<tr draggable=\"true\" data-drag-toc=\"" + item.event.id + "\">";
      html += '<td><input type="checkbox" data-toc-check="' + item.event.id + '"' + (state.checked[item.event.id] ? " checked" : "") + "></td>";
      html += "<td>" + (idx + 1) + "</td>";
      html += "<td>" + esc(item.product.name) + "</td>";
      html += "<td>" + esc(item.process.name) + (item.process.manual ? '<span class="badge-manual">매뉴얼</span>' : "") + "</td>";
      html += "<td>" + esc(label) + "</td>";
      html += "<td class=\"toc-move\">⋮⋮</td></tr>";
    });
    if (!entries.length) html += '<tr><td colspan="6">이벤트가 없습니다.</td></tr>';
    html += "</tbody></table></div>";
    $("editor").innerHTML = html;
    $("toc-all").onclick = function () {
      entries.forEach(function (item) { state.checked[item.event.id] = true; });
      render();
    };
    $("toc-none").onclick = function () {
      state.checked = {};
      render();
    };
    $("editor").onchange = function (e) {
      const t = e.target;
      if (t.dataset.tocCheck) {
        state.checked[t.dataset.tocCheck] = t.checked;
        persist();
        renderTree();
      }
    };
    bindTocDrag($("editor"));
  }

  function bindTocDrag(editor) {
    let fromId = "";
    let blockDrag = false;
    editor.onmousedown = function (e) {
      const el = eventEl(e);
      blockDrag = !!(el && el.closest("input, button"));
    };
    editor.ondragstart = function (e) {
      if (blockDrag) {
        e.preventDefault();
        return;
      }
      const el = eventEl(e);
      const tr = el && el.closest("[data-drag-toc]");
      if (!tr) return;
      fromId = tr.getAttribute("data-drag-toc");
      tr.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      try { e.dataTransfer.setData("text/plain", fromId); } catch (err) {}
    };
    editor.ondragover = function (e) {
      const el = eventEl(e);
      const tr = el && el.closest("[data-drag-toc]");
      if (!tr || !fromId) return;
      e.preventDefault();
      editor.querySelectorAll(".drag-over").forEach(function (node) { node.classList.remove("drag-over"); });
      tr.classList.add("drag-over");
    };
    editor.ondrop = function (e) {
      const el = eventEl(e);
      const tr = el && el.closest("[data-drag-toc]");
      if (!tr || !fromId) return;
      e.preventDefault();
      M.moveId(state.doc.tocOrder, fromId, tr.getAttribute("data-drag-toc"));
      fromId = "";
      persist();
      render();
    };
    editor.ondragend = function () {
      fromId = "";
      editor.querySelectorAll(".drag-over, .dragging").forEach(function (node) {
        node.classList.remove("drag-over");
        node.classList.remove("dragging");
      });
    };
  }

  function renderEmpty() {
    $("editor").innerHTML =
      '<div class="empty-card">' +
        "<h2>설비 메시지 정의서</h2>" +
        "<p>제품명 → 공정 명 → 이벤트 순으로 관리합니다. 이벤트 종류는 기준정보에서 공통으로 두고, 각 이벤트의 항목은 편집할 수 있습니다. JSON으로 저장하면 마지막 수정이 그대로 열립니다.</p>" +
        '<div class="toolbar">' +
          '<button class="btn btn-primary" type="button" id="boot-sample">CISCO V4 샘플 불러오기</button>' +
          '<button class="btn" type="button" id="boot-product">빈 제품 만들기</button>' +
        "</div>" +
      "</div>";
    $("boot-sample").onclick = loadSample;
    $("boot-product").onclick = function () {
      const p = M.addProduct(state.doc, "새 제품");
      persist();
      selectProduct(p.id);
    };
  }

  function inputRow(label, value, attrs) {
    return '<div class="row"><label>' + esc(label) + "</label><input type=\"text\" " + attrs + ' value="' + esc(value) + '"></div>';
  }

  function renderProduct(product) {
    $("editor").innerHTML =
      '<div class="editor-head"><h2>제품</h2><button class="btn btn-danger" type="button" id="del-product">삭제</button></div>' +
      inputRow("제품명", product.name, 'id="f-product-name"') +
      '<p class="hint">하위에 공정과 이벤트를 두면 엑셀 목차의 제품명 열이 됩니다.</p>';
    $("f-product-name").oninput = function () {
      product.name = this.value;
      persist();
      renderTree();
    };
    $("del-product").onclick = function () {
      if (!confirm("제품과 하위 공정·이벤트를 삭제할까요?")) return;
      M.removeById(state.doc.products, product.id);
      state.sel = { productId: "", processId: "", eventId: "" };
      persist();
      render();
    };
  }

  function renderProcess(product, process) {
    $("editor").innerHTML =
      '<div class="editor-head"><h2>공정</h2><button class="btn btn-danger" type="button" id="del-process">삭제</button></div>' +
      inputRow("공정 명", process.name, 'id="f-process-name"') +
      inputRow("설비 명", process.equipmentName || "-", 'id="f-eq"') +
      inputRow("설비 업체 명", process.vendorName || "", 'id="f-vendor"') +
      inputRow("시트 접두어", process.sheetPrefix || M.sheetPrefixOf(product, process), 'id="f-prefix"') +
      '<div class="row"><label>매뉴얼</label><label class="check-label"><input type="checkbox" id="f-manual"' + (process.manual ? " checked" : "") + "> 설비 통신 없이 매뉴얼로만 진행</label></div>" +
      '<p class="hint">체크하면 엑셀 목차의 <b>상세보기</b> 칸에 빨간색 매뉴얼이 표시됩니다. 시트 이름 예: ' + esc(M.sheetPrefixOf(product, process)) + "(STDTrackIn)</p>";
    $("f-process-name").oninput = function () { process.name = this.value; persist(); renderTree(); };
    $("f-eq").oninput = function () { process.equipmentName = this.value; persist(); };
    $("f-vendor").oninput = function () { process.vendorName = this.value; persist(); };
    $("f-vendor").onchange = function () { process.vendorName = this.value; persist(); renderTree(); };
    $("f-prefix").oninput = function () { process.sheetPrefix = this.value; persist(); };
    $("f-manual").onchange = function () {
      process.manual = this.checked;
      persist();
      renderTree();
    };
    $("del-process").onclick = function () {
      if (!confirm("공정과 하위 이벤트를 삭제할까요?")) return;
      M.removeById(product.processes, process.id);
      state.sel.processId = "";
      state.sel.eventId = "";
      persist();
      render();
    };
  }

  function emptyItem(extra) {
    return Object.assign({ name: "newItem", type: "String", description: "", detail: "", required: "", example: "" }, extra || {});
  }

  function fieldRowHtml(field, bind, delBtn) {
    let html = "<tr>";
    html += '<td><input ' + bind + ' data-k="name" value="' + esc(field.name || "") + '"></td>';
    html += '<td><input ' + bind + ' data-k="type" value="' + esc(field.type || "") + '" placeholder="String 또는 Type[]"></td>';
    html += '<td><input ' + bind + ' data-k="description" value="' + esc(field.description || "") + '"></td>';
    html += '<td><input ' + bind + ' data-k="detail" value="' + esc(field.detail || "") + '"></td>';
    html += '<td><input ' + bind + ' data-k="required" value="' + esc(field.required || "") + '"></td>';
    html += '<td><input ' + bind + ' data-k="example" value="' + esc(field.example || "") + '"></td>';
    html += "<td>" + (delBtn || "") + "</td></tr>";
    return html;
  }

  function renderFieldGrid(fields, bindFn, delFn) {
    let html = '<div class="table-wrap"><table class="grid"><thead><tr><th>이름</th><th>타입</th><th>설명</th><th>상세설명</th><th>필수</th><th>예시값</th><th></th></tr></thead><tbody>';
    (fields || []).forEach(function (field, idx) {
      html += fieldRowHtml(field, bindFn(idx), delFn(idx));
    });
    if (!(fields || []).length) html += '<tr><td colspan="7">항목이 없습니다. 추가하세요.</td></tr>';
    html += "</tbody></table></div>";
    return html;
  }

  function renderNestedBlocks(event, sector, fields) {
    let html = "";
    (fields || []).forEach(function (field) {
      const nid = M.nestedIdOf(field);
      if (!nid) return;
      M.syncFieldNested(event, state.sectors, sector.id, field);
      const inner = M.nestedFieldsOf(event, state.sectors, sector.id, nid);
      html += '<div class="nested-block">';
      html += '<div class="sector-head"><h4>' + esc(M.nestedTitleOf(state.sectors, nid));
      html += " <small>" + esc(field.name) + " · " + esc(field.type || nid) + "</small></h4>";
      html += '<button class="btn" type="button" data-add-nested="' + sector.id + '" data-nid="' + esc(nid) + '">항목 추가</button></div>';
      html += '<p class="hint">배열/객체 내부 스키마입니다. 이름·타입을 수정하고 항목을 추가·삭제할 수 있습니다. 타입을 <code>Type[]</code> 로 두면 그 아래 또 다른 배열 블록이 생깁니다.</p>';
      html += renderFieldGrid(inner, function (idx) {
        return 'data-n-sec="' + sector.id + '" data-nid="' + esc(nid) + '" data-i="' + idx + '"';
      }, function (idx) {
        return '<button class="btn btn-ghost" type="button" data-del-nested="' + sector.id + '" data-nid="' + esc(nid) + '" data-i="' + idx + '">삭제</button>';
      });
      html += renderNestedBlocks(event, sector, inner);
      html += "</div>";
    });
    return html;
  }

  function renderKv(event, sector, eventType) {
    let html = '<section class="sector"><h3>' + esc(sector.title) + "</h3>";
    (sector.fields || []).forEach(function (field) {
      const fallback = (eventType.defaults || {})[field.key] || "";
      const value = M.kvValue(event, sector.id, field.key, fallback);
      html += '<div class="row"><label>' + esc(field.label) + '</label><input data-kv-sec="' + sector.id + '" data-kv-key="' + field.key + '" value="' + esc(value) + '"></div>';
    });
    html += "</section>";
    return html;
  }

  function renderObject(event, sector) {
    const fields = M.fieldsOf(event, sector);
    M.snapshotNestedFromFields(event, state.sectors, sector.id, fields);
    let html = '<section class="sector"><div class="sector-head"><h3>' + esc(sector.title) + '</h3><div class="toolbar">';
    html += '<button class="btn" type="button" data-add-item="' + sector.id + '">항목 추가</button>';
    html += '<button class="btn" type="button" data-add-array="' + sector.id + '">배열 추가</button></div></div>';
    html += '<p class="hint">상위 항목입니다. 배열이면 타입을 <code>BulkConsumableList[]</code> 처럼 적거나 [배열 추가]를 누르면, 아래에 내부 항목 편집 블록이 생깁니다.</p>';
    html += renderFieldGrid(fields, function (idx) {
      return 'data-item-sec="' + sector.id + '" data-i="' + idx + '"';
    }, function (idx) {
      return '<button class="btn btn-ghost" type="button" data-del-item="' + sector.id + '" data-i="' + idx + '">삭제</button>';
    });
    html += renderNestedBlocks(event, sector, fields);
    html += "</section>";
    return html;
  }

  function renderRows(event, sector) {
    const rows = M.rowsOf(event, sector.id, sector);
    let html = '<section class="sector"><div class="sector-head"><h3>' + esc(sector.title) + '</h3><button class="btn" type="button" data-add-row="' + sector.id + '">행 추가</button></div>';
    html += '<div class="table-wrap"><table class="grid"><thead><tr>';
    (sector.columns || []).forEach(function (col) { html += "<th>" + esc(col.header) + "</th>"; });
    html += "<th></th></tr></thead><tbody>";
    rows.forEach(function (row, idx) {
      html += "<tr>";
      (sector.columns || []).forEach(function (col) {
        html += '<td><input data-row-sec="' + sector.id + '" data-row="' + idx + '" data-col="' + col.key + '" value="' + esc(row[col.key] == null ? "" : row[col.key]) + '"></td>';
      });
      html += '<td><button class="btn btn-ghost" type="button" data-del-row="' + sector.id + '" data-row="' + idx + '">삭제</button></td></tr>';
    });
    if (!rows.length) html += '<tr><td colspan="' + ((sector.columns || []).length + 1) + '">값이 없습니다. 행을 추가하세요.</td></tr>';
    html += "</tbody></table></div></section>";
    return html;
  }

  function renderExample(event, sector) {
    const built = M.buildExample(state.sectors, event, sector);
    const over = M.exampleOverride(event, sector.id);
    const req = over.request || built.request;
    const res = over.response || built.response;
    return '<section class="sector"><h3>' + esc(sector.title) + "</h3>" +
      '<p class="hint">예시 JSON은 섹터 값으로 자동 생성됩니다. 필요하면 직접 수정할 수 있습니다.</p>' +
      '<div class="grid-2">' +
        '<div><label>요청</label><textarea data-ex-sec="' + sector.id + '" data-ex-key="request">' + esc(req) + "</textarea></div>" +
        '<div><label>응답</label><textarea data-ex-sec="' + sector.id + '" data-ex-key="response">' + esc(res) + "</textarea></div>" +
      "</div>" +
      '<button class="btn" type="button" data-reset-ex="' + sector.id + '">자동 생성 값으로 되돌리기</button>' +
      "</section>";
  }

  function renderEvent(product, process, event) {
    const eventType = M.findEventType(state.sectors, event.typeId);
    const sheet = eventType ? M.sheetNameOf(product, process, eventType) : "";
    let html = '<div class="editor-head"><h2>' + esc(product.name) + " / " + esc(process.name) + " / " + esc(eventType ? eventType.name : event.typeId) + "</h2>";
    html += '<button class="btn btn-danger" type="button" id="del-event">삭제</button></div>';
    if (sheet) html += '<p class="hint">엑셀 시트: ' + esc(sheet) + "</p>";
    else html += '<p class="hint">이 이벤트는 목차에만 기록되고 상세 시트는 만들지 않습니다.</p>';
    if (eventType) {
      (eventType.sectors || []).forEach(function (sid) {
        const sector = M.sectorOf(state.sectors, sid);
        if (!sector) return;
        if (sector.kind === "kv") html += renderKv(event, sector, eventType);
        else if (sector.kind === "object") html += renderObject(event, sector);
        else if (sector.kind === "rows") html += renderRows(event, sector);
        else if (sector.kind === "example") html += renderExample(event, sector);
      });
    }
    $("editor").innerHTML = html;
    $("del-event").onclick = function () {
      if (!confirm("이 이벤트를 삭제할까요?")) return;
      M.removeById(process.events, event.id);
      state.sel.eventId = "";
      persist();
      render();
    };
    $("editor").oninput = onEditorInput;
    $("editor").onchange = onEditorChange;
    $("editor").onclick = onEditorClick;
  }

  function onEditorInput(e) {
    const t = e.target;
    const { event } = selected();
    if (!event) return;
    if (t.dataset.kvSec) M.setKvValue(event, t.dataset.kvSec, t.dataset.kvKey, t.value);
    if (t.dataset.nSec) {
      const fields = M.nestedFieldsOf(event, state.sectors, t.dataset.nSec, t.dataset.nid);
      const field = fields[Number(t.dataset.i)];
      if (field) {
        field[t.dataset.k] = t.value;
        if (t.dataset.k === "type") M.syncFieldNested(event, state.sectors, t.dataset.nSec, field);
      }
    } else if (t.dataset.itemSec) {
      const sector = M.sectorOf(state.sectors, t.dataset.itemSec);
      const fields = sector ? M.fieldsOf(event, sector) : [];
      const field = fields[Number(t.dataset.i)];
      if (field) {
        const key = t.dataset.k || t.dataset.key;
        field[key] = t.value;
        if (key === "type") M.syncFieldNested(event, state.sectors, t.dataset.itemSec, field);
        if (key !== "name" && key !== "type") M.setFieldValue(event, t.dataset.itemSec, field.name, key, t.value);
      }
    } else if (t.dataset.field) {
      M.setFieldValue(event, t.dataset.sec, t.dataset.field, t.dataset.key, t.value);
    }
    if (t.dataset.rowSec) {
      const sector = M.sectorOf(state.sectors, t.dataset.rowSec);
      const rows = M.rowsOf(event, t.dataset.rowSec, sector);
      const row = rows[Number(t.dataset.row)];
      if (row) row[t.dataset.col] = t.value;
    }
    if (t.dataset.exSec) M.setKvValue(event, t.dataset.exSec, t.dataset.exKey, t.value);
    persist();
  }

  function onEditorChange(e) {
    const t = e.target;
    if (!t.dataset || (t.dataset.k !== "type" && t.dataset.k !== "name")) return;
    persist();
    render();
  }

  function freshNestedId(event, sectorId, base) {
    const bag = (event.nestedItems && event.nestedItems[sectorId]) || {};
    let n = 1;
    let id = base;
    while (Object.prototype.hasOwnProperty.call(bag, id)) {
      n += 1;
      id = base + n;
    }
    return id;
  }

  function onEditorClick(e) {
    const btn = e.target.closest("[data-add-row],[data-del-row],[data-reset-ex],[data-add-item],[data-del-item],[data-add-array],[data-add-nested],[data-del-nested]");
    if (!btn) return;
    const { event } = selected();
    if (!event) return;
    if (btn.dataset.addRow) {
      const sector = M.sectorOf(state.sectors, btn.dataset.addRow);
      const row = {};
      (sector.columns || []).forEach(function (c) { row[c.key] = ""; });
      M.rowsOf(event, sector.id, sector).push(row);
    }
    if (btn.dataset.delRow) {
      const sector = M.sectorOf(state.sectors, btn.dataset.delRow);
      M.rowsOf(event, btn.dataset.delRow, sector).splice(Number(btn.dataset.row), 1);
    }
    if (btn.dataset.addItem) {
      const sector = M.sectorOf(state.sectors, btn.dataset.addItem);
      M.fieldsOf(event, sector).push(emptyItem());
    }
    if (btn.dataset.delItem) {
      const sector = M.sectorOf(state.sectors, btn.dataset.delItem);
      M.fieldsOf(event, sector).splice(Number(btn.dataset.i), 1);
    }
    if (btn.dataset.addArray) {
      const sector = M.sectorOf(state.sectors, btn.dataset.addArray);
      const nid = freshNestedId(event, sector.id, "NewList");
      M.fieldsOf(event, sector).push(emptyItem({ name: nid.charAt(0).toLowerCase() + nid.slice(1), type: nid + "[]", nested: nid, description: "" }));
      M.nestedFieldsOf(event, state.sectors, sector.id, nid).push(emptyItem({ name: "id", type: "String" }));
    }
    if (btn.dataset.addNested) {
      M.nestedFieldsOf(event, state.sectors, btn.dataset.addNested, btn.dataset.nid).push(emptyItem());
    }
    if (btn.dataset.delNested) {
      M.nestedFieldsOf(event, state.sectors, btn.dataset.delNested, btn.dataset.nid).splice(Number(btn.dataset.i), 1);
    }
    if (btn.dataset.resetEx) {
      if (event.values) delete event.values[btn.dataset.resetEx];
    }
    persist();
    render();
  }

  function uniqueEventTypeId(name) {
    const base = String(name || "").replace(/\s+/g, "").replace(/[^\w가-힣\-]/g, "") || "ev";
    let id = base;
    let n = 2;
    while ((state.sectors.events || []).some(function (ev) { return ev.id === id; })) {
      id = base + "_" + n;
      n += 1;
    }
    return id;
  }

  function renderMaster() {
    const events = state.sectors.events || [];
    if (!state.masterEventId && events[0]) state.masterEventId = events[0].id;
    const current = M.findEventType(state.sectors, state.masterEventId) || events[0];
    let html = '<div class="editor-head"><h2>이벤트 기준정보</h2>';
    if (current) html += '<button class="btn btn-danger" type="button" id="del-event-type">이 종류 삭제</button>';
    html += "</div>";
    html += '<p class="hint">이벤트 종류(STDTrackIn 등)는 기준정보로 공통 관리합니다. 이름을 직접 넣고 추가·수정·삭제할 수 있습니다. 요청/응답 필드 기본값은 여기서 고치고, 각 제품·공정 이벤트 화면에서 다시 편집할 수 있습니다.</p>';
    html += '<div class="row"><label>새 이벤트</label><div class="inline-add"><input id="new-master-event-name" placeholder="이름 (예: STDTrackIn)"><button class="btn btn-primary" type="button" id="add-event-type">종류 추가</button></div></div>';
    html += '<div class="row"><label>이벤트 종류</label><select id="master-event">';
    events.forEach(function (ev) {
      html += '<option value="' + esc(ev.id) + '"' + (current && current.id === ev.id ? " selected" : "") + ">" + esc(ev.name) + "</option>";
    });
    html += "</select></div>";
    if (current) {
      html += inputRow("이름", current.name || "", 'id="master-event-name"');
      html += inputRow("ID", current.id || "", 'id="master-event-id"');
      html += '<div class="row"><label>시트 생성</label><label class="check-label"><input type="checkbox" id="master-gen-sheet"' + (current.generateSheet ? " checked" : "") + "> 엑셀 상세 시트 생성</label></div>";
      html += '<div class="stats"><span class="stat">시트 생성<b>' + (current.generateSheet ? "예" : "아니오") + "</b></span>";
      html += '<span class="stat">섹터<b>' + (current.sectors || []).length + "</b></span></div>";
      (current.sectors || []).forEach(function (sid) {
        const sector = M.sectorOf(state.sectors, sid);
        if (!sector) return;
        html += '<section class="sector"><h3>' + esc(sector.title) + ' <small>' + esc(sector.kind) + "</small></h3>";
        if (sector.kind === "object") {
          html += '<div class="table-wrap"><table class="grid"><thead><tr><th>이름</th><th>타입</th><th>설명</th><th>상세설명</th><th>예시값</th><th></th></tr></thead><tbody>';
          (sector.fields || []).forEach(function (f, i) {
            html += "<tr>";
            html += '<td><input data-mf="' + sid + '" data-i="' + i + '" data-k="name" value="' + esc(f.name) + '"></td>';
            html += '<td><input data-mf="' + sid + '" data-i="' + i + '" data-k="type" value="' + esc(f.type || "") + '"></td>';
            html += '<td><input data-mf="' + sid + '" data-i="' + i + '" data-k="description" value="' + esc(f.description || "") + '"></td>';
            html += '<td><input data-mf="' + sid + '" data-i="' + i + '" data-k="detail" value="' + esc(f.detail || "") + '"></td>';
            html += '<td><input data-mf="' + sid + '" data-i="' + i + '" data-k="example" value="' + esc(f.example || "") + '"></td>';
            html += '<td><button class="btn btn-ghost" type="button" data-del-field="' + sid + '" data-i="' + i + '">삭제</button></td></tr>';
          });
          html += '</tbody></table></div><button class="btn" type="button" data-add-field="' + sid + '">필드 추가</button>';
        } else if (sector.kind === "rows") {
          if (!Array.isArray(sector.defaultRows)) sector.defaultRows = [];
          html += '<div class="sector-head"><p>기본 항목</p><button class="btn" type="button" data-add-def-row="' + sid + '">항목 추가</button></div>';
          html += '<div class="table-wrap"><table class="grid"><thead><tr>';
          (sector.columns || []).forEach(function (col) { html += "<th>" + esc(col.header) + "</th>"; });
          html += "<th></th></tr></thead><tbody>";
          sector.defaultRows.forEach(function (row, idx) {
            html += "<tr>";
            (sector.columns || []).forEach(function (col) {
              html += '<td><input data-def-row="' + sid + '" data-i="' + idx + '" data-k="' + col.key + '" value="' + esc(row[col.key] == null ? "" : row[col.key]) + '"></td>';
            });
            html += '<td><button class="btn btn-ghost" type="button" data-del-def-row="' + sid + '" data-i="' + idx + '">삭제</button></td></tr>';
          });
          if (!sector.defaultRows.length) {
            html += '<tr><td colspan="' + ((sector.columns || []).length + 1) + '">기본 항목이 없습니다.</td></tr>';
          }
          html += "</tbody></table></div>";
        } else if (sector.kind === "kv") {
          html += "<p>항목: " + esc((sector.fields || []).map(function (f) { return f.label; }).join(", ")) + "</p>";
        } else {
          html += "<p>예시 JSON 섹터입니다.</p>";
        }
        html += "</section>";
      });
    }
    html += '<section class="sector"><div class="sector-head"><h3>배열/객체 정의</h3><button class="btn" type="button" id="add-nested-type">정의 추가</button></div>';
    html += '<p class="hint">BulkConsumableList, ITEM, DATA처럼 배열·객체 내부 항목의 기준정보입니다. 이벤트 화면에서 배열을 추가하면 이 정의를 기본값으로 복사한 뒤, 해당 이벤트에서 다시 편집합니다.</p>';
    if (!state.sectors.nested) state.sectors.nested = {};
    Object.keys(state.sectors.nested).forEach(function (nid) {
      const def = state.sectors.nested[nid];
      if (!Array.isArray(def.fields)) def.fields = [];
      html += '<div class="nested-block"><div class="sector-head"><h4>' + esc(def.title || nid) + " <small>" + esc(nid) + "</small></h4>";
      html += '<button class="btn btn-ghost" type="button" data-del-ntype="' + esc(nid) + '">정의 삭제</button></div>';
      html += '<div class="row"><label>표시 이름</label><input data-nt="' + esc(nid) + '" data-nk="title" value="' + esc(def.title || nid) + '"></div>';
      html += '<div class="table-wrap"><table class="grid"><thead><tr><th>이름</th><th>타입</th><th>설명</th><th>상세설명</th><th>예시값</th><th></th></tr></thead><tbody>';
      def.fields.forEach(function (f, i) {
        html += "<tr>";
        html += '<td><input data-nf="' + esc(nid) + '" data-i="' + i + '" data-k="name" value="' + esc(f.name || "") + '"></td>';
        html += '<td><input data-nf="' + esc(nid) + '" data-i="' + i + '" data-k="type" value="' + esc(f.type || "") + '"></td>';
        html += '<td><input data-nf="' + esc(nid) + '" data-i="' + i + '" data-k="description" value="' + esc(f.description || "") + '"></td>';
        html += '<td><input data-nf="' + esc(nid) + '" data-i="' + i + '" data-k="detail" value="' + esc(f.detail || "") + '"></td>';
        html += '<td><input data-nf="' + esc(nid) + '" data-i="' + i + '" data-k="example" value="' + esc(f.example || "") + '"></td>';
        html += '<td><button class="btn btn-ghost" type="button" data-del-nfield="' + esc(nid) + '" data-i="' + i + '">삭제</button></td></tr>';
      });
      if (!def.fields.length) html += '<tr><td colspan="6">필드가 없습니다.</td></tr>';
      html += '</tbody></table></div><button class="btn" type="button" data-add-nfield="' + esc(nid) + '">필드 추가</button></div>';
    });
    html += "</section>";
    html += '<section class="sector"><h3>기준정보 JSON</h3><textarea id="master-json" class="json">' + esc(JSON.stringify(state.sectors, null, 2)) + "</textarea>";
    html += '<div class="toolbar"><button class="btn btn-primary" type="button" id="apply-json">JSON 적용</button>';
    html += '<button class="btn" type="button" id="reset-sectors">기본 기준정보로 복원</button>';
    html += '<button class="btn" type="button" id="dl-sectors">기준정보 저장</button>';
    html += '<label class="btn file-btn">기준정보 열기<input type="file" id="open-sectors" accept="application/json"></label></div></section>';
    $("editor").innerHTML = html;
    const masterSel = $("master-event");
    if (masterSel) masterSel.onchange = function () { state.masterEventId = this.value; render(); };
    $("add-event-type").onclick = function () {
      const name = (($("new-master-event-name") && $("new-master-event-name").value) || "").trim();
      if (!name) {
        flash("추가할 이벤트 이름을 입력하세요.", "err");
        if ($("new-master-event-name")) $("new-master-event-name").focus();
        return;
      }
      if (!state.sectors.events) state.sectors.events = [];
      const id = uniqueEventTypeId(name);
      state.sectors.events.push({
        id: id,
        name: name,
        generateSheet: false,
        sheetKind: "none",
        sectors: []
      });
      state.masterEventId = id;
      persist();
      flash("이벤트 종류를 추가했습니다.", "ok");
      render();
    };
    const newName = $("new-master-event-name");
    if (newName) {
      newName.onkeydown = function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          $("add-event-type").click();
        }
      };
    }
    if (current) {
      const nameEl = $("master-event-name");
      if (nameEl) {
        nameEl.oninput = function () {
          current.name = this.value;
          persist();
          if (masterSel && masterSel.selectedOptions[0]) masterSel.selectedOptions[0].textContent = this.value || current.id;
          renderTree();
        };
      }
      const idEl = $("master-event-id");
      if (idEl) {
        idEl.onchange = function () {
          const next = this.value.trim();
          if (!next) { this.value = current.id; return; }
          if (next === current.id) return;
          if ((state.sectors.events || []).some(function (ev) { return ev.id === next; })) {
            flash("이미 있는 ID입니다.", "err");
            this.value = current.id;
            return;
          }
          M.renameEventTypeId(state.doc, state.sectors, current.id, next);
          state.masterEventId = next;
          persist();
          render();
        };
      }
      const genEl = $("master-gen-sheet");
      if (genEl) {
        genEl.onchange = function () {
          current.generateSheet = this.checked;
          current.sheetKind = this.checked ? (current.sheetKind === "none" ? "api" : current.sheetKind) : "none";
          persist();
        };
      }
      const delType = $("del-event-type");
      if (delType) {
        delType.onclick = function () {
          const used = M.countEventTypeUsage(state.doc, current.id);
          const msg = used
            ? "이 종류를 쓰는 이벤트가 " + used + "개 있습니다. 종류만 삭제하고 기존 이벤트는 남겨둘까요?"
            : "이 이벤트 종류를 삭제할까요?";
          if (!confirm(msg)) return;
          M.removeEventType(state.sectors, current.id);
          state.masterEventId = (state.sectors.events[0] && state.sectors.events[0].id) || "";
          persist();
          flash("이벤트 종류를 삭제했습니다.", "ok");
          render();
        };
      }
    }
    $("add-nested-type").onclick = function () {
      if (!state.sectors.nested) state.sectors.nested = {};
      let id = "NewType";
      let n = 2;
      while (state.sectors.nested[id]) { id = "NewType" + n; n += 1; }
      state.sectors.nested[id] = {
        title: id,
        columns: ["name", "type", "description", "detail"],
        fields: [{ name: "id", type: "String", description: "", detail: "", example: "" }]
      };
      persist();
      render();
    };
    $("editor").oninput = function (e) {
      const t = e.target;
      if (t.dataset.mf) {
        const sector = M.sectorOf(state.sectors, t.dataset.mf);
        const field = sector && sector.fields[Number(t.dataset.i)];
        if (!field) return;
        field[t.dataset.k] = t.value;
        persist();
      }
      if (t.dataset.defRow) {
        const sector = M.sectorOf(state.sectors, t.dataset.defRow);
        const row = sector && (sector.defaultRows || [])[Number(t.dataset.i)];
        if (!row) return;
        row[t.dataset.k] = t.value;
        persist();
      }
      if (t.dataset.nt) {
        const def = state.sectors.nested[t.dataset.nt];
        if (def) { def[t.dataset.nk] = t.value; persist(); }
      }
      if (t.dataset.nf) {
        const def = state.sectors.nested[t.dataset.nf];
        const field = def && def.fields[Number(t.dataset.i)];
        if (field) { field[t.dataset.k] = t.value; persist(); }
      }
    };
    $("editor").onclick = function (e) {
      const add = e.target.closest("[data-add-field]");
      const del = e.target.closest("[data-del-field]");
      const addRow = e.target.closest("[data-add-def-row]");
      const delRow = e.target.closest("[data-del-def-row]");
      const addNf = e.target.closest("[data-add-nfield]");
      const delNf = e.target.closest("[data-del-nfield]");
      const delNt = e.target.closest("[data-del-ntype]");
      if (add) {
        const sector = M.sectorOf(state.sectors, add.dataset.addField);
        sector.fields.push({ name: "newField", type: "String", description: "", detail: "", example: "" });
        persist();
        render();
      }
      if (del) {
        const sector = M.sectorOf(state.sectors, del.dataset.delField);
        sector.fields.splice(Number(del.dataset.i), 1);
        persist();
        render();
      }
      if (addRow) {
        const sector = M.sectorOf(state.sectors, addRow.dataset.addDefRow);
        if (!Array.isArray(sector.defaultRows)) sector.defaultRows = [];
        const row = {};
        (sector.columns || []).forEach(function (c) { row[c.key] = ""; });
        sector.defaultRows.push(row);
        persist();
        render();
      }
      if (delRow) {
        const sector = M.sectorOf(state.sectors, delRow.dataset.delDefRow);
        (sector.defaultRows || []).splice(Number(delRow.dataset.i), 1);
        persist();
        render();
      }
      if (addNf) {
        const def = state.sectors.nested[addNf.dataset.addNfield];
        if (def) {
          def.fields.push({ name: "newField", type: "String", description: "", detail: "", example: "" });
          persist();
          render();
        }
      }
      if (delNf) {
        const def = state.sectors.nested[delNf.dataset.delNfield];
        if (def) {
          def.fields.splice(Number(delNf.dataset.i), 1);
          persist();
          render();
        }
      }
      if (delNt) {
        delete state.sectors.nested[delNt.dataset.delNtype];
        persist();
        render();
      }
    };
    $("apply-json").onclick = function () {
      try {
        const parsed = JSON.parse($("master-json").value);
        if (!parsed.events || !parsed.sectors) throw new Error("events, sectors 가 필요합니다.");
        state.sectors = parsed;
        persist();
        flash("기준정보를 적용했습니다.", "ok");
        render();
      } catch (err) {
        flash(err.message, "err");
      }
    };
    $("reset-sectors").onclick = function () {
      if (!confirm("기준정보를 기본값으로 되돌릴까요?")) return;
      state.sectors = M.defaultSectors();
      persist();
      flash("기본 기준정보로 복원했습니다.", "ok");
      render();
    };
    $("dl-sectors").onclick = function () {
      downloadText("message-sectors.json", JSON.stringify(state.sectors, null, 2));
    };
    $("open-sectors").onchange = function () {
      readFile(this.files[0], function (text) {
        state.sectors = JSON.parse(text);
        persist();
        flash("기준정보를 불러왔습니다.", "ok");
        render();
      });
    };
  }

  function renderEditor() {
    ensureSelection();
    if (state.tab === "master") {
      renderMaster();
      return;
    }
    if (state.tab === "toc") {
      renderToc();
      return;
    }
    const s = selected();
    if (s.event) renderEvent(s.product, s.process, s.event);
    else if (s.process) renderProcess(s.product, s.process);
    else if (s.product) renderProduct(s.product);
    else renderEmpty();
  }

  function downloadText(filename, text) {
    const blob = new Blob([text], { type: "application/json;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 800);
  }

  function readFile(file, cb) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function () { cb(reader.result); };
    reader.readAsText(file, "utf-8");
  }

  function loadSample() {
    state.doc = M.clone(global.MSG_SAMPLE_DOC);
    M.materializeDoc(state.doc, state.sectors);
    persist();
    state.tab = "edit";
    if (state.doc.products[0]) selectProduct(state.doc.products[0].id);
    else render();
    flash("CISCO V4 샘플을 불러왔습니다.", "ok");
  }

  function bindToolbar() {
    $("btn-xlsx-out").onclick = async function () {
      try {
        const name = await MsgExcel.exportXlsx(state.doc, state.sectors);
        flash(name + " 파일을 만들었습니다.", "ok");
      } catch (err) {
        flash(err.message || String(err), "err");
      }
    };
    $("btn-xlsx-sel").onclick = async function () {
      let ids = selectedEventIds();
      if (!ids.length && state.sel.eventId) ids = [state.sel.eventId];
      if (!ids.length) {
        flash("엑셀로 만들 이벤트를 왼쪽에서 체크하거나 선택하세요.", "err");
        return;
      }
      try {
        const name = await MsgExcel.exportXlsx(state.doc, state.sectors, ids);
        flash("선택한 " + ids.length + "건으로 " + name + " 파일을 만들었습니다.", "ok");
      } catch (err) {
        flash(err.message || String(err), "err");
      }
    };
    $("file-xlsx-in").onchange = async function () {
      const file = this.files[0];
      this.value = "";
      if (!file) return;
      try {
        const buf = await file.arrayBuffer();
        state.doc = await MsgExcel.importXlsx(buf, state.sectors);
        persist();
        state.tab = "edit";
        state.sel = { productId: state.doc.products[0] ? state.doc.products[0].id : "", processId: "", eventId: "" };
        render();
        flash("엑셀을 불러왔습니다.", "ok");
      } catch (err) {
        flash(err.message || String(err), "err");
      }
    };
    $("btn-json-out").onclick = function () {
      const reissued = M.uniquifyDocIds(state.doc);
      persist();
      downloadText("message-definition.json", JSON.stringify(M.toBundle(state.doc, state.sectors), null, 2));
      flash(
        reissued
          ? "정의서 JSON을 저장했습니다. 겹치던 ID " + reissued + "개를 새로 발번했습니다."
          : "정의서 JSON을 저장했습니다. 이벤트 기준정보와 항목 수정이 함께 들어갑니다.",
        "ok"
      );
      if (reissued) render();
    };
    $("file-json-in").onchange = function () {
      readFile(this.files[0], function (text) {
        try {
          const loaded = M.fromBundle(JSON.parse(text), state.sectors);
          state.doc = loaded.doc;
          if (loaded.sectors) state.sectors = loaded.sectors;
          persist();
          state.tab = "edit";
          state.sel = { productId: state.doc.products[0] ? state.doc.products[0].id : "", processId: "", eventId: "" };
          render();
          flash(
            loaded.reissued
              ? "JSON을 열었습니다. 겹치던 ID " + loaded.reissued + "개를 새로 발번했습니다. 다시 저장하면 새 ID가 들어갑니다."
              : "JSON을 열었습니다. 마지막 항목 수정이 그대로 표시됩니다.",
            "ok"
          );
        } catch (err) {
          flash(err.message, "err");
        }
      });
      this.value = "";
    };
    $("btn-sample").onclick = loadSample;
    $("btn-toc").onclick = function () {
      state.tab = state.tab === "toc" ? "edit" : "toc";
      render();
    };
    $("btn-master").onclick = function () {
      state.tab = state.tab === "master" ? "edit" : "master";
      render();
    };
    $("btn-clear").onclick = function () {
      if (!confirm("작업 중인 정의서를 비울까요? 기준정보는 유지됩니다.")) return;
      state.doc = M.emptyDoc();
      state.sel = { productId: "", processId: "", eventId: "" };
      persist();
      render();
    };
  }

  let lastRenderedSel = "";

  function render() {
    const editor = $("editor");
    const editorY = editor ? editor.scrollTop : 0;
    const winY = window.pageYOffset || document.documentElement.scrollTop || 0;
    const selKey = state.sel.productId + "/" + state.sel.processId + "/" + state.sel.eventId + "/" + state.tab;
    const keepEditor = lastRenderedSel === selKey;
    renderTree();
    renderEditor();
    lastRenderedSel = selKey;
    function restore() {
      if (keepEditor && $("editor")) $("editor").scrollTop = editorY;
      window.scrollTo(0, winY);
    }
    restore();
    requestAnimationFrame(restore);
    $("btn-master").textContent = state.tab === "master" ? "편집으로" : "기준정보";
    $("btn-toc").textContent = state.tab === "toc" ? "편집으로" : "목차 순서";
    if (state.msg) {
      $("app-msg").className = "msg " + state.msgType;
      $("app-msg").textContent = state.msg;
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    M.materializeDoc(state.doc, state.sectors);
    persist();
    bindToolbar();
    bindTree();
    render();
  });
})(window);
