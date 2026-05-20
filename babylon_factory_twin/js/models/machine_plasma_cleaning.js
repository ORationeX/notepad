window.buildPlasmaCleaningModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 메탈릭 프레임 (회색)
  const metallicFrameMat = new BABYLON.StandardMaterial("metallicFrameMat", scene);
  metallicFrameMat.diffuseColor = new BABYLON.Color3(0.65, 0.65, 0.68);
  metallicFrameMat.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);

  // 내부 기구물 및 어두운 부품 (검은색)
  const darkInternalMat = new BABYLON.StandardMaterial("darkInternalMat", scene);
  darkInternalMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.18);

  // 전면 관찰창 (짙은 틴팅 아크릴)
  const tintedGlassMat = new BABYLON.StandardMaterial("tintedGlassMat", scene);
  tintedGlassMat.diffuseColor = new BABYLON.Color3(0.1, 0.15, 0.2);
  tintedGlassMat.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);
  tintedGlassMat.alpha = 0.6; // 내부가 살짝 비치는 틴팅
  tintedGlassMat.backFaceCulling = false; // 양면 렌더링

  // 모니터 화면 및 내부 조명 (빛나는 파란색 화면)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.3, 0.6); // 이미지의 푸른빛 MES UI 느낌
  screenMat.diffuseColor = new BABYLON.Color3(0, 0, 0);

  // 손잡이 및 노즐 금속 재질
  const metalToolMat = new BABYLON.StandardMaterial("metalToolMat", scene);
  metalToolMat.diffuseColor = new BABYLON.Color3(0.8, 0.8, 0.82);

  // 타워 램프 (Tower Light - 녹/황/적)
  const towerMatDetails = [
      { name: "red", col: new BABYLON.Color3(1, 0, 0) },
      { name: "yel", col: new BABYLON.Color3(1, 1, 0) },
      { name: "grn", col: new BABYLON.Color3(0, 1, 0) }
  ];

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("plasmaMachineFrame", scene);
  frameNode.parent = machineMesh;

  const frameSize = { width: 10, height: 16, depth: 7 };

  // 2. 외부 프레임 (External Enclosure)
  // 하부 제어반/캐비닛 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameSize.width, height: h * 0.6, depth: frameSize.depth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = metallicFrameMat;
  baseCabinet.parent = frameNode;

  // 상부 작업 챔버 메인 프레임 (Upper Chamber Frame)
  const chamberFrame = BABYLON.MeshBuilder.CreateBox("chamberFrame", {width: frameSize.width, height: h * 1, depth: frameSize.depth}, scene);
  chamberFrame.position.y = h * 1.1;
  chamberFrame.material = darkInternalMat;
  chamberFrame.parent = frameNode;
  chamberFrame.isVisible = false; // 프레임 외형만 잡고 내부는 비움

  // 수직 지지 기둥 (Pillars - 4모서리)
  const beamDetails = [
    {x: -4.75, z: -3.25}, {x: 4.75, z: -3.25},
    {x: -4.75, z: 3.25}, {x: 4.75, z: 3.25}
  ];
  beamDetails.forEach(beam => {
    const sBeam = BABYLON.MeshBuilder.CreateBox("sBeam", {width: w * 0.05, height: h * 1, depth: d * 0.05}, scene);
    sBeam.position = new BABYLON.Vector3(beam.x, 11, beam.z);
    sBeam.material = metallicFrameMat;
    sBeam.parent = frameNode;
  });

  // 상단 덮개 (Top Cover)
  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: frameSize.width, height: h * 0.05, depth: frameSize.depth}, scene);
  topCover.position.y = h * 1.575;
  topCover.material = metallicFrameMat;
  topCover.parent = frameNode;

  // 3. 전면 도어 및 관찰창 (Front Door & Window)
  // 짙은 틴팅 유리창 패널 (챔버 내 기구물이 보이도록)
  const frontGlass = BABYLON.MeshBuilder.CreateBox("frontGlass", {width: w * 0.9, height: h * 0.95, depth: d * 0.01}, scene);
  frontGlass.position = new BABYLON.Vector3(0, 11, -frameSize.depth/2 - 0.05);
  frontGlass.material = tintedGlassMat;
  frontGlass.parent = frameNode;

  // 도어 가로 지지대 및 손잡이 디테일 (은색)
  const handleDetails = [ {x: -2}, {x: 2} ]; // 수직 손잡이 2개
  handleDetails.forEach(handle => {
    const sHandle = BABYLON.MeshBuilder.CreateCylinder("sHandle", {diameter: w * 0.01, height: h * 0.2}, scene);
    sHandle.position = new BABYLON.Vector3(handle.x, 8, -frameSize.depth/2 - 0.2);
    sHandle.material = metalToolMat;
    sHandle.parent = frameNode;
  });

  // 4. 좌측 하단 조작 버튼부 (Lower Control Panel)
  const controlPanel = new BABYLON.TransformNode("controlPanel", scene);
  controlPanel.parent = frameNode;
  controlPanel.position = new BABYLON.Vector3(-4, 4.5, -frameSize.depth/2 - 0.2); // 좌측 하단 프레임에 부착

  // 비상 정지 버튼 (E-Stop - 노란 베이스 + 큰 빨간 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateCylinder("eStopBase", {diameter: w * 0.1, height: h * 0.01}, scene);
  eStopBase.rotation.x = Math.PI / 2;
  const yellowMat = new BABYLON.StandardMaterial("yellowMat", scene);
  yellowMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  eStopBase.material = yellowMat;
  eStopBase.parent = controlPanel;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.06999999999999999, height: h * 0.03}, scene);
  eStopBtn.rotation.x = Math.PI / 2;
  eStopBtn.position.z = d * -0.015; // 베이스 앞면에 부착
  const redMat = new BABYLON.StandardMaterial("redMat", scene);
  redMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  eStopBtn.material = redMat;
  eStopBtn.parent = controlPanel;

  // 작은 조작 버튼 (파워, 시작/정지 스위치 등)
  for(let i=0; i<4; i++) {
    const btn = BABYLON.MeshBuilder.CreateCylinder(`smallBtn${i}`, {diameter: w * 0.03, height: h * 0.02}, scene);
    btn.position = new BABYLON.Vector3(1 + (i*0.5), -0.5, 0); // E-Stop 옆에 가로로 배치
    btn.rotation.x = Math.PI / 2;
    btn.material = darkInternalMat;
    btn.parent = controlPanel;
  }

  // 5. 상단 모니터 및 HMI 암 (Top Monitor & HMI Arm)
  const hmiStation = new BABYLON.TransformNode("hmiStation", scene);
  hmiStation.parent = frameNode;
  hmiStation.position = new BABYLON.Vector3(4, 16.5, -frameSize.depth/2 - 0.5); // 상단 우측 전면

  // 모니터 본체
  const monitorBody = BABYLON.MeshBuilder.CreateBox("monitorBody", {width: w * 0.4, height: h * 0.25, depth: d * 0.02}, scene);
  monitorBody.rotation.x = -Math.PI / 18; // 살짝 위를 향함 (사용자 시야각)
  monitorBody.material = darkInternalMat;
  monitorBody.parent = hmiStation;

  // HMI 모니터 화면 (화면 켜진 푸른빛 + 디테일 텍스처)
  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.38, height: h * 0.22999999999999998}, scene);
  monitorScreen.rotation.x = -Math.PI / 18 + Math.PI/2;
  monitorScreen.position = new BABYLON.Vector3(0, 0, -0.11); // 본체 앞면에 밀착
  monitorScreen.material = screenMat;
  // 텍스처를 적용하고 싶다면 주석 해제 (실제 이미지 텍스처 필요)
  // monitorScreen.material.diffuseTexture = new BABYLON.Texture("path/to/your/mes_ui_texture.png", scene);
  // monitorScreen.material.emissiveTexture = monitorScreen.material.diffuseTexture;
  // monitorScreen.material.emissiveTextureLevel = 1.0;
  monitorScreen.parent = hmiStation;

  // 키보드 트레이
  const keyboardTray = BABYLON.MeshBuilder.CreateBox("keyboardTray", {width: w * 0.35, height: h * 0.005, depth: d * 0.15}, scene);
  keyboardTray.position.y = h * -0.15;
  keyboardTray.position.z = d * -0.1; // 앞으로 길게 돌출
  keyboardTray.rotation.x = Math.PI / 12; // 살짝 앞쪽으로 꺾인 각도
  keyboardTray.material = darkInternalMat;
  keyboardTray.parent = hmiStation;

  // 6. 타워 램프 (Tower Light - 우측 상단)
  const pole = BABYLON.MeshBuilder.CreateCylinder("pole", {diameter: w * 0.015, height: h * 0.15}, scene);
  pole.position = new BABYLON.Vector3(4.5, 16.25, 0);
  pole.material = metallicFrameMat;
  pole.parent = frameNode;

  towerMatDetails.forEach((c, index) => {
    const mat = new BABYLON.StandardMaterial(c.name + "TMat", scene);
    mat.diffuseColor = c.col;
    mat.emissiveColor = c.col; // 자체 발광
    
    const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "TLight", {diameter: w * 0.04, height: h * 0.025}, scene);
    light.position = new BABYLON.Vector3(4.5, 16.5 + (index * 0.3), 0);
    light.material = mat;
    light.parent = frameNode;
  });
};