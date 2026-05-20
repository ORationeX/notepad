window.buildUltrasonicCleaningModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 메탈릭 프레임 (회색)
  const metallicFrameMat = new BABYLON.StandardMaterial("metallicFrameMat", scene);
  metallicFrameMat.diffuseColor = new BABYLON.Color3(0.7, 0.73, 0.75);
  metallicFrameMat.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);

  // 내부 기구물 및 어두운 부품 (검은색)
  const darkInternalMat = new BABYLON.StandardMaterial("darkInternalMat", scene);
  darkInternalMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.18);

  // 공압 튜브용 재질 (파란색)
  const blueTubeMat = new BABYLON.StandardMaterial("blueTubeMat", scene);
  blueTubeMat.diffuseColor = new BABYLON.Color3(0.1, 0.4, 0.8);

  // 손잡이 및 금속 부품
  const metalToolMat = new BABYLON.StandardMaterial("metalToolMat", scene);
  metalToolMat.diffuseColor = new BABYLON.Color3(0.75, 0.75, 0.75);

  // 버튼 및 램프 색상
  const redMat = new BABYLON.StandardMaterial("redMat", scene);
  redMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  const greenMat = new BABYLON.StandardMaterial("greenMat", scene);
  greenMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);
  greenMat.emissiveColor = new BABYLON.Color3(0.1, 0.5, 0.1);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("ultrasonicMachineFrame", scene);
  frameNode.parent = machineMesh;

  const frameSize = { width: 14, height: 18, depth: 8 };

  // 2. 외부 프레임 및 캐비닛 (Base & Body)
  // 하부 제어반 캐비닛 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameSize.width, height: h * 0.6, depth: frameSize.depth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = metallicFrameMat;
  baseCabinet.parent = frameNode;

  // 상부 작업 챔버 메인 프레임 (Upper Chamber Frame)
  const chamberFrame = BABYLON.MeshBuilder.CreateBox("chamberFrame", {width: frameSize.width, height: h * 1.2, depth: frameSize.depth}, scene);
  chamberFrame.position.y = h * 1.2;
  chamberFrame.material = metallicFrameMat;
  chamberFrame.parent = frameNode;
  chamberFrame.isVisible = false; // 프레임 외형만 잡고 내부는 비움

  // 수직 지지 기둥 (Pillars - 4모서리)
  const beamDetails = [
    {x: -6.75, z: -3.75}, {x: 6.75, z: -3.75},
    {x: -6.75, z: 3.75}, {x: 6.75, z: 3.75}
  ];
  beamDetails.forEach(beam => {
    const sBeam = BABYLON.MeshBuilder.CreateBox("sBeam", {width: w * 0.05, height: h * 1.2, depth: d * 0.05}, scene);
    sBeam.position = new BABYLON.Vector3(beam.x, 12, beam.z);
    sBeam.material = metallicFrameMat;
    sBeam.parent = frameNode;
  });

  // 상단 덮개 (Top Cover)
  const topCover = BABYLON.MeshBuilder.CreateBox("topCover", {width: frameSize.width, height: h * 0.05, depth: frameSize.depth}, scene);
  topCover.position.y = h * 1.775;
  topCover.material = metallicFrameMat;
  topCover.parent = frameNode;

  // 3. 수조 및 갠트리 (Baths & Gantry)
  const gantrySystem = new BABYLON.TransformNode("gantrySystem", scene);
  gantrySystem.parent = frameNode;
  gantrySystem.position.y = h * 1.2;

  // 상단 X축 갠트리 빔
  const xGantry = BABYLON.MeshBuilder.CreateBox("xGantry", {width: w * 1.2, height: h * 0.05, depth: d * 0.08}, scene);
  xGantry.position.y = h * 0.55;
  xGantry.position.z = d * -0.05;
  xGantry.material = darkInternalMat;
  xGantry.parent = gantrySystem;

  // 수조 (Baths - 일렬로 늘어선 여러 개의 수조)
  const bathDetails = [
      { name: "bath0", x: -5 }, { name: "bath1", x: -2.5 }, { name: "bath2", x: 0 }, { name: "bath3", x: 2.5 }, { name: "bath4", x: 5 }
  ];
  bathDetails.forEach((bath, index) => {
      const b = BABYLON.MeshBuilder.CreateBox(bath.name, {width: w * 0.22000000000000003, height: h * 0.08, depth: d * 0.5}, scene);
      b.position.x = bath.x;
      b.position.y = h * -0.45999999999999996; // 상부 챔버 바닥 바로 위
      b.material = darkInternalMat;
      b.parent = frameNode;
  });

  // X축 이동 캐리지 및 Z축 세정 툴 (카메라/렌즈 세정 툴)
  const alignToolNode = new BABYLON.TransformNode("alignToolNode", scene);
  alignToolNode.position = new BABYLON.Vector3(1, 5.5, -0.5); // 이미지의 오른쪽 툴 위치
  alignToolNode.parent = gantrySystem;

  const carriage = BABYLON.MeshBuilder.CreateBox("carriage", {width: w * 0.15, height: h * 0.1, depth: d * 0.15}, scene);
  carriage.material = darkInternalMat;
  carriage.parent = alignToolNode;

  const zAxis = BABYLON.MeshBuilder.CreateCylinder("zAxis", {diameter: w * 0.06, height: h * 0.6}, scene);
  zAxis.position.y = h * -0.25;
  zAxis.material = darkInternalMat;
  zAxis.parent = alignToolNode;

  const toolHead = BABYLON.MeshBuilder.CreateBox("toolHead", {width: w * 0.12, height: h * 0.2, depth: d * 0.12}, scene);
  toolHead.position.y = h * -0.6;
  toolHead.material = metalToolMat;
  toolHead.parent = alignToolNode;

  // 파란색 공압 튜브들 (시각적 포인트)
  for(let i=0; i<3; i++) {
    const tube = BABYLON.MeshBuilder.CreateCylinder(`tube${i}`, {diameter: w * 0.01, height: h * 0.2}, scene);
    tube.position.x = w * -0.18 + (i * 0.2);
    tube.position.y = h * 1.05;
    tube.position.z = d * -0.15;
    tube.rotation.z = Math.PI / 6;
    tube.material = blueTubeMat;
    tube.parent = frameNode;
  }

  // 4. 전면 제어 패널 (Front Control Panel)
  const controlPanel = BABYLON.MeshBuilder.CreateBox("controlPanel", {width: frameSize.width, height: h * 0.15, depth: d * 0.12}, scene);
  controlPanel.position.y = h * 0.65;
  controlPanel.position.z = -frameSize.depth/2 - 0.2;
  controlPanel.rotation.x = Math.PI / 12; // 살짝 기울어진 디자인
  const whiteMat = new BABYLON.StandardMaterial("whiteMat", scene);
  whiteMat.diffuseColor = new BABYLON.Color3(0.85, 0.85, 0.85);
  controlPanel.material = whiteMat;
  controlPanel.parent = frameNode;

  // 비상 정지 버튼 (노란 베이스 + 빨간 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateCylinder("eStopBase", {diameter: w * 0.12, height: h * 0.01}, scene);
  eStopBase.position.x = w * -0.6;
  eStopBase.position.y = h * 0.6599999999999999;
  eStopBase.position.z = -frameSize.depth/2 - 0.8;
  eStopBase.rotation.x = Math.PI / 12;
  const yellowMat = new BABYLON.StandardMaterial("yellowMat", scene);
  yellowMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  eStopBase.material = yellowMat;
  eStopBase.parent = frameNode;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.03}, scene);
  eStopBtn.position.x = w * -0.6;
  eStopBtn.position.y = h * 0.67;
  eStopBtn.position.z = -frameSize.depth/2 - 0.85;
  eStopBtn.rotation.x = Math.PI / 12 + Math.PI/2;
  eStopBtn.material = redMat;
  eStopBtn.parent = frameNode;

  // "HANKUK ULTRASONIC" 로고 텍스트 (텍스트 텍스처로 단순 구현)
  const logoText = BABYLON.MeshBuilder.CreatePlane("logoText", {width: w * 0.4, height: h * 0.1}, scene);
  logoText.position.x = 0;
  logoText.position.y = h * 0.67;
  logoText.position.z = -frameSize.depth/2 - 0.7;
  logoText.rotation.x = Math.PI / 12;
  // 텍스트를 적용하고 싶다면 주석 해제 (실제 이미지 텍스처 필요)
  // logoText.material.diffuseTexture = new BABYLON.Texture("path/to/your/logo_texture.png", scene);
  // logoText.material.diffuseTexture.hasAlpha = true;
  logoText.parent = frameNode;

  // 5. 하단 배관 및 펌프 (Lower Piping & Pumps)
  const lowerDetails = new BABYLON.TransformNode("lowerDetails", scene);
  lowerDetails.parent = frameNode;
  lowerDetails.position.y = h * 0.05;

  const pipeDetails = [
      { name: "pipe0", diameter: 0.3, height: 4, x: -5, y: 1 }, { name: "pipe1", diameter: 0.3, height: 4, x: -3.5, y: 1 },
      { name: "pipe2", diameter: 0.3, height: 4, x: 5, y: 1 }
  ];
  pipeDetails.forEach(pipe => {
      const p = BABYLON.MeshBuilder.CreateCylinder(pipe.name, {diameter: pipe.diameter, height: pipe.height}, scene);
      p.position.x = pipe.x;
      p.position.y = pipe.y;
      p.material = metallicFrameMat;
      p.parent = lowerDetails;
  });

  const pump = BABYLON.MeshBuilder.CreateBox("pump", {width: w * 0.25, height: h * 0.12, depth: d * 0.3}, scene);
  pump.position.x = w * 0.2; pumping.position.y = h * 0.12;
  pump.material = darkInternalMat;
  pump.parent = lowerDetails;

  const filterHousing = BABYLON.MeshBuilder.CreateCylinder("filterHousing", {diameter: w * 0.08, height: h * 0.25}, scene);
  filterHousing.position.x = w * -0.25; filterHousing.position.y = h * 0.1;
  filterHousing.material = darkInternalMat;
  filterHousing.parent = lowerDetails;
};