window.buildIntrinsicCalibrationModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 외관 메인 프레임 (흰색/밝은 회색)
  const whiteBodyMat = new BABYLON.StandardMaterial("whiteBodyMat", scene);
  whiteBodyMat.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.92);

  // 내부 어두운 챔버 및 기구물
  const darkInternalMat = new BABYLON.StandardMaterial("darkInternalMat", scene);
  darkInternalMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.12);

  // 전면 차폐창 (짙은 틴팅 아크릴)
  const tintedGlassMat = new BABYLON.StandardMaterial("tintedGlassMat", scene);
  tintedGlassMat.diffuseColor = new BABYLON.Color3(0.1, 0.15, 0.2);
  tintedGlassMat.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);
  tintedGlassMat.alpha = 0.6; // 내부가 살짝 비치는 틴팅
  tintedGlassMat.backFaceCulling = false;

  // 안전 센서바 및 코일 선 (눈에 띄는 노란색)
  const yellowSafetyMat = new BABYLON.StandardMaterial("yellowSafetyMat", scene);
  yellowSafetyMat.diffuseColor = new BABYLON.Color3(0.95, 0.85, 0.1);
  yellowSafetyMat.emissiveColor = new BABYLON.Color3(0.2, 0.2, 0); // 살짝 밝게

  // 다관절 암 및 모니터 베이스 (검은색 무광)
  const blackArmMat = new BABYLON.StandardMaterial("blackArmMat", scene);
  blackArmMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.15);

  // 모니터 화면 (빛나는 파란색 UI)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.3, 0.6);
  screenMat.diffuseColor = new BABYLON.Color3(0, 0, 0);

  // 버튼류 컬러
  const redBtnMat = new BABYLON.StandardMaterial("redBtnMat", scene);
  redBtnMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  const greenBtnMat = new BABYLON.StandardMaterial("greenBtnMat", scene);
  greenBtnMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("ipcMachineFrame", scene);
  frameNode.parent = machineMesh;

  const width = 8;
  const height = 16;
  const depth = 6;

  // 2. 메인 캐비닛 구조 (Main Cabinet Structure)
  // 하부 베이스
  const lowerBase = BABYLON.MeshBuilder.CreateBox("lowerBase", {width: width, height: h * 0.6, depth: depth}, scene);
  lowerBase.position.y = h * 0.3;
  lowerBase.material = whiteBodyMat;
  lowerBase.parent = frameNode;

  // 하단 전면 유지보수 패널 라인 (음각 느낌)
  const maintPanel = BABYLON.MeshBuilder.CreateBox("maintPanel", {width: w * 0.4, height: h * 0.3, depth: d * 0.01}, scene);
  maintPanel.position = new BABYLON.Vector3(0, 3, -(depth / 2) - 0.01);
  maintPanel.material = whiteBodyMat;
  maintPanel.parent = frameNode;

  // 좌/우측 및 후면 벽 (챔버 구성을 위해)
  const leftWall = BABYLON.MeshBuilder.CreateBox("leftWall", {width: w * 0.15, height: h * 0.6, depth: depth}, scene);
  leftWall.position = new BABYLON.Vector3(-(width / 2) + 0.75, 9, 0);
  leftWall.material = whiteBodyMat;
  leftWall.parent = frameNode;

  const rightWall = BABYLON.MeshBuilder.CreateBox("rightWall", {width: w * 0.15, height: h * 0.6, depth: depth}, scene);
  rightWall.position = new BABYLON.Vector3((width / 2) - 0.75, 9, 0);
  rightWall.material = whiteBodyMat;
  rightWall.parent = frameNode;

  const backWall = BABYLON.MeshBuilder.CreateBox("backWall", {width: width - 3, height: h * 0.6, depth: d * 0.2}, scene);
  backWall.position = new BABYLON.Vector3(0, 9, (depth / 2) - 1);
  backWall.material = darkInternalMat; // 내부는 어둡게
  backWall.parent = frameNode;

  // 상단 헤드 덮개
  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: width, height: h * 0.4, depth: depth}, scene);
  topCover.position = new BABYLON.Vector3(0, 14, 0);
  topCover.material = whiteBodyMat;
  topCover.parent = frameNode;

  // 3. 중앙 챔버 창 및 안전 센서 (Chamber Window & Safety Light Curtains)
  // 좌측 노란색 안전 센서 바
  const leftSafetyBar = BABYLON.MeshBuilder.CreateBox("leftSafetyBar", {width: w * 0.03, height: h * 0.55, depth: d * 0.04}, scene);
  leftSafetyBar.position = new BABYLON.Vector3(-(width / 2) + 1.6, 9, -(depth / 2) + 0.1);
  leftSafetyBar.material = yellowSafetyMat;
  leftSafetyBar.parent = frameNode;

  // 우측 노란색 안전 센서 바
  const rightSafetyBar = BABYLON.MeshBuilder.CreateBox("rightSafetyBar", {width: w * 0.03, height: h * 0.55, depth: d * 0.04}, scene);
  rightSafetyBar.position = new BABYLON.Vector3((width / 2) - 1.6, 9, -(depth / 2) + 0.1);
  rightSafetyBar.material = yellowSafetyMat;
  rightSafetyBar.parent = frameNode;

  // 짙은 틴팅 차폐창 (센서 바 안쪽)
  const tintedShield = BABYLON.MeshBuilder.CreateBox("tintedShield", {width: width - 3.5, height: h * 0.55, depth: d * 0.01}, scene);
  tintedShield.position = new BABYLON.Vector3(0, 9, -(depth / 2) + 0.2);
  tintedShield.material = tintedGlassMat;
  tintedShield.parent = frameNode;

  // 챔버 내부 검사 지그 플레이스홀더
  const innerJig = BABYLON.MeshBuilder.CreateBox("innerJig", {width: w * 0.2, height: h * 0.1, depth: d * 0.2}, scene);
  innerJig.position = new BABYLON.Vector3(0, 6.5, -1);
  innerJig.material = darkInternalMat;
  innerJig.parent = frameNode;

  // 4. 좌측 부가 요소 (Left Side Elements - Buttons & Scanner)
  // 버튼 조작부 패널
  const leftBtnPanel = BABYLON.MeshBuilder.CreateBox("leftBtnPanel", {width: w * 0.1, height: h * 0.3, depth: d * 0.1}, scene);
  leftBtnPanel.position = new BABYLON.Vector3(-(width / 2) - 0.2, 10, -(depth / 2) + 0.5);
  leftBtnPanel.material = whiteBodyMat;
  leftBtnPanel.parent = frameNode;

  // 비상 정지 버튼 (E-Stop)
  const eStop = BABYLON.MeshBuilder.CreateCylinder("eStop", {diameter: w * 0.06, height: h * 0.02}, scene);
  eStop.position = new BABYLON.Vector3(-(width / 2) - 0.2, 9.5, -(depth / 2) - 0.05);
  eStop.rotation.x = Math.PI / 2;
  eStop.material = redBtnMat;
  eStop.parent = frameNode;

  const startBtn = BABYLON.MeshBuilder.CreateCylinder("startBtn", {diameter: w * 0.04, height: h * 0.02}, scene);
  startBtn.position = new BABYLON.Vector3(-(width / 2) - 0.2, 10.5, -(depth / 2) - 0.05);
  startBtn.rotation.x = Math.PI / 2;
  startBtn.material = greenBtnMat;
  startBtn.parent = frameNode;

  // 노란색 바코드 스캐너 홀더 및 코일 케이블 (디테일)
  const scannerHolder = BABYLON.MeshBuilder.CreateBox("scannerHolder", {width: w * 0.08, height: h * 0.15, depth: d * 0.1}, scene);
  scannerHolder.position = new BABYLON.Vector3(-(width / 2) - 0.2, 7.5, -(depth / 2) + 0.5);
  scannerHolder.material = whiteBodyMat;
  scannerHolder.parent = frameNode;

  const yellowCoil = BABYLON.MeshBuilder.CreateCylinder("yellowCoil", {diameter: w * 0.03, height: h * 0.25}, scene);
  yellowCoil.position = new BABYLON.Vector3(-(width / 2) - 0.2, 5.5, -(depth / 2) + 0.2);
  yellowCoil.material = yellowSafetyMat;
  yellowCoil.parent = frameNode; // 노란색 스프링 코일 케이블을 실린더로 단순 묘사

  // 좌측 상단 타워 램프 (Tower Light - 녹색 점등 상태)
  const towerPole = BABYLON.MeshBuilder.CreateCylinder("towerPole", {diameter: w * 0.015, height: h * 0.15}, scene);
  towerPole.position = new BABYLON.Vector3(-(width / 2) + 0.5, 16.5, -(depth / 2) + 1);
  towerPole.material = whiteBodyMat;
  towerPole.parent = frameNode;

  const topLight = BABYLON.MeshBuilder.CreateCylinder("topLight", {diameter: w * 0.04, height: h * 0.05}, scene);
  topLight.position = new BABYLON.Vector3(-(width / 2) + 0.5, 17.5, -(depth / 2) + 1);
  const greenLightMat = new BABYLON.StandardMaterial("greenLightMat", scene);
  greenLightMat.diffuseColor = new BABYLON.Color3(0, 1, 0);
  greenLightMat.emissiveColor = new BABYLON.Color3(0, 1, 0); // 밝게 빛남
  topLight.material = greenLightMat;
  topLight.parent = frameNode;

  // 5. 우측 모니터 및 다관절 암 (Right Side Monitor & Arm)
  // 관절 암 1 (본체에 연결)
  const arm1 = BABYLON.MeshBuilder.CreateBox("arm1", {width: w * 0.25, height: h * 0.03, depth: d * 0.03}, scene);
  arm1.position = new BABYLON.Vector3((width / 2) + 1, 8.5, -(depth / 2) + 0.5);
  arm1.material = blackArmMat;
  arm1.parent = frameNode;

  // 관절 암 2 (모니터로 연결 - 살짝 앞으로 꺾임)
  const arm2 = BABYLON.MeshBuilder.CreateBox("arm2", {width: w * 0.25, height: h * 0.03, depth: d * 0.03}, scene);
  arm2.position = new BABYLON.Vector3((width / 2) + 3, 8.5, -(depth / 2) - 0.5);
  arm2.rotation.y = -Math.PI / 4;
  arm2.material = blackArmMat;
  arm2.parent = frameNode;

  // Elo 터치 모니터 본체
  const monitorNode = new BABYLON.TransformNode("monitorNode", scene);
  monitorNode.position = new BABYLON.Vector3((width / 2) + 4, 9, -(depth / 2) - 1.5);
  monitorNode.rotation.y = -Math.PI / 6; // 사용자(중앙)를 향하도록 살짝 틈
  monitorNode.parent = frameNode;

  const monitorBack = BABYLON.MeshBuilder.CreateBox("monitorBack", {width: w * 0.4, height: h * 0.3, depth: d * 0.03}, scene);
  monitorBack.material = blackArmMat;
  monitorBack.parent = monitorNode;

  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.36, height: h * 0.26}, scene);
  monitorScreen.position = new BABYLON.Vector3(0, 0, -0.16); // 본체 앞면에 부착
  monitorScreen.material = screenMat;
  monitorScreen.parent = monitorNode;

  // 키보드 거치대 (모니터 하단)
  const kbdTray = BABYLON.MeshBuilder.CreateBox("kbdTray", {width: w * 0.4, height: h * 0.01, depth: d * 0.15}, scene);
  kbdTray.position = new BABYLON.Vector3(0, -2, -0.5);
  kbdTray.rotation.x = Math.PI / 12; // 살짝 기울어짐
  kbdTray.material = blackArmMat;
  kbdTray.parent = monitorNode;
};