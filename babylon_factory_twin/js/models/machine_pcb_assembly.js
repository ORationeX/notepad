window.buildPcbAssemblyModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 메탈릭 프레임 (회색)
  const metallicFrameMat = new BABYLON.StandardMaterial("metallicFrameMat", scene);
  metallicFrameMat.diffuseColor = new BABYLON.Color3(0.65, 0.65, 0.68);
  metallicFrameMat.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);

  // 상부 작업 챔버 내부 및 기구물 (어두운 회색)
  const darkInternalMat = new BABYLON.StandardMaterial("darkInternalMat", scene);
  darkInternalMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.18);

  // 전면 관찰창 (투명 아크릴)
  const glassMat = new BABYLON.StandardMaterial("glassMat", scene);
  glassMat.diffuseColor = new BABYLON.Color3(0.8, 0.85, 0.9);
  glassMat.alpha = 0.3; // 반투명
  glassMat.backFaceCulling = false;

  // 좌측 상단 녹색 자재 롤 (prominent green spool)
  const greenRollMat = new BABYLON.StandardMaterial("greenRollMat", scene);
  greenRollMat.diffuseColor = new BABYLON.Color3(0.2, 0.6, 0.2); // 선명한 녹색

  // 중앙 노즐 툴 몸체 (노란색/오렌지색 계열)
  const toolMat = new BABYLON.StandardMaterial("toolMat", scene);
  toolMat.diffuseColor = new BABYLON.Color3(0.9, 0.7, 0.1);

  // 우측 HMI 모니터 화면 (빛나는 파란색 화면)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.4, 0.7);
  screenMat.diffuseColor = new BABYLON.Color3(0, 0, 0);

  // 하부 수납/제어부 (파란색 서랍 등 포인트)
  const bluePanelMat = new BABYLON.StandardMaterial("bluePanelMat", scene);
  bluePanelMat.diffuseColor = new BABYLON.Color3(0.1, 0.3, 0.6); // 이미지의 하부 파란색 수납함 색상

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("pcbAssemblyFrame", scene);
  frameNode.parent = machineMesh;

  const frameSize = { width: 10, height: 18, depth: 7 }; // 장비 전체 스케일

  // 2. 외부 인클로저 (External Enclosure)
  // 하부 제어반 캐비닛 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameSize.width, height: h * 0.6, depth: frameSize.depth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = metallicFrameMat;
  baseCabinet.parent = frameNode;

  // 상부 작업 챔버 메인 프레임 (Upper Chamber Frame)
  const upperFrame = BABYLON.MeshBuilder.CreateBox("upperFrame", {width: frameSize.width, height: h * 1.2, depth: frameSize.depth}, scene);
  upperFrame.position.y = h * 1.2;
  upperFrame.material = darkInternalMat;
  upperFrame.parent = frameNode;
  upperFrame.isVisible = false; // 프레임 외형만 잡고 내부는 비움

  // 수직 지지 기둥 (Pillars - 4모서리)
  const pillarDetails = [
    {x: -4.75, z: -3.25}, {x: 4.75, z: -3.25},
    {x: -4.75, z: 3.25}, {x: 4.75, z: 3.25}
  ];
  pillarDetails.forEach((pos, index) => {
    const pillar = BABYLON.MeshBuilder.CreateBox(`pillar_${index}`, {width: w * 0.05, height: h * 1.2, depth: d * 0.05}, scene);
    pillar.position = new BABYLON.Vector3(pos.x, 12, pos.z);
    pillar.material = metallicFrameMat;
    pillar.parent = frameNode;
  });

  // 상단 덮개 (Top Cover)
  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: frameSize.width, height: h * 0.05, depth: frameSize.depth}, scene);
  topCover.position.y = h * 1.775;
  topCover.material = metallicFrameMat;
  topCover.parent = frameNode;

  // 3. 전면 도어 및 관찰창 (Front Door & Window)
  // 투명 유리창 패널 (챔버 내 기구물이 보이도록)
  const frontGlass = BABYLON.MeshBuilder.CreateBox("frontGlass", {width: w * 0.9, height: h * 1.15, depth: d * 0.01}, scene);
  frontGlass.position = new BABYLON.Vector3(0, 12, -frameSize.depth/2 - 0.05);
  frontGlass.material = glassMat;
  frontGlass.parent = frameNode;

  // 가로 지지대 및 손잡이 디테일 (은색)
  const frontBar = BABYLON.MeshBuilder.CreateBox("frontBar", {width: w * 0.9, height: h * 0.015, depth: d * 0.02}, scene);
  frontBar.position = new BABYLON.Vector3(0, 9.5, -frameSize.depth/2 - 0.1);
  frontBar.material = metallicFrameMat;
  frontBar.parent = frameNode;

  const handleDetails = [ {x: -2}, {x: 2} ]; // 수직 손잡이 2개
  handleDetails.forEach((pos, index) => {
    const handle = BABYLON.MeshBuilder.CreateCylinder(`frontHandle_${index}`, {diameter: w * 0.01, height: h * 0.1}, scene);
    handle.position = new BABYLON.Vector3(pos.x, 10, -frameSize.depth/2 - 0.2);
    handle.material = metallicFrameMat;
    handle.parent = frameNode;
  });

  // 4. 내부 갠트리 및 조립 노즐 (Internal Gantry & Nozzle Tool)
  // X-Y 축 이송 갠트리 시스템 전체
  const gantrySystem = new BABYLON.TransformNode("gantrySystem", scene);
  gantrySystem.parent = frameNode;
  gantrySystem.position.y = h * 1.2;

  // 상단 X축 가이드 레일
  const xRail = BABYLON.MeshBuilder.CreateBox("xRail", {width: w * 0.8, height: h * 0.05, depth: d * 0.08}, scene|;
  xRail.position.y = h * 0.5;
  xRail.material = darkInternalMat;
  xRail.parent = gantrySystem;

  // X축 이동 캐리지 및 Z축 정렬 헤드 (카메라/렌즈 조립 툴)
  const headBlock = new BABYLON.TransformNode("alignToolHead", scene);
  headBlock.parent = gantrySystem;
  headBlock.position = new BABYLON.Vector3(1, 4, 0); // 이미지의 오른쪽 툴 위치

  // 노즐 툴 몸체 (노란색/오렌지색)
  const toolBody = BABYLON.MeshBuilder.CreateCylinder("toolBody", {diameter: w * 0.08, height: h * 0.2}, scene);
  toolBody.material = toolMat;
  toolBody.parent = headBlock;

  // 노즐 팁
  const nozzleTip = BABYLON.MeshBuilder.CreateCylinder("nozzleTip", {diameter: w * 0.01, height: h * 0.05}, scene);
  nozzleTip.position.y = h * -0.125; // 확장 튜브 하단
  nozzleTip.material = darkInternalMat;
  nozzleTip.parent = headBlock;

  // 5. 핵심 특징: 좌측 자재 롤 (Prominent Green Material Spool)
  const spoolNode = new BABYLON.TransformNode("greenSpoolNode", scene);
  spoolNode.parent = frameNode;
  spoolNode.position = new BABYLON.Vector3(-4, 15, -2.5); // 상부 챔버 좌측 전면

  // 녹색 플렉서블 자재 롤 (이미지에서 가장 눈에 띄는 포인트)
  const greenSpool = BABYLON.MeshBuilder.CreateCylinder("greenSpool", {diameter: w * 0.2, height: h * 0.08}, scene);
  greenSpool.rotation.x = Math.PI / 2; // 가로로 눕힘
  greenSpool.material = greenRollMat;
  greenSpool.parent = spoolNode;

  // Spindle 거치대 (메탈릭 실린더)
  const spindle = BABYLON.MeshBuilder.CreateCylinder("spindle", {diameter: w * 0.03, height: h * 0.15}, scene);
  spindle.rotation.x = Math.PI / 2;
  spindle.material = metallicFrameMat;
  spindle.parent = spoolNode;

  // 6. 우측 수직 제어반 (Right Side Control Panel)
  const panelFrame = BABYLON.MeshBuilder.CreateBox("panelFrame", {width: w * 0.22000000000000003, height: h * 1, depth: d * 0.1}, scene);
  panelFrame.position = new BABYLON.Vector3(6, 11, -2); // 우측 프레임에 부착
  panelFrame.material = metallicFrameMat;
  panelFrame.parent = frameNode;

  // HMI 모니터 화면 (화면 켜진 푸른빛)
  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.2, height: h * 0.15}, scene);
  monitorScreen.position = new BABYLON.Vector3(6, 14, -2.55); // 프레임 앞면에 밀착
  monitorScreen.material = screenMat;
  monitorScreen.parent = frameNode;

  // 비상 정지 버튼 (E-Stop - 큼직한 빨간색 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateSphere("eStopBase", {diameter: w * 0.08, segments: 16}, scene);
  eStopBase.scaling.z = 0.2; // 납작하게 만들어 버튼 형태
  eStopBase.position = new BABYLON.Vector3(6, 12, -2.5); // 화면 하단
  const yellowMat = new BABYLON.StandardMaterial("yellowMat", scene);
  yellowMat.diffuseColor = BABYLON.Color3.Yellow();
  eStopBase.material = yellowMat;
  eStopBase.parent = frameNode;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.04, height: h * 0.03}, scene);
  eStopBtn.position = new BABYLON.Vector3(6, 12, -2.6); // 돌출된 빨간 버튼
  eStopBtn.rotation.x = Math.PI / 2; // 가로로 눕힘
  const redMat = new BABYLON.StandardMaterial("redMat", scene);
  redMat.diffuseColor = BABYLON.Color3.Red();
  eStopBtn.material = redMat;
  eStopBtn.parent = frameNode;

  // 작은 조작 버튼들
  for(let i=0; i<3; i++) {
    const btn = BABYLON.MeshBuilder.CreateCylinder(`panelBtn${i}`, {diameter: w * 0.02, height: h * 0.015}, scene);
    btn.position = new BABYLON.Vector3(5.7 + (i*0.3), 11, -2.5);
    btn.rotation.x = Math.PI / 2;
    btn.material = metallicFrameMat;
    btn.parent = frameNode;
  }

  // 7. 하부 세부 요소 (Lower Details - 파란색 서랍 등)
  // 전면 하단 파란색 수납함/서랍 (04 이미지 포인트)
  const blueDrawer = BABYLON.MeshBuilder.CreateBox("blueDrawer", {width: w * 0.35, height: h * 0.12, depth: d * 0.01}, scene);
  blueDrawer.position = new BABYLON.Vector3(0, 3, -FrameSize.depth/2 - 0.05); // 중앙 전면 밀착
  blueDrawer.material = bluePanelMat;
  blueDrawer.parent = frameNode;

  // 우측 하단 금속 도어/패널 라인 (손잡이)
  const darkTrimPanel = BABYLON.MeshBuilder.CreateBox("darkTrimPanel", {width: w * 0.4, height: h * 0.3, depth: d * 0.01}, scene);
  darkTrimPanel.position = new BABYLON.Vector3(3.5, 3, -frameSize.depth/2 - 0.05); // 오른쪽 수직 패널
  darkTrimPanel.material = darkInternalMat;
  darkTrimPanel.parent = frameNode;
};