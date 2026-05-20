window.buildVisionInspectionModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 외관 (화이트/밝은 회색)
  const whiteMat = new BABYLON.StandardMaterial("whiteMat", scene);
  whiteMat.diffuseColor = new BABYLON.Color3(0.92, 0.92, 0.95);

  // 후면 암실 챔버 패널 (무광 검정)
  const darkPanelMat = new BABYLON.StandardMaterial("darkPanelMat", scene);
  darkPanelMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.12);
  darkPanelMat.roughness = 0.8;

  // LED 광원 패널 (매우 밝은 화이트 자체 발광)
  const ledLightMat = new BABYLON.StandardMaterial("ledLightMat", scene);
  ledLightMat.diffuseColor = new BABYLON.Color3(1, 1, 1);
  ledLightMat.emissiveColor = new BABYLON.Color3(0.9, 0.9, 0.9); // 눈부신 광원

  // 금속 기구물 및 거치대 (어두운 금속)
  const metalMat = new BABYLON.StandardMaterial("metalMat", scene);
  metalMat.diffuseColor = new BABYLON.Color3(0.3, 0.3, 0.35);

  // 모니터 화면 (빛나는 화면 - 컬러바 느낌의 밝은 톤)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.8, 0.8, 0.9);

  // 작업대 위 테이프 마킹 영역 (노란색, 파란색)
  const yellowTapeMat = new BABYLON.StandardMaterial("yellowTapeMat", scene);
  yellowTapeMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  yellowTapeMat.emissiveColor = new BABYLON.Color3(0.2, 0.2, 0);

  const blueTapeMat = new BABYLON.StandardMaterial("blueTapeMat", scene);
  blueTapeMat.diffuseColor = new BABYLON.Color3(0.1, 0.3, 0.8);
  blueTapeMat.emissiveColor = new BABYLON.Color3(0, 0.1, 0.2);

  // 비상정지 버튼 (노란 베이스, 빨간 버튼)
  const redBtnMat = new BABYLON.StandardMaterial("redBtnMat", scene);
  redBtnMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("visionInspectionFrame", scene);
  frameNode.parent = machineMesh;

  const width = 14;
  const depth = 6;
  const deskHeight = 5;
  const backPanelHeight = 7;

  // 2. 하부 데스크 및 서랍 (Lower Desk & Drawers)
  const deskBase = BABYLON.MeshBuilder.CreateBox("deskBase", {width: width, height: deskHeight, depth: depth}, scene);
  deskBase.position.y = deskHeight / 2;
  deskBase.material = whiteMat;
  deskBase.parent = frameNode;

  // 전면 서랍 디테일 (음각 느낌을 위해 얇은 박스 덧댐)
  const drawer = BABYLON.MeshBuilder.CreateBox("drawer", {width: w * 0.6, height: h * 0.12, depth: d * 0.01}, scene);
  drawer.position = new BABYLON.Vector3(0, deskHeight - 1, -(depth / 2) - 0.05);
  drawer.material = whiteMat;
  drawer.parent = frameNode;

  const drawerHandle = BABYLON.MeshBuilder.CreateCylinder("drawerHandle", {diameter: w * 0.01, height: h * 0.15}, scene);
  drawerHandle.rotation.z = Math.PI / 2;
  drawerHandle.position = new BABYLON.Vector3(0, deskHeight - 1, -(depth / 2) - 0.15);
  drawerHandle.material = metalMat;
  drawerHandle.parent = frameNode;

  // 작업대 위 가이드 마킹 (노란색/파란색 사각형 라인)
  const tapeZoneY = deskHeight + 0.02; // 데스크 표면 바로 위 (Z-fighting 방지)
  
  const yellowZone = BABYLON.MeshBuilder.CreatePlane("yellowZone", {width: w * 0.35, height: h * 0.2}, scene);
  yellowZone.rotation.x = Math.PI / 2;
  yellowZone.position = new BABYLON.Vector3(-3, tapeZoneY, -1.5);
  yellowZone.material = yellowTapeMat;
  yellowZone.parent = frameNode;
  // 내부를 파내어 테이프 라인처럼 보이게 할 수도 있으나, 여기서는 색상 면으로 단순화

  const blueZone = BABYLON.MeshBuilder.CreatePlane("blueZone", {width: w * 0.35, height: h * 0.2}, scene);
  blueZone.rotation.x = Math.PI / 2;
  blueZone.position = new BABYLON.Vector3(4, tapeZoneY, -1.5);
  blueZone.material = blueTapeMat;
  blueZone.parent = frameNode;

  // 3. 후면 차폐 패널 및 광원 (Back Panel & LED Array)
  // 후면 검은색 패널
  const backPanel = BABYLON.MeshBuilder.CreateBox("backPanel", {width: width - 1, height: backPanelHeight, depth: d * 0.1}, scene);
  backPanel.position = new BABYLON.Vector3(0, deskHeight + (backPanelHeight / 2), (depth / 2) - 0.5);
  backPanel.material = darkPanelMat;
  backPanel.parent = frameNode;

  // 후면 패널을 감싸는 흰색 프레임 (외곽)
  const topFrame = BABYLON.MeshBuilder.CreateBox("topFrame", {width: width, height: h * 0.05, depth: d * 0.12}, scene);
  topFrame.position = new BABYLON.Vector3(0, deskHeight + backPanelHeight + 0.25, (depth / 2) - 0.4);
  topFrame.material = whiteMat;
  topFrame.parent = frameNode;

  const leftFrame = BABYLON.MeshBuilder.CreateBox("leftFrame", {width: w * 0.05, height: backPanelHeight, depth: d * 0.12}, scene);
  leftFrame.position = new BABYLON.Vector3(-(width / 2) + 0.25, deskHeight + (backPanelHeight / 2), (depth / 2) - 0.4);
  leftFrame.material = whiteMat;
  leftFrame.parent = frameNode;

  const rightFrame = BABYLON.MeshBuilder.CreateBox("rightFrame", {width: w * 0.05, height: backPanelHeight, depth: d * 0.12}, scene);
  rightFrame.position = new BABYLON.Vector3((width / 2) - 0.25, deskHeight + (backPanelHeight / 2), (depth / 2) - 0.4);
  rightFrame.material = whiteMat;
  rightFrame.parent = frameNode;

  // 눈부신 정사각형 LED 광원 패널 2개
  const ledSize = 2.5;
  [-1.5, 1.5].forEach((posX, idx) => {
    const ledPanel = BABYLON.MeshBuilder.CreateBox(`ledPanel_${idx}`, {width: ledSize, height: ledSize, depth: d * 0.01}, scene);
    ledPanel.position = new BABYLON.Vector3(posX, deskHeight + 2, (depth / 2) - 1.05);
    ledPanel.material = ledLightMat;
    ledPanel.parent = frameNode;
  });

  // 4. 테스트 지그 (Test Jigs)
  [-1.5, 1.5].forEach((posX, idx) => {
    const jigBase = BABYLON.MeshBuilder.CreateBox(`jigBase_${idx}`, {width: w * 0.2, height: h * 0.04, depth: d * 0.2}, scene);
    jigBase.position = new BABYLON.Vector3(posX, deskHeight + 0.2, (depth / 2) - 1.5);
    jigBase.material = darkPanelMat;
    jigBase.parent = frameNode;

    const jigTop = BABYLON.MeshBuilder.CreateBox(`jigTop_${idx}`, {width: w * 0.1, height: h * 0.02, depth: d * 0.1}, scene);
    jigTop.position = new BABYLON.Vector3(posX, deskHeight + 0.5, (depth / 2) - 1.5);
    jigTop.material = metalMat;
    jigTop.parent = frameNode;
  });

  // 5. 좌측 모니터 및 암 (Left Monitor & Arm)
  const monitorArm = BABYLON.MeshBuilder.CreateBox("monitorArm", {width: w * 0.2, height: h * 0.02, depth: d * 0.02}, scene);
  monitorArm.position = new BABYLON.Vector3(-(width / 2) + 1, deskHeight + 3, (depth / 2) - 1.2);
  monitorArm.material = metalMat;
  monitorArm.parent = frameNode;

  const monitorNode = new BABYLON.TransformNode("monitorNode", scene);
  monitorNode.position = new BABYLON.Vector3(-(width / 2) + 2.5, deskHeight + 3, (depth / 2) - 2);
  monitorNode.rotation.y = Math.PI / 8; // 중앙을 향함
  monitorNode.parent = frameNode;

  const monitorBack = BABYLON.MeshBuilder.CreateBox("monitorBack", {width: w * 0.45, height: h * 0.3, depth: d * 0.02}, scene);
  monitorBack.material = darkPanelMat;
  monitorBack.parent = monitorNode;

  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.43, height: h * 0.27999999999999997}, scene);
  monitorScreen.position.z = d * -0.011;
  monitorScreen.material = screenMat;
  // 실제 컬러바 텍스처를 적용할 수 있는 자리
  // monitorScreen.material.diffuseTexture = new BABYLON.Texture("path/to/colorbar.png", scene);
  // monitorScreen.material.emissiveTexture = monitorScreen.material.diffuseTexture;
  monitorScreen.parent = monitorNode;

  // 6. 우측 바코드 스캐너 및 E-Stop (Right Scanner & Controls)
  // 구스넥 바코드 스캐너 스탠드
  const scannerBase = BABYLON.MeshBuilder.CreateCylinder("scannerBase", {diameter: w * 0.1, height: h * 0.02}, scene);
  scannerBase.position = new BABYLON.Vector3(5, deskHeight + 0.1, 0);
  scannerBase.material = metalMat;
  scannerBase.parent = frameNode;

  const scannerNeck = BABYLON.MeshBuilder.CreateCylinder("scannerNeck", {diameter: w * 0.015, height: h * 0.3}, scene);
  scannerNeck.position = new BABYLON.Vector3(5, deskHeight + 1.5, 0);
  scannerNeck.rotation.x = -Math.PI / 8; // 앞으로 살짝 기울어짐
  scannerNeck.material = metalMat;
  scannerNeck.parent = frameNode;

  const scannerHead = BABYLON.MeshBuilder.CreateBox("scannerHead", {width: w * 0.06, height: h * 0.04, depth: d * 0.12}, scene);
  scannerHead.position = new BABYLON.Vector3(5, deskHeight + 3, -0.6);
  scannerHead.rotation.x = Math.PI / 4; // 아래쪽을 향함
  scannerHead.material = darkPanelMat;
  scannerHead.parent = frameNode;

  // 우측 끝 비상정지 버튼 패널 (노란색 가드 + 빨간 버튼)
  const eStopPanel = BABYLON.MeshBuilder.CreateBox("eStopPanel", {width: w * 0.15, height: h * 0.15, depth: d * 0.15}, scene);
  eStopPanel.position = new BABYLON.Vector3((width / 2) - 1, deskHeight + 0.75, (depth / 2) - 1.5);
  eStopPanel.material = yellowTapeMat;
  eStopPanel.parent = frameNode;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.04}, scene);
  eStopBtn.position = new BABYLON.Vector3((width / 2) - 1, deskHeight + 1.6, (depth / 2) - 1.5);
  eStopBtn.material = redBtnMat;
  eStopBtn.parent = frameNode;
};