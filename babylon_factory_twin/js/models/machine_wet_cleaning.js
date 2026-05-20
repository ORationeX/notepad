window.buildWetCleaningModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 폴리싱된 스테인리스 스틸 (광택이 매우 강한 은색)
  const stainlessMat = new BABYLON.StandardMaterial("stainlessMat", scene);
  stainlessMat.diffuseColor = new BABYLON.Color3(0.7, 0.7, 0.75);
  stainlessMat.specularColor = new BABYLON.Color3(1, 1, 1);
  stainlessMat.roughness = 0.15; // 강한 반사광

  // 챔버 내부 회전판 및 기구물 (무광 스테인리스/알루미늄)
  const dullMetalMat = new BABYLON.StandardMaterial("dullMetalMat", scene);
  dullMetalMat.diffuseColor = new BABYLON.Color3(0.5, 0.5, 0.55);

  // 내부 고정 지그 및 고무 패킹 (검은색)
  const blackMat = new BABYLON.StandardMaterial("blackMat", scene);
  blackMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.1);

  // 곡면 투명 유리 도어
  const glassMat = new BABYLON.StandardMaterial("glassMat", scene);
  glassMat.diffuseColor = new BABYLON.Color3(0.8, 0.9, 0.9);
  glassMat.alpha = 0.3; // 투명도
  glassMat.backFaceCulling = false; // 양면 렌더링
  glassMat.specularColor = new BABYLON.Color3(1, 1, 1);

  // 제어 패널 화면 및 버튼
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.2, 0.4, 0.8); // 파란색 계열 화면
  screenMat.diffuseColor = new BABYLON.Color3(0, 0, 0);

  const greenBtnMat = new BABYLON.StandardMaterial("greenBtnMat", scene);
  greenBtnMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);
  const redBtnMat = new BABYLON.StandardMaterial("redBtnMat", scene);
  redBtnMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  const yellowBtnMat = new BABYLON.StandardMaterial("yellowBtnMat", scene);
  yellowBtnMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  const whiteBtnMat = new BABYLON.StandardMaterial("whiteBtnMat", scene);
  whiteBtnMat.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.9);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("wetCleaningFrame", scene);
  frameNode.parent = machineMesh;

  const width = 11;
  const depth = 9;
  const baseHeight = 5;
  const chamberHeight = 9;

  // 2. 외부 프레임 및 하부 캐비닛 (Outer Enclosure & Base)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: width, height: baseHeight, depth: depth}, scene);
  baseCabinet.position.y = baseHeight / 2;
  baseCabinet.material = stainlessMat;
  baseCabinet.parent = frameNode;

  // 좌/우/후/상단 패널 (챔버를 감싸는 형태)
  const leftWall = BABYLON.MeshBuilder.CreateBox("leftWall", {width: w * 0.1, height: chamberHeight, depth: depth}, scene);
  leftWall.position = new BABYLON.Vector3(-(width / 2) + 0.5, baseHeight + (chamberHeight / 2), 0);
  leftWall.material = stainlessMat;
  leftWall.parent = frameNode;

  const rightWall = BABYLON.MeshBuilder.CreateBox("rightWall", {width: w * 0.1, height: chamberHeight, depth: depth}, scene);
  rightWall.position = new BABYLON.Vector3((width / 2) - 0.5, baseHeight + (chamberHeight / 2), 0);
  rightWall.material = stainlessMat;
  rightWall.parent = frameNode;

  const backWall = BABYLON.MeshBuilder.CreateBox("backWall", {width: width - 2, height: chamberHeight, depth: d * 0.1}, scene);
  backWall.position = new BABYLON.Vector3(0, baseHeight + (chamberHeight / 2), (depth / 2) - 0.5);
  backWall.material = stainlessMat;
  backWall.parent = frameNode;

  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: width, height: h * 0.15, depth: depth}, scene);
  topCover.position = new BABYLON.Vector3(0, baseHeight + chamberHeight + 0.75, 0);
  topCover.material = stainlessMat;
  topCover.parent = frameNode;

  // 3. 원통형 세정 챔버 및 내부 회전판 (Cylindrical Chamber & Plate)
  // 챔버 내부 벽면 (반원 형태의 실린더)
  const innerChamber = BABYLON.MeshBuilder.CreateCylinder("innerChamber", {
    diameter: w * 0.8, height: chamberHeight - 0.5, arc: 0.55, sideOrientation: BABYLON.Mesh.DOUBLESIDE
  }, scene);
  innerChamber.position = new BABYLON.Vector3(0, baseHeight + (chamberHeight / 2), 1.5);
  innerChamber.rotation.y = Math.PI; // 뒤쪽을 향하도록 회전
  innerChamber.material = stainlessMat;
  innerChamber.parent = frameNode;

  // 중앙 스핀들 (회전축)
  const spindle = BABYLON.MeshBuilder.CreateCylinder("spindle", {diameter: w * 0.15, height: h * 0.2}, scene);
  spindle.position = new BABYLON.Vector3(0, baseHeight + 1, 0);
  spindle.material = dullMetalMat;
  spindle.parent = frameNode;

  // 제품 고정용 회전판 (Rotating Plate)
  const plateNode = new BABYLON.TransformNode("plateNode", scene);
  plateNode.position = new BABYLON.Vector3(0, baseHeight + 2, 0);
  plateNode.parent = frameNode;

  const plate = BABYLON.MeshBuilder.CreateCylinder("plate", {diameter: w * 0.65, height: h * 0.015}, scene);
  plate.material = dullMetalMat;
  plate.parent = plateNode;

  // 가장자리 검은색 고정 지그(Jigs)들 배치
  const jigCount = 8;
  for (let i = 0; i < jigCount; i++) {
    const angle = (i * Math.PI * 2) / jigCount;
    const jig = BABYLON.MeshBuilder.CreateBox(`jig_${i}`, {width: w * 0.06, height: h * 0.04, depth: d * 0.12}, scene);
    
    // 원통 좌표계에 맞게 배치
    jig.position.x = Math.cos(angle) * 2.8;
    jig.position.z = Math.sin(angle) * 2.8;
    jig.position.y = h * 0.025;
    jig.rotation.y = -angle; // 중심을 바라보도록 회전
    
    jig.material = blackMat;
    jig.parent = plateNode;
  }

  // 4. 전면 원통형 유리 도어 (Front Curved Glass Door)
  // 닫힌 상태의 둥근 유리창 (arc를 활용)
  const doorGlass = BABYLON.MeshBuilder.CreateCylinder("doorGlass", {
    diameter: w * 0.82, height: chamberHeight - 1, arc: 0.4, sideOrientation: BABYLON.Mesh.DOUBLESIDE
  }, scene);
  doorGlass.position = new BABYLON.Vector3(0, baseHeight + (chamberHeight / 2), 1.3);
  doorGlass.rotation.y = -Math.PI * 0.2; // 정면을 덮도록 회전
  doorGlass.material = glassMat;
  doorGlass.parent = frameNode;

  // 도어 테두리 검은색 고무 패킹 (Gasket)
  // 편의상 상하단 둥근 테두리를 얇은 실린더로 덧댐
  const gasketTop = BABYLON.MeshBuilder.CreateCylinder("gasketTop", {diameter: w * 0.8300000000000001, height: h * 0.01, arc: 0.4}, scene);
  gasketTop.position = new BABYLON.Vector3(0, baseHeight + chamberHeight - 0.5, 1.3);
  gasketTop.rotation.y = -Math.PI * 0.2;
  gasketTop.material = blackMat;
  gasketTop.parent = frameNode;

  const gasketBottom = BABYLON.MeshBuilder.CreateCylinder("gasketBottom", {diameter: w * 0.8300000000000001, height: h * 0.01, arc: 0.4}, scene);
  gasketBottom.position = new BABYLON.Vector3(0, baseHeight + 0.5, 1.3);
  gasketBottom.rotation.y = -Math.PI * 0.2;
  gasketBottom.material = blackMat;
  gasketBottom.parent = frameNode;

  // 도어 손잡이
  const doorHandle = BABYLON.MeshBuilder.CreateCylinder("doorHandle", {diameter: w * 0.015, height: h * 0.15}, scene);
  doorHandle.position = new BABYLON.Vector3(3.5, baseHeight + (chamberHeight / 2), -2);
  doorHandle.material = stainlessMat;
  doorHandle.parent = frameNode;

  // 5. 제어 패널 (Control Panel - 우측 돌출부)
  const ctrlPanel = BABYLON.MeshBuilder.CreateBox("ctrlPanel", {width: w * 0.35, height: h * 0.35, depth: d * 0.1}, scene);
  ctrlPanel.position = new BABYLON.Vector3((width / 2) + 0.5, baseHeight + 6, -(depth / 2) + 1.5);
  ctrlPanel.rotation.y = -Math.PI / 6; // 사용자를 향해 꺾임
  ctrlPanel.material = stainlessMat;
  ctrlPanel.parent = frameNode;

  // HMI 디스플레이
  const screen = BABYLON.MeshBuilder.CreatePlane("screen", {width: w * 0.25, height: h * 0.18}, scene);
  screen.position = new BABYLON.Vector3(0, 0.5, -0.51);
  screen.material = screenMat;
  screen.parent = ctrlPanel;

  // 조작 버튼부 (녹/적/황/백)
  const btnColors = [greenBtnMat, redBtnMat, yellowBtnMat, whiteBtnMat];
  btnColors.forEach((mat, i) => {
    const btn = BABYLON.MeshBuilder.CreateCylinder(`ctrlBtn_${i}`, {diameter: w * 0.04, height: h * 0.02}, scene);
    btn.position = new BABYLON.Vector3(-0.9 + (i * 0.6), -0.8, -0.5);
    btn.rotation.x = Math.PI / 2;
    btn.material = mat;
    btn.parent = ctrlPanel;
  });

  // 6. 하부 디테일 (Lower Details - 공압/진공 게이지 및 도어)
  // 캐비닛 전면 도어 손잡이 (매립형 느낌)
  const lowerHandle1 = BABYLON.MeshBuilder.CreateBox("lowerHandle1", {width: w * 0.02, height: h * 0.15, depth: d * 0.01}, scene);
  lowerHandle1.position = new BABYLON.Vector3(-2, baseHeight / 2 - 0.5, -(depth / 2) - 0.01);
  lowerHandle1.material = blackMat;
  lowerHandle1.parent = frameNode;

  const lowerHandle2 = BABYLON.MeshBuilder.CreateBox("lowerHandle2", {width: w * 0.02, height: h * 0.15, depth: d * 0.01}, scene);
  lowerHandle2.position = new BABYLON.Vector3(2, baseHeight / 2 - 0.5, -(depth / 2) - 0.01);
  lowerHandle2.material = blackMat;
  lowerHandle2.parent = frameNode;

  // 아날로그 게이지 (하단에 위치한 둥근 다이얼 2개)
  [-1.5, 1.5].forEach((posX, i) => {
    const gaugeBase = BABYLON.MeshBuilder.CreateCylinder(`gauge_${i}`, {diameter: w * 0.1, height: h * 0.02}, scene);
    gaugeBase.position = new BABYLON.Vector3(posX, baseHeight / 2 - 1.5, -(depth / 2) - 0.1);
    gaugeBase.rotation.x = Math.PI / 2;
    gaugeBase.material = blackMat;
    gaugeBase.parent = frameNode;

    const gaugeFace = BABYLON.MeshBuilder.CreateCylinder(`gaugeFace_${i}`, {diameter: w * 0.08, height: h * 0.025}, scene);
    gaugeFace.position = new BABYLON.Vector3(posX, baseHeight / 2 - 1.5, -(depth / 2) - 0.1);
    gaugeFace.rotation.x = Math.PI / 2;
    const whiteFaceMat = new BABYLON.StandardMaterial("whiteFaceMat", scene);
    whiteFaceMat.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.9);
    gaugeFace.material = whiteFaceMat;
    gaugeFace.parent = frameNode;
  });

  // 상단 경광등 (Tower Light)
  const towerLight = BABYLON.MeshBuilder.CreateCylinder("towerLight", {diameter: w * 0.05, height: h * 0.1}, scene);
  towerLight.position = new BABYLON.Vector3(-(width / 2) + 1.5, baseHeight + chamberHeight + 1.5, 0);
  const redEmissiveMat = new BABYLON.StandardMaterial("redEmissiveMat", scene);
  redEmissiveMat.diffuseColor = new BABYLON.Color3(1, 0, 0);
  redEmissiveMat.emissiveColor = new BABYLON.Color3(0.6, 0, 0);
  towerLight.material = redEmissiveMat;
  towerLight.parent = frameNode;
};