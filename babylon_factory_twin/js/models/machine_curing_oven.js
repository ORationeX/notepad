window.buildCuringOvenModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 프레임 (밝은 회색/흰색)
  const mainFrameMat = new BABYLON.StandardMaterial("mainFrameMat", scene);
  mainFrameMat.diffuseColor = new BABYLON.Color3(0.75, 0.75, 0.78);

  // 하단 기구부 (스테인리스 스틸 느낌)
  const stainlessMat = new BABYLON.StandardMaterial("stainlessMat", scene);
  stainlessMat.diffuseColor = new BABYLON.Color3(0.6, 0.6, 0.65);
  stainlessMat.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);
  stainlessMat.roughness = 0.3; // 부드러운 반사

  // 내부 어두운 부분 및 기구물
  const darkMat = new BABYLON.StandardMaterial("darkMat", scene);
  darkMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.1);

  // HMI 모니터 화면 (이미지의 녹색 UI 느낌)
  const hmiScreenMat = new BABYLON.StandardMaterial("hmiScreenMat", scene);
  hmiScreenMat.emissiveColor = new BABYLON.Color3(0.1, 0.5, 0.1); // 자체 발광하는 녹색 UI
  hmiScreenMat.diffuseColor = new BABYLON.Color3(0.1, 0.3, 0.1);

  // 경화 챔버 내부 (열기/UV 빛 표현)
  const chamberInternalMat = new BABYLON.StandardMaterial("chamberInternalMat", scene);
  chamberInternalMat.emissiveColor = new BABYLON.Color3(0.8, 0.6, 0.2); // 따뜻한 열기 표현
  
  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("curingOvenFrame", scene);
  frameNode.parent = machineMesh;

  const ovenSize = { width: 10, height: 18, depth: 8 };

  // 2. 외부 본체 (Main Enclosure)
  // 하부 캐비닛 (Base Cabinet - 제어부 및 파워 랙)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: ovenSize.width, height: h * 0.6, depth: ovenSize.depth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = mainFrameMat;
  baseCabinet.parent = frameNode;

  // 상부 경화 챔버 영역 (Upper Chamber Area)
  const upperChamber = BABYLON.MeshBuilder.CreateBox("upperChamber", {width: ovenSize.width, height: h * 1.2, depth: ovenSize.depth}, scene);
  upperChamber.position.y = h * 1.2;
  upperChamber.material = mainFrameMat;
  upperChamber.parent = frameNode;

  // 3. 전면 조작 및 관찰부 (Front HMI & Viewport)
  // HMI 모니터 암 (이미지의 모니터 지지 기둥)
  const monitorArm = BABYLON.MeshBuilder.CreateCylinder("monitorArm", {diameter: w * 0.02, height: h * 0.4}, scene);
  monitorArm.position.x = -(ovenSize.width / 2) + 0.8;
  monitorArm.position.y = h * 1.2;
  monitorArm.position.z = -(ovenSize.depth / 2) - 0.5; // 앞으로 돌출
  monitorArm.material = stainlessMat;
  monitorArm.parent = frameNode;

  // HMI 모니터 본체
  const monitorBody = BABYLON.MeshBuilder.CreateBox("monitorBody", {width: w * 0.4, height: h * 0.3, depth: d * 0.02}, scene);
  monitorBody.position.x = -(ovenSize.width / 2) + 0.8;
  monitorBody.position.y = h * 1.4;
  monitorBody.position.z = -(ovenSize.depth / 2) - 0.6;
  monitorBody.rotation.y = Math.PI / 18; // 사용자를 향해 살짝 틀어짐
  monitorBody.material = darkMat;
  monitorBody.parent = frameNode;

  // HMI 모니터 화면 (녹색 UI)
  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.38, height: h * 0.27999999999999997}, scene);
  monitorScreen.position.x = -(ovenSize.width / 2) + 0.8;
  monitorScreen.position.y = h * 1.4;
  monitorScreen.position.z = -(ovenSize.depth / 2) - 0.71; // 본드 앞면에 밀착
  monitorScreen.rotation.y = Math.PI / 18 + Math.PI/2;
  monitorScreen.material = hmiScreenMat;
  monitorScreen.parent = frameNode;

  // 키보드/마우스 트레이 (HMI 아래)
  const kbdTray = BABYLON.MeshBuilder.CreateBox("kbdTray", {width: w * 0.4, height: h * 0.01, depth: d * 0.15}, scene);
  kbdTray.position.x = -(ovenSize.width / 2) + 1.2;
  kbdTray.position.y = h * 1.2;
  kbdTray.position.z = -(ovenSize.depth / 2) - 1; // 앞으로 길게 돌출
  kbdTray.rotation.x = Math.PI / 24; // 살짝 앞쪽으로 꺾인 각도
  kbdTray.material = darkMat;
  kbdTray.parent = frameNode;

  // 전면 챔버 관찰창 (틴팅 유리 느낌)
  const darkGlassMat = new BABYLON.StandardMaterial("darkGlassMat", scene);
  darkGlassMat.diffuseColor = new BABYLON.Color3(0.05, 0.05, 0.05);
  darkGlassMat.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);
  darkGlassMat.alpha = 0.85; // 내부가 거의 안 보이는 짙은 틴팅

  const chamberWindow = BABYLON.MeshBuilder.CreateBox("chamberWindow", {width: w * 0.6, height: h * 0.55, depth: d * 0.01}, scene);
  chamberWindow.position.y = h * 1.15;
  chamberWindow.position.z = -(ovenSize.depth / 2) - 0.05; // 앞으로 살짝 돌출
  chamberWindow.material = darkGlassMat;
  chamberWindow.parent = frameNode;

  // 도어 가로 손잡이 (은색)
  const handle = BABYLON.MeshBuilder.CreateBox("handle", {width: w * 0.5, height: h * 0.015, depth: d * 0.025}, scene);
  handle.position.y = h * 0.9;
  handle.position.z = -(ovenSize.depth / 2) - 0.2;
  handle.material = stainlessMat;
  handle.parent = frameNode;

  // 4. 내부 경화 시스템 (Internal Curing System)
  // 자재가 놓이는 하단 스테이지
  const internalStage = BABYLON.MeshBuilder.CreateBox("internalStage", {width: w * 0.8, height: h * 0.02, depth: d * 0.6}, scene);
  internalStage.position.y = h * 0.61; // 베이스 캐비닛 바로 위
  internalStage.material = stainlessMat;
  internalStage.parent = frameNode;

  // 챔버 내부 벽 (열기 표현)
  const chamberInternal = BABYLON.MeshBuilder.CreateBox("chamberInternal", {width: w * 0.75, height: h * 0.5, depth: d * 0.55}, scene);
  chamberInternal.position.y = h * 1.15;
  chamberInternal.material = chamberInternalMat;
  chamberInternal.parent = frameNode;

  // 상단 UV/열 경화 유닛 (실린더 어레이)
  for(let i=0; i<3; i++) {
    const curingUnit = BABYLON.MeshBuilder.CreateCylinder(`curingUnit_${i}`, {diameter: w * 0.08, height: h * 0.1}, scene);
    curingUnit.position.x = w * -0.25 + (i * 2.5);
    curingUnit.position.y = h * 1.35;
    curingUnit.position.z = 0;
    curingUnit.rotation.x = Math.PI / 2;
    curingUnit.material = darkMat;
    curingUnit.parent = frameNode;
  }

  // 5. 타워 램프 (Tower Light - 우측 상단)
  const towerPole = BABYLON.MeshBuilder.CreateCylinder("towerPole", {diameter: w * 0.015, height: h * 0.1}, scene);
  towerPole.position.x = (ovenSize.width / 2) - 0.5;
  towerPole.position.y = h * 1.85;
  towerPole.position.z = 0;
  towerPole.material = darkMat;
  towerPole.parent = frameNode;

  const colors = [
    { name: "grn", col: new BABYLON.Color3(0, 1, 0), y: 19 },
    { name: "yel", col: new BABYLON.Color3(1, 1, 0), y: 19.3 },
    { name: "red", col: new BABYLON.Color3(1, 0, 0), y: 19.6 }
  ];

  colors.forEach(c => {
    const mat = new BABYLON.StandardMaterial(c.name + "TMat", scene);
    mat.diffuseColor = c.col;
    mat.emissiveColor = c.col;
    const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "TLight", {diameter: w * 0.04, height: h * 0.025}, scene);
    light.position.x = (ovenSize.width / 2) - 0.5;
    light.position.y = c.y;
    light.position.z = 0;
    light.material = mat;
    light.parent = frameNode;
  });
};