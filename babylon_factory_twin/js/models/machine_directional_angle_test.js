window.buildDirectionalAngleTestModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 하부 캐비닛 및 기본 외관 (흰색/밝은 회색)
  const whiteMat = new BABYLON.StandardMaterial("whiteMat", scene);
  whiteMat.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.92);

  // 알루미늄 프로파일 프레임
  const aluMat = new BABYLON.StandardMaterial("aluMat", scene);
  aluMat.diffuseColor = new BABYLON.Color3(0.7, 0.7, 0.7);
  aluMat.specularColor = new BABYLON.Color3(0.9, 0.9, 0.9);

  // 상부 챔버 투명 창 (아크릴/유리)
  const glassMat = new BABYLON.StandardMaterial("glassMat", scene);
  glassMat.diffuseColor = new BABYLON.Color3(0.8, 0.85, 0.9);
  glassMat.alpha = 0.3; // 투명도
  glassMat.backFaceCulling = false;

  // 내부 기구물 (검은색 지그 등)
  const darkMat = new BABYLON.StandardMaterial("darkMat", scene);
  darkMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.15);

  // 파란색 액추에이터 실린더
  const blueCylMat = new BABYLON.StandardMaterial("blueCylMat", scene);
  blueCylMat.diffuseColor = new BABYLON.Color3(0.1, 0.4, 0.8);

  // 내부 빨간색 검사 조명 (자체 발광)
  const redEmissiveMat = new BABYLON.StandardMaterial("redEmissiveMat", scene);
  redEmissiveMat.diffuseColor = new BABYLON.Color3(1, 0.1, 0.1);
  redEmissiveMat.emissiveColor = new BABYLON.Color3(0.8, 0, 0);

  // 버튼 및 기타 포인트 컬러
  const redBtnMat = new BABYLON.StandardMaterial("redBtnMat", scene);
  redBtnMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  const yellowBtnMat = new BABYLON.StandardMaterial("yellowBtnMat", scene);
  yellowBtnMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  
  // 모니터 화면 (빛나는 UI)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.2, 0.6);

  // 전체 모델을 그룹화할 TransformNode
  const frame = new BABYLON.TransformNode("directionalAngleTestFrame", scene);
  frame.parent = machineMesh;

  const frameWidth = 12;
  const frameDepth = 6;
  const lowerHeight = 5;
  const upperHeight = 6;

  // 2. 하부 캐비닛 (Lower Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameWidth, height: lowerHeight, depth: frameDepth}, scene);
  baseCabinet.position.y = lowerHeight / 2;
  baseCabinet.material = whiteMat;
  baseCabinet.parent = frame;

  // 캐비닛 전면 도어 디테일 (손잡이)
  const handleL = BABYLON.MeshBuilder.CreateBox("handleL", {width: w * 0.01, height: h * 0.1, depth: d * 0.02}, scene);
  handleL.position = new BABYLON.Vector3(-2, lowerHeight / 2, -(frameDepth / 2) - 0.1);
  handleL.material = aluMat;
  handleL.parent = frame;

  const handleR = BABYLON.MeshBuilder.CreateBox("handleR", {width: w * 0.01, height: h * 0.1, depth: d * 0.02}, scene);
  handleR.position = new BABYLON.Vector3(2, lowerHeight / 2, -(frameDepth / 2) - 0.1);
  handleR.material = aluMat;
  handleR.parent = frame;

  // 3. 상부 아크릴 챔버 및 프레임 (Upper Enclosure)
  // 챔버 외곽 투명 박스
  const upperChamber = BABYLON.MeshBuilder.CreateBox("upperChamber", {width: frameWidth - 0.5, height: upperHeight, depth: frameDepth - 1}, scene);
  upperChamber.position.y = lowerHeight + (upperHeight / 2);
  upperChamber.position.z = d * 0.05; // 약간 뒤쪽으로 배치
  upperChamber.material = glassMat;
  upperChamber.parent = frame;

  // 알루미늄 프레임 기둥 (모서리)
  const cornerPositions = [
    {x: -5.6, z: -1.9}, {x: 5.6, z: -1.9},
    {x: -5.6, z: 2.9}, {x: 5.6, z: 2.9}
  ];
  cornerPositions.forEach((pos, idx) => {
    const pillar = BABYLON.MeshBuilder.CreateBox(`pillar_${idx}`, {width: w * 0.03, height: upperHeight, depth: d * 0.03}, scene);
    pillar.position = new BABYLON.Vector3(pos.x, lowerHeight + (upperHeight / 2), pos.z);
    pillar.material = aluMat;
    pillar.parent = frame;
  });

  // 상단 알루미늄 프레임
  const topFrame = BABYLON.MeshBuilder.CreateBox("topFrame", {width: frameWidth - 0.5, height: h * 0.03, depth: frameDepth - 1}, scene);
  topFrame.position = new BABYLON.Vector3(0, lowerHeight + upperHeight, 0.5);
  topFrame.material = aluMat;
  topFrame.parent = frame;

  // 전면 슬라이딩 도어 손잡이 (흰색 둥근 손잡이 2개)
  const doorHandle1 = BABYLON.MeshBuilder.CreateCylinder("doorHandle1", {diameter: w * 0.02, height: h * 0.12}, scene);
  doorHandle1.position = new BABYLON.Vector3(-0.5, lowerHeight + 3, -2.1);
  doorHandle1.material = whiteMat;
  doorHandle1.parent = frame;

  const doorHandle2 = BABYLON.MeshBuilder.CreateCylinder("doorHandle2", {diameter: w * 0.02, height: h * 0.12}, scene);
  doorHandle2.position = new BABYLON.Vector3(0.5, lowerHeight + 3, -2.1);
  doorHandle2.material = whiteMat;
  doorHandle2.parent = frame;

  // 4. 내부 기구물 (Internal Mechanisms)
  // 하판 스테이지
  const innerStage = BABYLON.MeshBuilder.CreateBox("innerStage", {width: frameWidth - 1, height: h * 0.02, depth: frameDepth - 1.5}, scene);
  innerStage.position = new BABYLON.Vector3(0, lowerHeight + 0.1, 0.5);
  innerStage.material = aluMat;
  innerStage.parent = frame;

  // A, B 테스트 지그 (검은색 블록)
  const jigA = BABYLON.MeshBuilder.CreateBox("jigA", {width: w * 0.15, height: h * 0.1, depth: d * 0.15}, scene);
  jigA.position = new BABYLON.Vector3(-2, lowerHeight + 0.6, 0);
  jigA.material = darkMat;
  jigA.parent = frame;

  const jigB = BABYLON.MeshBuilder.CreateBox("jigB", {width: w * 0.15, height: h * 0.1, depth: d * 0.15}, scene);
  jigB.position = new BABYLON.Vector3(2, lowerHeight + 0.6, 0);
  jigB.material = darkMat;
  jigB.parent = frame;

  // 상단 파란색 실린더 (액추에이터)
  const blueActuator = BABYLON.MeshBuilder.CreateCylinder("blueActuator", {diameter: w * 0.08, height: h * 0.3}, scene);
  blueActuator.position = new BABYLON.Vector3(-4, lowerHeight + 4, 0);
  blueActuator.material = blueCylMat;
  blueActuator.parent = frame;

  // 빨간색 검사 조명 (Emissive Red Light)
  const redLightBase = BABYLON.MeshBuilder.CreateBox("redLightBase", {width: w * 0.2, height: h * 0.05, depth: d * 0.05}, scene);
  redLightBase.position = new BABYLON.Vector3(0, lowerHeight + 2, -1);
  redLightBase.material = redEmissiveMat;
  redLightBase.parent = frame;

  // 5. 전면 좌측 조작 패널 (Front Control Panel)
  // 비스듬한 형태의 컨트롤 박스
  const controlPanel = BABYLON.MeshBuilder.CreateBox("controlPanel", {width: w * 0.35, height: h * 0.2, depth: d * 0.2}, scene);
  controlPanel.position = new BABYLON.Vector3(-4, lowerHeight + 0.5, -2.5);
  controlPanel.rotation.x = Math.PI / 6; // 기울어짐
  controlPanel.material = whiteMat;
  controlPanel.parent = frame;

  // 비상 정지 버튼 (노란 베이스 + 큰 빨간 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateBox("eStopBase", {width: w * 0.12, height: h * 0.02, depth: d * 0.12}, scene);
  eStopBase.position = new BABYLON.Vector3(-4.5, lowerHeight + 1.2, -3);
  eStopBase.rotation.x = Math.PI / 6;
  eStopBase.material = yellowBtnMat;
  eStopBase.parent = frame;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.04}, scene);
  eStopBtn.position = new BABYLON.Vector3(-4.5, lowerHeight + 1.3, -3.05);
  eStopBtn.rotation.x = Math.PI / 6 + Math.PI/2;
  eStopBtn.material = redBtnMat;
  eStopBtn.parent = frame;

  // 작은 조작 버튼 (파워, 리셋 등)
  const smallBtn = BABYLON.MeshBuilder.CreateCylinder("smallBtn", {diameter: w * 0.03, height: h * 0.02}, scene);
  smallBtn.position = new BABYLON.Vector3(-3, lowerHeight + 1.4, -3.15);
  smallBtn.rotation.x = Math.PI / 6 + Math.PI/2;
  smallBtn.material = blueCylMat;
  smallBtn.parent = frame;

  // 6. 주변기기 (Peripherals)
  // 측면 모니터 암 및 모니터 (왼쪽)
  const monitorArm = BABYLON.MeshBuilder.CreateBox("monitorArm", {width: w * 0.3, height: h * 0.03, depth: d * 0.03}, scene);
  monitorArm.position = new BABYLON.Vector3(-7, lowerHeight + 2, 0);
  monitorArm.material = aluMat;
  monitorArm.parent = frame;

  const monitor = BABYLON.MeshBuilder.CreateBox("monitor", {width: w * 0.02, height: h * 0.3, depth: d * 0.4}, scene);
  monitor.position = new BABYLON.Vector3(-8.5, lowerHeight + 2, 0);
  monitor.rotation.y = -Math.PI / 8; // 사용자를 향함
  monitor.material = darkMat;
  monitor.parent = frame;

  const screen = BABYLON.MeshBuilder.CreatePlane("screen", {width: w * 0.38, height: h * 0.27999999999999997}, scene);
  screen.position = new BABYLON.Vector3(-8.39, lowerHeight + 2, 0);
  screen.rotation.y = -Math.PI / 8 - Math.PI/2;
  screen.material = screenMat;
  screen.parent = frame;

  // 바코드 스캐너 거치대 (오른쪽 전면)
  const scannerStand = BABYLON.MeshBuilder.CreateCylinder("scannerStand", {diameter: w * 0.01, height: h * 0.2}, scene);
  scannerStand.position = new BABYLON.Vector3(4.5, lowerHeight + 1, -3);
  scannerStand.material = darkMat;
  scannerStand.parent = frame;

  const scannerHead = BABYLON.MeshBuilder.CreateBox("scannerHead", {width: w * 0.05, height: h * 0.05, depth: d * 0.1}, scene);
  scannerHead.position = new BABYLON.Vector3(4.5, lowerHeight + 2, -2.8);
  scannerHead.rotation.x = Math.PI / 4;
  scannerHead.material = darkMat;
  scannerHead.parent = frame;

  // 바코드 프린터 (우측 하단 캐비닛 위)
  const printer = BABYLON.MeshBuilder.CreateBox("printer", {width: w * 0.25, height: h * 0.3, depth: d * 0.35}, scene);
  printer.position = new BABYLON.Vector3(6.5, lowerHeight + 1.5, -0.5);
  printer.material = aluMat;
  printer.parent = frame;

  const printerPanel = BABYLON.MeshBuilder.CreateBox("printerPanel", {width: w * 0.25, height: h * 0.15, depth: d * 0.01}, scene);
  printerPanel.position = new BABYLON.Vector3(6.5, lowerHeight + 2, -2.25);
  printerPanel.rotation.x = Math.PI / 12;
  printerPanel.material = darkMat;
  printerPanel.parent = frame;
};