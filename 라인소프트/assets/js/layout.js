(function () {
  const page = document.querySelector(".page");
  if (!page || !window.APP_MENU) return;

  const root = rootPrefix();
  const current = currentPath();

  const shell = document.createElement("div");
  shell.className = "shell";
  shell.innerHTML =
    '<aside class="sidebar">' +
      '<a class="brand" href="' + hrefOf(window.APP_HOME) + '">' +
        '<div class="brand-mark">LS</div>' +
        '<div class="brand-text"><strong>라인소프트</strong><span>업무 유틸</span></div>' +
      "</a>" +
      '<nav id="nav" class="nav" aria-label="폴더 메뉴"></nav>' +
    "</aside>" +
    '<div class="workspace">' +
      '<header class="topbar">' +
        '<div id="crumb" class="crumb"></div>' +
        '<div id="path" class="path"></div>' +
      "</header>" +
      '<main class="content"></main>' +
    "</div>";

  document.body.prepend(shell);
  shell.querySelector(".content").appendChild(page);

  const navEl = shell.querySelector("#nav");
  const crumbEl = shell.querySelector("#crumb");
  const pathEl = shell.querySelector("#path");
  const found = findEntry(current);

  pathEl.textContent = found ? found.path : current;

  if (found) {
    crumbEl.innerHTML =
      "<span>" + found.folder + '</span><span class="sep">/</span><b>' + found.item.name + "</b>";
    document.title = found.item.name + " · 라인소프트 업무 유틸";
  } else {
    crumbEl.innerHTML = "<b>" + document.title + "</b>";
  }

  window.APP_MENU.forEach(function (group) {
    navEl.appendChild(renderGroup(group, "", 0));
  });

  function renderGroup(group, parentPath, depth) {
    const folderPath = parentPath ? parentPath + "/" + group.folder : group.folder;
    const wrap = document.createElement("div");
    wrap.className = "folder" + (depth ? " nested" : "");
    if (!pathStartsWith(folderPath)) wrap.classList.add("collapsed");

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "folder-btn";
    btn.style.paddingLeft = 10 + depth * 10 + "px";
    btn.innerHTML =
      "<span>" + group.folder + "</span>" +
      '<svg class="chev" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
    btn.addEventListener("click", function () {
      wrap.classList.toggle("collapsed");
    });

    const list = document.createElement("div");
    list.className = "folder-items";

    (group.children || []).forEach(function (child) {
      if (child.children) {
        list.appendChild(renderGroup(child, folderPath, depth + 1));
        return;
      }
      const rel = folderPath + "/" + child.file;
      const a = document.createElement("a");
      a.className = "nav-item" + (rel === (found && found.path) ? " active" : "");
      a.style.paddingLeft = 18 + depth * 10 + "px";
      a.href = hrefOf(rel);
      a.textContent = child.name;
      list.appendChild(a);
    });

    wrap.appendChild(btn);
    wrap.appendChild(list);
    return wrap;
  }

  function rootPrefix() {
    const el = document.querySelector('script[src*="assets/js/menu.js"]');
    if (!el) return "../";
    return (el.getAttribute("src") || "").replace(/assets\/js\/menu\.js$/, "");
  }

  function hrefOf(rel) {
    return root + rel;
  }

  function currentPath() {
    return decodeURIComponent((location.pathname || "").replace(/\\/g, "/"));
  }

  function pathStartsWith(folderPath) {
    const needle = "/" + folderPath + "/";
    return current.indexOf(needle) !== -1 || current.endsWith("/" + folderPath);
  }

  function findEntry(pathname) {
    let match = null;
    window.eachMenuPage(function (folder, item, path) {
      if (pathname.endsWith("/" + path) || pathname.endsWith(path)) {
        match = { folder: folder, item: item, path: path };
      }
    });
    return match;
  }
})();
