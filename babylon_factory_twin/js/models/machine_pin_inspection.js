window.buildPinInspectionModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 외관 메인 프레임 (밝은 회색/흰색 - 16_PinTest_01.jpg 참조)
  const grayMat = new BABYLON.StandardMaterial("grayMat", scene);
  grayMat.diffuseColor = new BABYLON.Color3(0.75, 0.75, 0.78);
  grayMat.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);

  // 내부 기구물 및 하단 베이스 (어두운 회색/검정)
  const darkInternalMat = new BABYLON.StandardMaterial("darkInternalMat", scene);
  darkInternalMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.18);

  // 전면 관찰창 (투명 아크릴)
  const glassPanelMat = new BABYLON.StandardMaterial("glassPanelMat", scene);
  glassPanelMat.diffuseColor = new BABYLON.Color3(0.8, 0.85, 0.9);
  glassPanelMat.alpha = 0.3; // 반투명
  glassPanelMat.backFaceCulling = false; // 양면 렌더링

  // 핀 지그 베이스 (검은색 ESD 재질 느낌 - 16_PinTest_02.jpg 참조)
  const darkJigMat = new BABYLON.StandardMaterial("darkJigMat", scene);
  darkJigMat.diffuseColor = new BABYLON.Color3(0.08, 0.08, 0.1);

  // 포고 핀 어레이 (금색/황동색 포인트 컬러)
  const goldPinMat = new BABYLON.StandardMaterial("goldPinMat", scene);
  goldPinMat.diffuseColor = new BABYLON.Color3(0.9, 0.75, 0.2);
  goldPinMat.specularColor = new BABYLON.Color3(1, 1, 0.6); // Shiny gold

  // 배선 및 튜브 포인트 (파란색/검은색 섞임)
  const wireMat = new BABYLON.StandardMaterial("wireMat", scene);
  wireMat.diffuseColor = new BABYLON.Color3(0.2, 0.5, 0.9);

  // 버튼류 컬러 (자체 발광 포함)
  const redBtnMat = new BABYLON.StandardMaterial("redBtnMat", scene);
  redBtnMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  redBtnMat.emissiveColor = new BABYLON.Color3(0.4, 0, 0);

  const greenBtnMat = new BABYLON.StandardMaterial("greenBtnMat", scene);
  greenBtnMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);
  greenBtnMat.emissiveColor = new BABYLON.Color3(0, 0.4, 0);

  const yellowMat = new BABYLON.StandardMaterial("yellowMat", scene);
  yellowMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("pinInspectionFrame", scene);
  frameNode.parent = machineMesh;

  const frameWidth = 10;
  const frameHeight = 14; // 타워 램프 제외 본체 높이
  const frameDepth = 8;

  // 2. 외부 인클로저 (External Enclosure)
  // 하부 캐비닛 및 베이스 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameWidth, height: h * 0.5, depth: frameDepth}, scene);
  baseCabinet.position.y = h * 0.25;
  baseCabinet.material = grayMat;
  baseCabinet.parent = frameNode;

  // 상부 작업 챔버 메인 프레임 (Upper Chamber Frame)
  const chamberFrame = BABYLON.MeshBuilder.CreateBox("chamberFrame", {width: frameWidth, height: h * 0.9, depth: frameDepth}, scene);
  chamberFrame.position.y = h * 0.95;
  chamberFrame.material = grayMat;
  chamberFrame.parent = frameNode;
  chamberFrame.isVisible = false; // 프레임 외형만 잡고 내부는 비움

  // 수직 지지 기둥 (Pillars - 4모서리)
  const pillarPositions = [
    {x: -4.75, z: -3.75}, {x: 4.75, z: -3.75},
    {x: -4.75, z: 3.75}, {x: 4.75, z: 3.75}
  ];
  pillarPositions.forEach((pos, index) => {
    const pillar = BABYLON.MeshBuilder.CreateBox(`pillar_${index}`, {width: w * 0.05, height: h * 0.9, depth: d * 0.05}, scene);
    pillar.position = new BABYLON.Vector3(pos.x, 9.5, pos.z);
    pillar.material = grayMat;
    pillar.parent = frameNode;
  });

  // 상단 덮개 및 공조 장치
  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: frameWidth, height: h * 0.05, depth: frameSize.depth}, scene);
  topCover.position.y = h * 1.375;
  topCover.material = grayMat;
  topCover.parent = frameNode;

  const airUnit = BABYLON.MeshBuilder.CreateBox("airUnit", {width: w * 0.5, height: h * 0.1, depth: d * 0.5}, scene);
  airUnit.position.y = h * 1.45; // 탑 커버 위에 돌출
  airUnit.material = darkInternalMat;
  airUnit.parent = frameNode;

  // 3. 관찰창 및 손잡이 (Panels & Handles)
  // 전면 대형 유리 도어
  const frontGlass = BABYLON.MeshBuilder.CreateBox("frontGlass", {width: w * 0.9, height: h * 0.85, depth: d * 0.01}, scene);
  frontGlass.position = new BABYLON.Vector3(0, 9.25, -frameDepth / 2 - 0.05);
  frontGlass.material = glassPanelMat;
  frontGlass.parent = frameNode;

  // 도어 가로 지지대 및 수직 손잡이 디테일 (은색)
  const handleBar = BABYLON.MeshBuilder.CreateBox("handleBar", {width: w * 0.9, height: h * 0.02, depth: d * 0.03}, scene);
  handleBar.position = new BABYLON.Vector3(0, 7.5, -frameSize.depth/2 - 0.2);
  handleBar.material = grayMat;
  handleBar.parent = frameNode;

  const leftHandle = BABYLON.MeshBuilder.CreateCylinder("frontHandle0", {diameter: w * 0.01, height: h * 0.1}, scene);
  leftHandle.position = new BABYLON.Vector3(-2, 7, -frameSize.depth/2 - 0.2);
  leftHandle.material = grayMat;
  leftHandle.parent = frameNode;

  const rightHandle = BABYLON.MeshBuilder.CreateCylinder("frontHandle1", {diameter: w * 0.01, height: h * 0.1}, scene);
  rightHandle.position = new BABYLON.Vector3(2, 7, -frameSize.depth/2 - 0.2);
  rightHandle.material = grayMat;
  rightHandle.parent = frameNode;

  // 4. 전면 하부 조작 패널 (Front Control Panel - 16_PinTest_01.jpg 참조)
  // 비스듬한 형태의 슬라이딩 도어 및 버튼부
  const controlPanel = BABYLON.MeshBuilder.CreateBox("controlPanel", {width: frameWidth - 0.5, height: h * 0.2, depth: d * 0.1}, scene);
  controlPanel.position.y = h * 0.55;
  controlPanel.position.z = -frameSize.depth/2 - 0.3;
  controlPanel.rotation.x = Math.PI / 12; // 살짝 앞쪽으로 꺾인 각도
  controlPanel.material = grayMat;
  controlPanel.parent = frameNode;

  // 비상 정지 버튼 (E-Stop - 노란 베이스 + 큰 빨간 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateBox("eStopBase", {width: w * 0.12, height: h * 0.02, depth: d * 0.12}, scene);
  eStopBase.position.x = w * -0.35;
  eStopBase.position.y = h * 0.5599999999999999;
  eStopBase.position.z = -frameSize.depth/2 - 0.9;
  eStopBase.rotation.x = Math.PI / 12;
  eStopBase.material = yellowMat;
  eStopBase.parent = frameNode;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.04}, scene);
  eStopBtn.position.x = w * -0.35;
  eStopBtn.position.y = h * 0.5700000000000001;
  eStopBtn.position.z = -frameSize.depth/2 - 0.95;
  eStopBtn.rotation.x = Math.PI / 12 + Math.PI / 2;
  eStopBtn.material = redBtnMat;
  eStopBtn.parent = frameNode;

  // 작은 조작 버튼 (파워, 시작 등)
  const smallBtn = BABYLON.MeshBuilder.CreateCylinder("smallBtn", {diameter: w * 0.03, height: h * 0.02}, scene);
  smallBtn.position.x = w * -0.25;
  smallBtn.position.y = h * 0.5549999999999999;
  smallBtn.position.z = -frameSize.depth/2 - 0.9;
  smallBtn.rotation.x = Math.PI / 12 + Math.PI / 2;
  smallBtn.material = greenBtnMat;
  smallBtn.parent = frameNode;

  // 5. 핵심 특징: 핀 검사 지그 및 어레이 (Inner Jig & Pin Array - 16_PinTest_02.jpg 참조)
  // 하부 고정 지그 베이스 (검은색 무광)
  const dutStage = BABYLON.MeshBuilder.CreateBox("dutStage", {width: frameWidth - 2, height: h * 0.15, depth: frameDepth - 2}, scene);
  dutStage.position.y = h * 0.5 + 0.75; // 베이스 캐비닛 바로 위
  dutStage.material = darkJigMat;
  dutStage.parent = frameNode;

  // 산업용 안티-스틱 트레이 (앞서 모델링한 형태를 단순화하여 배치)
  const tray = BABYLON.MeshBuilder.CreateBox("dutTray", {width: w * 0.6, height: h * 0.02, depth: d * 0.4}, scene);
  tray.position = new BABYLON.Vector3(0, 5 + 1.5 + 0.1, 1);
  tray.material = darkJigMat;
  tray.parent = frameNode;

  // 핵심 특징: 금색 포고 핀 어레이 (미세 실린더 어레이 - 02_이미지 포인트)
  const pinGridRows = 5;
  const pinGridCols = 4;
  const pinSpacing = 0.5;

  for (let r = 0; r < pinGridRows; r++) {
    for (let c = 0; c < pinGridCols; c++) {
      const posX = -0.75 + c * pinSpacing;
      const posZ = -1 + r * pinSpacing;

      const pogoPin = BABYLON.MeshBuilder.CreateCylinder(`pogoPin_r${r}_c${c}`, {diameter: w * 0.008, height: h * 0.06}, scene);
      pogoPin.position = new BABYLON.Vector3(posX - 1.5, 5 + 1.5 + 0.3, posZ + 0.5); // 트레이 왼쪽 자재 포켓 위
      pogoPin.material = goldPinMat;
      pogoPin.parent = frameNode;
    }
  }

  // 챔버 내부 검사 헤드 메커니즘
  const cameraMechanism = BABYLON.MeshBuilder.CreateBox("cameraMechanism", {width: w * 0.45, height: h * 0.2, depth: d * 0.15}, scene);
  cameraMechanism.position.y = h * 1.25;
  cameraMechanism.position.z = d * -0.1; // 중앙 위에 배치
  cameraMechanism.material = darkInternalMat;
  cameraMechanism.parent = frameNode;

  // 6. 타워 램프 (Tower Light - 우측 상단 타워 램프)
  const towerPole = BABYLON.MeshBuilder.CreateCylinder("towerPole", {diameter: w * 0.015, height: h * 0.2}, scene);
  towerPole.position.x = w * 0.4;
  towerPole.position.y = h * 1.475;
  towerPole.position.z = d * 0.2;
  towerPole.material = metalMat;
  towerPole.parent = frameNode;

  const colors = [
    { name: "grn", col: new BABYLON.Color3(0, 1, 0), y: 15.2 },
    { name: "yel", col: new BABYLON.Color3(1, 1, 0), y: 15.6 },
    { name: "red", col: new BABYLON.Color3(1, 0, 0), y: 16.0 }
  ];

  colors.forEach(c => {
    const mat = new BABYLON.StandardMaterial(c.name + "TMat", scene);
    mat.diffuseColor = c.col;
    mat.emissiveColor = c.col;
    const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "TLight", {diameter: w * 0.04, height: h * 0.025}, scene);
    light.position.x = w * 0.4;
    light.position.y = c.y;
    light.position.z = d * 0.2;
    light.material = mat;
    light.parent = frameNode;
  });
};