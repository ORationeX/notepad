window.buildFinalOpticalTesterModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 프레임 (밝은 메탈릭 회색)
  const metallicFrameMat = new BABYLON.StandardMaterial("metallicFrameMat", scene);
  metallicFrameMat.diffuseColor = new BABYLON.Color3(0.7, 0.73, 0.75);
  metallicFrameMat.specularColor = new BABYLON.Color3(0.9, 0.9, 0.9);
  metallicFrameMat.roughness = 0.3; // 약간 부드러운 금속 광택

  // 내부 기구물 및 하단 베이스 (어두운 회색/검정)
  const darkInternalMat = new BABYLON.StandardMaterial("darkInternalMat", scene);
  darkInternalMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.15);

  // 전면/측면 관찰창 (투명 유리/아크릴)
  const glassPanelMat = new BABYLON.StandardMaterial("glassPanelMat", scene);
  glassPanelMat.diffuseColor = new BABYLON.Color3(0.8, 0.85, 0.9);
  glassPanelMat.alpha = 0.4; // 반투명
  glassPanelMat.backFaceCulling = false; // 양면 렌더링

  // 모니터 화면 및 내부 조명 (빛나는 파란색/녹색 UI 느낌)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.4, 0.7); // 자체 발광
  screenMat.diffuseColor = new BABYLON.Color3(0, 0, 0);

  // 손잡이 및 노즐 금속 재질
  const metalToolMat = new BABYLON.StandardMaterial("metalToolMat", scene);
  metalToolMat.diffuseColor = new BABYLON.Color3(0.8, 0.8, 0.82);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("opticalTesterFrame", scene);
  frameNode.parent = machineMesh;

  const frameSize = { width: 12, height: 18, depth: 8 };

  // 2. 외부 본체 (Main Enclosure)
  // 하부 캐비닛 및 베이스 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameSize.width, height: h * 0.6, depth: frameSize.depth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = darkInternalMat;
  baseCabinet.parent = frameNode;

  // 상부 작업 챔버 메인 프레임 (Upper Chamber Frame)
  const chamberFrame = BABYLON.MeshBuilder.CreateBox("chamberFrame", {width: frameSize.width, height: h * 1.2, depth: frameSize.depth}, scene);
  chamberFrame.position.y = h * 1.2;
  chamberFrame.material = metallicFrameMat;
  chamberFrame.parent = frameNode;
  chamberFrame.isVisible = false; // 프레임 외형만 잡고 내부는 비움

  // 수직 지지 기둥 (Pillars - 4모서리)
  const beamWidth = 0.5;
  const beamPositions = [
    {x: -frameSize.width/2 + beamWidth/2, z: -frameSize.depth/2 + beamWidth/2},
    {x: frameSize.width/2 - beamWidth/2, z: -frameSize.depth/2 + beamWidth/2},
    {x: -frameSize.width/2 + beamWidth/2, z: frameSize.depth/2 - beamWidth/2},
    {x: frameSize.width/2 - beamWidth/2, z: frameSize.depth/2 - beamWidth/2}
  ];
  beamPositions.forEach(pos => {
    const pillar = BABYLON.MeshBuilder.CreateBox("pillar", {width: beamWidth, height: h * 1.2, depth: beamWidth}, scene);
    pillar.position = new BABYLON.Vector3(pos.x, 12, pos.z);
    pillar.material = metallicFrameMat;
    pillar.parent = frameNode;
  });

  // 상단 덮개 (Top Cover)
  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: frameSize.width, height: h * 0.05, depth: frameSize.depth}, scene);
  topCover.position.y = h * 1.775;
  topCover.material = metallicFrameMat;
  topCover.parent = frameNode;

  // 3. 관찰창 및 손잡이 (Panels & Handles)
  // 전면 대형 유리 도어
  const frontGlass = BABYLON.MeshBuilder.CreateBox("frontGlass", {width: w * 1.1, height: h * 1, depth: d * 0.01}, scene);
  frontGlass.position = new BABYLON.Vector3(0, 11.5, -frameSize.depth/2 - 0.05);
  frontGlass.material = glassPanelMat;
  frontGlass.parent = frameNode;

  // 도어 수직 손잡이 (좌/우 2개)
  for(let i=0; i<2; i++) {
    const handle = BABYLON.MeshBuilder.CreateCylinder(`frontHandle${i}`, {diameter: w * 0.01, height: h * 0.25}, scene);
    handle.position = new BABYLON.Vector3(i === 0 ? -2 : 2, 9, -frameSize.depth/2 - 0.2);
    handle.material = metalToolMat;
    handle.parent = frameNode;
  }

  // 측면 관찰창 (좌/우)
  for(let i=0; i<2; i++) {
    const sideGlass = BABYLON.MeshBuilder.CreateBox(`sideGlass${i}`, {width: w * 0.01, height: h * 1, depth: d * 0.7}, scene);
    sideGlass.position = new BABYLON.Vector3(i === 0 ? -frameSize.width/2 - 0.05 : frameSize.width/2 + 0.05, 11.5, 0);
    sideGlass.material = glassPanelMat;
    sideGlass.parent = frameNode;
  }

  // 4. 내부 기구물 (Internal Gantry & Stage) - 06_Final_Test.jpg 참조
  // 상단 X축 갠트리 빔
  const xGantry = BABYLON.MeshBuilder.CreateBox("xGantry", {width: w * 1, height: h * 0.08, depth: d * 0.08}, scene);
  xGantry.position = new BABYLON.Vector3(0, 16.5, 0);
  xGantry.material = darkInternalMat;
  xGantry.parent = frameNode;

  // X축 이동 캐리지 및 Z축 정렬 헤드 (카메라/렌즈 검사 툴)
  const alignToolNode = new BABYLON.TransformNode("alignToolNode", scene);
  alignToolNode.position = new BABYLON.Vector3(1, 16.5, 0); // 이미지의 오른쪽 툴 위치
  alignToolNode.parent = frameNode;

  const carriage = BABYLON.MeshBuilder.CreateBox("carriage", {width: w * 0.15, height: h * 0.1, depth: d * 0.15}, scene);
  carriage.material = darkInternalMat;
  carriage.parent = alignToolNode;

  const zAxis = BABYLON.MeshBuilder.CreateCylinder("zAxis", {diameter: w * 0.06, height: h * 0.6}, scene);
  zAxis.position.y = h * -0.25;
  zAxis.material = darkInternalMat;
  zAxis.parent = alignToolNode;

  // 광학 검사 헤드 (Optical Head - 하단 카메라 모양)
  const opticalHead = BABYLON.MeshBuilder.CreateBox("opticalHead", {width: w * 0.12, height: h * 0.2, depth: d * 0.12}, scene);
  opticalHead.position.y = h * -0.6;
  opticalHead.material = metalToolMat;
  opticalHead.parent = alignToolNode;

  const lensNozzle = BABYLON.MeshBuilder.CreateCylinder("lensNozzle", {diameter: w * 0.03, height: h * 0.05}, scene);
  lensNozzle.position.y = h * -0.725;
  lensNozzle.material = darkInternalMat;
  lensNozzle.parent = alignToolNode;

  // 하단 자재 스테이지 및 트레이 (DUT Stage)
  const lowerStage = BABYLON.MeshBuilder.CreateBox("lowerStage", {width: frameSize.width - 2, height: h * 0.02, depth: frameSize.depth - 2}, scene);
  lowerStage.position.y = h * 0.61; // 베이스 캐비닛 바로 위
  lowerStage.material = stainlessMat;
  lowerStage.parent = frameNode;

  // 검사 대상(DUT) 트레이 플레이스홀더
  const dutTray = BABYLON.MeshBuilder.CreateBox("dutTray", {width: w * 0.6, height: h * 0.01, depth: d * 0.4}, scene);
  dutTray.position = new BABYLON.Vector3(0, 6.25, 1);
  dutTray.material = darkInternalMat;
  dutTray.parent = frameNode;

  // 5. 측면 HMI 제어대 (HMI Control Station) - 06_Final_Test.jpg의 오른쪽 모니터
  const hmiStationNode = new BABYLON.TransformNode("hmiStationNode", scene);
  hmiStationNode.position = new BABYLON.Vector3(8.5, 9, -2.5); // 이미지의 오른쪽 앞 위치
  hmiStationNode.rotation.y = -Math.PI / 8; // 사용자를 향해 살짝 틀어짐
  hmiStationNode.parent = frameNode;

  // 모니터 본체
  const monitorBody = BABYLON.MeshBuilder.CreateBox("monitorBody", {width: w * 0.4, height: h * 0.25, depth: d * 0.02}, scene);
  monitorBody.material = darkInternalMat;
  monitorBody.parent = hmiStationNode;

  // 모니터 화면
  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.38, height: h * 0.22999999999999998}, scene);
  monitorScreen.position.z = d * -0.011; // 본체 전면에 밀착
  monitorScreen.material = screenMat;
  monitorScreen.parent = hmiStationNode;

  // 키보드 트레이 (HMI 아래)
  const keyboardTray = BABYLON.MeshBuilder.CreateBox("keyboardTray", {width: w * 0.3, height: h * 0.005, depth: d * 0.15}, scene);
  keyboardTray.position.y = h * -0.15;
  keyboardTray.position.z = d * -0.1; // 앞으로 길게 돌출
  keyboardTray.material = darkInternalMat;
  keyboardTray.parent = hmiStationNode;

  // 6. 타워 램프 (Tower Light - 우측 상단)
  const towerPole = BABYLON.MeshBuilder.CreateCylinder("towerPole", {diameter: w * 0.015, height: h * 0.15}, scene);
  towerPole.position.x = w * 0.525;
  towerPole.position.y = h * 1.85;
  towerPole.position.z = d * 0.2;
  towerPole.material = darkInternalMat;
  towerPole.parent = frameNode;

  const lightColors = [
      { name: "red", col: new BABYLON.Color3(1, 0, 0), yPos: h * 1.98 },
      { name: "yel", col: new BABYLON.Color3(1, 1, 0), yPos: h * 1.95 },
      { name: "grn", col: new BABYLON.Color3(0, 1, 0), yPos: h * 1.92 }
  ];

  lightColors.forEach(c => {
      const mat = new BABYLON.StandardMaterial(c.name + "TMat", scene);
      mat.diffuseColor = c.col;
      mat.emissiveColor = c.col; // 자체 발광
      
      const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "Light", {diameter: w * 0.04, height: h * 0.025}, scene);
      light.position.x = w * 0.525;
      light.position.y = c.yPos;
      light.position.z = d * 0.2;
      light.material = mat;
      light.parent = frameNode;
  });
};