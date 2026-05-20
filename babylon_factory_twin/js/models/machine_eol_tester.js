window.buildEolTesterModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 외관 (화이트/아주 밝은 회색)
  const whiteMat = new BABYLON.StandardMaterial("whiteMat", scene);
  whiteMat.diffuseColor = new BABYLON.Color3(0.93, 0.93, 0.95);

  // 금속 타공판 및 손잡이 (은색)
  const metalMat = new BABYLON.StandardMaterial("metalMat", scene);
  metalMat.diffuseColor = new BABYLON.Color3(0.65, 0.65, 0.7);
  metalMat.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);

  // 중앙 챔버 내부 및 기구물 (검은색)
  const darkMat = new BABYLON.StandardMaterial("darkMat", scene);
  darkMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.1);

  // 지그(Jig)의 포인트 컬러 (금색/황동색)
  const goldMat = new BABYLON.StandardMaterial("goldMat", scene);
  goldMat.diffuseColor = new BABYLON.Color3(0.8, 0.6, 0.1);

  // 공압 튜브 (파란색)
  const blueTubeMat = new BABYLON.StandardMaterial("blueTubeMat", scene);
  blueTubeMat.diffuseColor = new BABYLON.Color3(0.2, 0.5, 0.9);

  // 모니터 화면 (빛나는 UI)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.8, 0.9, 1.0); // 밝은 화면

  // 챔버 후면 해상력 테스트 차트 백라이트 (자체 발광 화이트)
  const chartBacklightMat = new BABYLON.StandardMaterial("chartBacklightMat", scene);
  chartBacklightMat.diffuseColor = new BABYLON.Color3(1, 1, 1);
  chartBacklightMat.emissiveColor = new BABYLON.Color3(0.9, 0.9, 0.9); // 눈부시게 빛남

  const blackMat = new BABYLON.StandardMaterial("blackMat", scene);
  blackMat.diffuseColor = new BABYLON.Color3(0, 0, 0);

  // 전체 모델을 그룹화할 TransformNode
  const frame = new BABYLON.TransformNode("eolTesterFrame", scene);
  frame.parent = machineMesh;

  const frameWidth = 14;
  const frameDepth = 6;
  const baseHeight = 5;

  // 2. 하부 캐비닛 및 테이블 (Lower Cabinet & Table)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameWidth, height: baseHeight, depth: frameDepth - 1}, scene);
  baseCabinet.position.y = baseHeight / 2;
  baseCabinet.position.z = d * 0.05;
  baseCabinet.material = whiteMat;
  baseCabinet.parent = frame;

  // 전면 캐비닛 손잡이 (검은색 매립형 느낌)
  const handle1 = BABYLON.MeshBuilder.CreateBox("handle1", {width: w * 0.03, height: h * 0.12, depth: d * 0.01}, scene);
  handle1.position = new BABYLON.Vector3(-2, baseHeight / 2, -2.55);
  handle1.material = darkMat;
  handle1.parent = frame;

  const handle2 = BABYLON.MeshBuilder.CreateBox("handle2", {width: w * 0.03, height: h * 0.12, depth: d * 0.01}, scene);
  handle2.position = new BABYLON.Vector3(2, baseHeight / 2, -2.55);
  handle2.material = darkMat;
  handle2.parent = frame;

  // 테이블 상판 (Table Top)
  const tableTop = BABYLON.MeshBuilder.CreateBox("tableTop", {width: frameWidth, height: h * 0.03, depth: frameDepth + 0.5}, scene);
  tableTop.position.y = baseHeight + 0.15;
  tableTop.position.z = d * -0.025; // 앞으로 돌출
  tableTop.material = whiteMat;
  tableTop.parent = frame;

  // 좌/우측 금속 타공판 작업대 (Perforated Plates)
  const leftPlate = BABYLON.MeshBuilder.CreateBox("leftPlate", {width: w * 0.35, height: h * 0.01, depth: d * 0.25}, scene);
  leftPlate.position = new BABYLON.Vector3(-4.5, baseHeight + 0.35, -1.5);
  leftPlate.material = metalMat;
  leftPlate.parent = frame;

  const rightPlate = BABYLON.MeshBuilder.CreateBox("rightPlate", {width: w * 0.35, height: h * 0.01, depth: d * 0.25}, scene);
  rightPlate.position = new BABYLON.Vector3(4.5, baseHeight + 0.35, -1.5);
  rightPlate.material = metalMat;
  rightPlate.parent = frame;

  // 중앙 돌출 키보드 트레이
  const kbTray = BABYLON.MeshBuilder.CreateBox("kbTray", {width: w * 0.45, height: h * 0.02, depth: d * 0.15}, scene);
  kbTray.position = new BABYLON.Vector3(0, baseHeight - 0.5, -3.2);
  kbTray.material = whiteMat;
  kbTray.parent = frame;

  const keyboard = BABYLON.MeshBuilder.CreateBox("keyboard", {width: w * 0.35, height: h * 0.01, depth: d * 0.12}, scene);
  keyboard.position = new BABYLON.Vector3(0, baseHeight - 0.35, -3.2);
  keyboard.material = darkMat;
  keyboard.parent = frame;

  // 3. 상부 프레임 및 모니터 (Upper Frame & Monitors)
  // 좌/우측 기둥 (Pillars)
  const leftPillar = BABYLON.MeshBuilder.CreateBox("leftPillar", {width: w * 0.35, height: h * 0.8, depth: d * 0.3}, scene);
  leftPillar.position = new BABYLON.Vector3(-5.25, baseHeight + 4.3, 1.5);
  leftPillar.material = whiteMat;
  leftPillar.parent = frame;

  const rightPillar = BABYLON.MeshBuilder.CreateBox("rightPillar", {width: w * 0.35, height: h * 0.8, depth: d * 0.3}, scene);
  rightPillar.position = new BABYLON.Vector3(5.25, baseHeight + 4.3, 1.5);
  rightPillar.material = whiteMat;
  rightPillar.parent = frame;

  // 상단 연결부
  const topBridge = BABYLON.MeshBuilder.CreateBox("topBridge", {width: w * 0.7, height: h * 0.1, depth: d * 0.3}, scene);
  topBridge.position = new BABYLON.Vector3(0, baseHeight + 7.8, 1.5);
  topBridge.material = whiteMat;
  topBridge.parent = frame;

  // 좌측 대형 모니터
  const leftMonitor = BABYLON.MeshBuilder.CreateBox("leftMonitor", {width: w * 0.45, height: h * 0.3, depth: d * 0.02}, scene);
  leftMonitor.position = new BABYLON.Vector3(-3.5, baseHeight + 6, -0.2);
  leftMonitor.rotation.y = Math.PI / 8; // 중앙을 향해 틀어짐
  leftMonitor.material = darkMat;
  leftMonitor.parent = frame;

  const leftScreen = BABYLON.MeshBuilder.CreatePlane("leftScreen", {width: w * 0.43, height: h * 0.27999999999999997}, scene);
  leftScreen.position = new BABYLON.Vector3(-3.45, baseHeight + 6, -0.31);
  leftScreen.rotation.y = Math.PI / 8;
  leftScreen.material = screenMat;
  leftScreen.parent = frame;

  // 우측 대형 모니터
  const rightMonitor = BABYLON.MeshBuilder.CreateBox("rightMonitor", {width: w * 0.45, height: h * 0.3, depth: d * 0.02}, scene);
  rightMonitor.position = new BABYLON.Vector3(3.5, baseHeight + 6, -0.2);
  rightMonitor.rotation.y = -Math.PI / 8; // 중앙을 향해 틀어짐
  rightMonitor.material = darkMat;
  rightMonitor.parent = frame;

  const rightScreen = BABYLON.MeshBuilder.CreatePlane("rightScreen", {width: w * 0.43, height: h * 0.27999999999999997}, scene);
  rightScreen.position = new BABYLON.Vector3(3.45, baseHeight + 6, -0.31);
  rightScreen.rotation.y = -Math.PI / 8;
  rightScreen.material = screenMat;
  rightScreen.parent = frame;

  // 4. 중앙 테스트 챔버 및 지그 (Center Testing Area)
  // 후면 광원 차트 (백라이트)
  const chartBack = BABYLON.MeshBuilder.CreatePlane("chartBack", {width: w * 0.6799999999999999, height: h * 0.65}, scene);
  chartBack.position = new BABYLON.Vector3(0, baseHeight + 4, 2.9);
  chartBack.material = chartBacklightMat;
  chartBack.parent = frame;

  // 체커보드 패턴 (단순화된 검은색 마커들)
  const markerPositions = [
    {x: -2, y: 5}, {x: 0, y: 6}, {x: 2, y: 5},
    {x: -1, y: 3}, {x: 1, y: 3}
  ];
  markerPositions.forEach((pos, i) => {
    const marker = BABYLON.MeshBuilder.CreatePlane(`marker_${i}`, {size: w * 0.05}, scene);
    marker.position = new BABYLON.Vector3(pos.x, baseHeight + pos.y - 1, 2.89);
    marker.material = blackMat;
    marker.parent = frame;
  });

  // 듀얼 테스트 지그 (좌/우)
  [-1.5, 1.5].forEach((posX, idx) => {
    const jigBase = BABYLON.MeshBuilder.CreateBox(`jigBase_${idx}`, {width: w * 0.18, height: h * 0.15, depth: d * 0.2}, scene);
    jigBase.position = new BABYLON.Vector3(posX, baseHeight + 1.05, 1);
    jigBase.material = darkMat;
    jigBase.parent = frame;

    const jigTop = BABYLON.MeshBuilder.CreateBox(`jigTop_${idx}`, {width: w * 0.12, height: h * 0.08, depth: d * 0.12}, scene);
    jigTop.position = new BABYLON.Vector3(posX, baseHeight + 2.2, 1.2);
    jigTop.material = darkMat;
    jigTop.parent = frame;

    // 금색 포인트 부품
    const goldPart = BABYLON.MeshBuilder.CreateBox(`goldPart_${idx}`, {width: w * 0.04, height: h * 0.04, depth: d * 0.06}, scene);
    goldPart.position = new BABYLON.Vector3(posX + 0.5, baseHeight + 1.5, 0.5);
    goldPart.material = goldMat;
    goldPart.parent = frame;

    // 파란색 튜브
    const tube = BABYLON.MeshBuilder.CreateCylinder(`tube_${idx}`, {diameter: w * 0.008, height: h * 0.15}, scene);
    tube.position = new BABYLON.Vector3(posX - 0.5, baseHeight + 2, 0.5);
    tube.rotation.x = -Math.PI / 4;
    tube.material = blueTubeMat;
    tube.parent = frame;
  });

  // 조작 버튼부 (중앙 앞쪽)
  const buttonPanel = BABYLON.MeshBuilder.CreateBox("buttonPanel", {width: w * 0.2, height: h * 0.01, depth: d * 0.06}, scene);
  buttonPanel.position = new BABYLON.Vector3(0, baseHeight + 0.35, -0.5);
  buttonPanel.material = metalMat;
  buttonPanel.parent = frame;

  const btnLeft = BABYLON.MeshBuilder.CreateCylinder("btnLeft", {diameter: w * 0.025, height: h * 0.015}, scene);
  btnLeft.position = new BABYLON.Vector3(-0.5, baseHeight + 0.45, -0.5);
  const grnMat = new BABYLON.StandardMaterial("grnMat", scene);
  grnMat.diffuseColor = new BABYLON.Color3(0, 0.8, 0);
  btnLeft.material = grnMat;
  btnLeft.parent = frame;

  const btnRight = BABYLON.MeshBuilder.CreateCylinder("btnRight", {diameter: w * 0.025, height: h * 0.015}, scene);
  btnRight.position = new BABYLON.Vector3(0.5, baseHeight + 0.45, -0.5);
  btnRight.material = grnMat;
  btnRight.parent = frame;
};