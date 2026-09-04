/**
 * 메뉴 = 폴더 구조.
 * 새 화면을 추가하려면:
 *  1) 해당 폴더에 HTML 파일을 넣는다
 *  2) 아래에 같은 경로로 항목을 추가한다
 *
 * children 안에 { folder, children } 을 넣으면 하위 폴더가 된다.
 */
window.APP_MENU = [
  {
    folder: "홈",
    children: [
      { name: "대시보드", file: "dashboard.html", desc: "도구 모음 한눈에 보기" }
    ]
  },
  {
    folder: "개발도구",
    children: [
      { name: "JSON 포맷터", file: "json.html", desc: "JSON 정리 · 압축 · 검증" },
      { name: "Base64 변환", file: "base64.html", desc: "문자열 인코딩 / 디코딩" },
      { name: "URL 인코딩", file: "url.html", desc: "URL 인코딩 / 디코딩" },
      { name: "SQL 정리", file: "sql.html", desc: "공백 · 보이지 않는 문자 제거" },
      { name: "타임스탬프", file: "timestamp.html", desc: "Unix ↔ 날짜 변환" },
      { name: "정규식 테스트", file: "regex.html", desc: "정규식 매칭 확인" }
    ]
  },
  {
    folder: "텍스트도구",
    children: [
      { name: "글자수", file: "counter.html", desc: "글자 · 단어 · 줄 수 세기" },
      { name: "텍스트 비교", file: "diff.html", desc: "두 텍스트 줄 단위 비교" },
      { name: "줄 정렬", file: "sort.html", desc: "정렬 · 중복 제거 · 뒤집기" }
    ]
  },
  {
    folder: "업무계산",
    children: [
      { name: "숫자 합계", file: "sum.html", desc: "텍스트에서 숫자를 뽑아 합산" },
      { name: "날짜 계산", file: "date.html", desc: "기간 · D-day · 날짜 더하기" }
    ]
  },
  {
    folder: "개발산출물",
    children: [
      {
        folder: "설계",
        children: [
          {
            folder: "설비시나리오",
            children: [
              {
                folder: "메시지초안",
                children: [
                  { name: "설비 메시지 정의서", file: "index.html", desc: "제품·공정·이벤트 기준 메시지 관리 · 엑셀 생성" }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
];

window.APP_HOME = "홈/dashboard.html";

window.eachMenuPage = function (cb, nodes, prefix) {
  (nodes || window.APP_MENU).forEach(function (group) {
    const folderPath = prefix ? prefix + "/" + group.folder : group.folder;
    (group.children || []).forEach(function (child) {
      if (child.children) {
        window.eachMenuPage(cb, [child], folderPath);
      } else {
        cb(folderPath, child, folderPath + "/" + child.file);
      }
    });
  });
};
