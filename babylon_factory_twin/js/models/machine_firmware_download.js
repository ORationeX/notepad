window.buildFirmwareDownloadModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 프레임 (어두운 무광 금속 - 09_FW_Download.jpg의 짙은 회색 베이스)
  const darkMetalMat = new BABYLON.StandardMaterial("darkMetalMat", scene);
  darkMetalMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.18);
  darkMetalMat.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2);
  darkMetalMat.roughness = 0.8; // 무광택 표면

  // 지그 베이스 및 트레이 (검은색)
  const darkJigMat = new BABYLON.StandardMaterial("darkJigMat", scene);
  darkJigMat.diffuseColor = new BABYLON.Color3(0.08, 0.08, 0.1);

  // 미세 포고 핀 (금색/황동색 - 특징적인 포인트)
  const goldPinMat = new BABYLON.StandardMaterial("goldPinMat", scene);
  goldPinMat.diffuseColor = new BABYLON.Color3(0.85, 0.7, 0.1);
  goldPinMat.specularColor = new BABYLON.Color3(1, 0.9, 0.5);

  // 공압 튜브 (파란색)
  const blueTubeMat = new BABYLON.StandardMaterial("blueTubeMat", scene);
  blueTubeMat.diffuseColor = new BABYLON.Color3(0.1, 0.4, 0.8);

  // 버튼 및 램프 컬러 (자체 발광 포함)
  const redBtnMat = new BABYLON.StandardMaterial("redBtnMat", scene);
  redBtnMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  redBtnMat.emissiveColor = new BABYLON.Color3(0.4, 0, 0);

  const greenBtnMat = new BABYLON.StandardMaterial("greenBtnMat", scene);
  greenBtnMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);
  greenBtnMat.emissiveColor = new BABYLON.Color3(0, 0.4, 0);

  const yellowBtnMat = new BABYLON.StandardMaterial("yellowBtnMat", scene);
  yellowBtnMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  yellowBtnMat.emissiveColor = new BABYLON.Color3(0.4, 0.3, 0);

  // 전체 모델을 그룹화할 TransformNode
  const frameNode = new BABYLON.TransformNode("fwDownloadJigFrame", scene);
  frameNode.parent = machineMesh;

  const jigSize = { width: 10, height: 12, depth: 7 };

  // 2. 하부 베이스 프레임 (Lower Base Frame)
  // 짙은 회색의 무거운 베이스 캐비닛
  const baseFrame = BABYLON.MeshBuilder.CreateBox("baseFrame", {width: jigSize.width, height: h * 0.5, depth: jigSize.depth}, scene);
  baseFrame.position.y = h * 0.25;
  baseFrame.material = darkMetalMat;
  baseFrame.parent = frameNode;

  // 전면 하단 통풍구 (Ventilation Slots - 단순화)
  for(let i=0; i<3; i++) {
    const vent = BABYLON.MeshBuilder.CreateBox("vent", {width: w * 0.25, height: h * 0.01, depth: d * 0.01}, scene);
    vent.position = new BABYLON.Vector3(-3 + (i * 3), 1, -(jigSize.depth / 2) - 0.05);
    vent.material = darkMetalMat;
    vent.parent = frameNode;
  }

  // 3. 지그 베이스 및 트레이 (DUT Stage & Tray)
  // 하부 고정 지그 베이스 (검은색)
  const dutStage = BABYLON.MeshBuilder.CreateBox("dutStage", {width: jigSize.width - 2, height: h * 0.15, depth: jigSize.depth - 2}, scene);
  dutStage.position = new BABYLON.Vector3(0, 5 + 0.75, 0.5); // 베이스 프레임 위에 돌출
  dutStage.material = darkJigMat;
  dutStage.parent = frameNode;

  // 산업용 안티-스틱 트레이 (앞서 모델링한 형태를 단순화하여 배치)
  const tray = BABYLON.MeshBuilder.CreateBox("dutTray", {width: w * 0.6, height: h * 0.02, depth: d * 0.4}, scene);
  tray.position = new BABYLON.Vector3(0, 5 + 1.5 + 0.1, 1);
  tray.material = darkJigMat;
  tray.parent = frameNode;

  // 트레이 안의 카메라 모듈 (플레이스홀더)
  const grip = BABYLON.MeshBuilder.CreateBox("grip", {width: w * 0.1, height: h * 0.01, depth: d * 0.1}, scene);
  grip.position = new BABYLON.Vector3(-1.5, 5 + 1.5 + 0.3, 0.5);
  grip.material = darkJigMat;
  grip.parent = frameNode;

  // 4. 수직 기둥 및 헤드 메커니즘 (Vertical Gantry & Head)
  // 수직 지지 기둥 (Column)
  const column = BABYLON.MeshBuilder.CreateBox("column", {width: w * 0.15, height: h * 0.6, depth: d * 0.2}, scene);
  column.position = new BABYLON.Vector3(-(jigSize.width / 2) + 1.5, 8, 1); // 뒤쪽 왼쪽에 배치
  column.material = darkMetalMat;
  column.parent = frameNode;

  // 상하 이동 갠트리 암 (Gantry Arm)
  const gantryArm = BABYLON.MeshBuilder.CreateBox("gantryArm", {width: w * 0.12, height: h * 0.1, depth: d * 0.45}, scene);
  gantryArm.position = new BABYLON.Vector3(-(jigSize.width / 2) + 1.5, 10, -1); // 앞으로 돌출
  gantryArm.material = darkMetalMat;
  gantryArm.parent = frameNode;

  // 다운로드 헤드 블록 (Download Head - 검은색)
  const headBlock = BABYLON.MeshBuilder.CreateBox("headBlock", {width: w * 0.25, height: h * 0.2, depth: d * 0.25}, scene);
  headBlock.position = new BABYLON.Vector3(0, 8.5, -1.5); // 트레이 중앙 위에 배치
  headBlock.material = darkJigMat;
  headBlock.parent = frameNode;

  // 5. 핵심 디테일: 포고 핀 어레이 및 배선 (Pogo Pins & Wiring)
  // 헤드 하단의 미세 포고 핀들 (09_FW_Download.jpg의 가장 큰 특징)
  const pinGridRows = 4;
  const pinGridCols = 3;
  const pinSpacing = 0.4;

  for (let r = 0; r < pinGridRows; r++) {
    for (let c = 0; c < pinGridCols; c++) {
      const posX = -0.5 + c * pinSpacing;
      const posZ = -0.8 + r * pinSpacing;

      const pogoPin = BABYLON.MeshBuilder.CreateCylinder(`pogoPin_r${r}_c${c}`, {diameter: w * 0.005, height: h * 0.08}, scene);
      pogoPin.position = new BABYLON.Vector3(posX, 7.1, posZ - 1.5); // 헤드 하단에 밀착
      pogoPin.material = goldPinMat;
      pogoPin.parent = frameNode;
    }
  }

  // 헤드 주변의 복잡한 배선 및 공압 튜브 (파란색/검은색 섞임)
  for(let i=0; i<4; i++) {
    const tube = BABYLON.MeshBuilder.CreateCylinder(`tube${i}`, {diameter: w * 0.01, height: h * 0.25}, scene);
    tube.position.x = -(jigSize.width / 2) + 1 + (i * 0.1);
    tube.position.y = h * 0.9;
    tube.position.z = d * 0.02;
    tube.rotation.z = Math.PI / 8;
    tube.material = i === 1 ? blueTubeMat : darkMetalMat; // 한 개만 파란색 공압 튜브
    tube.parent = frameNode;
  }

  const cableBundle = BABYLON.MeshBuilder.CreateCylinder("cableBundle", {diameter: w * 0.03, height: h * 0.2}, scene);
  cableBundle.position.x = w * -0.12;
  cableBundle.position.y = h * 0.95;
  cableBundle.position.z = d * -0.15;
  cableBundle.rotation.x = Math.PI / 4;
  cableBundle.material = darkMetalMat;
  cableBundle.parent = frameNode;

  // 6. 전면 조작 버튼부 (Front Control Buttons)
  // 09_FW_Download.jpg의 베이스 앞쪽 좌우에 배치된 큼직한 버튼들
  const buttonPanelSize = { width: jigSize.width - 2, height: 0.1, depth: 1.5 };
  
  const buttonPanel = BABYLON.MeshBuilder.CreateBox("buttonPanel", {width: buttonPanelSize.width, height: h * 0.015, depth: buttonPanelSize.depth}, scene);
  buttonPanel.position = new BABYLON.Vector3(0, 1.5, -(jigSize.depth / 2) - 0.7); // 앞으로 돌출된 패널
  buttonPanel.rotation.x = Math.PI / 12; // 살짝 기울어짐
  buttonPanel.material = darkMetalMat;
  buttonPanel.parent = frameNode;

  // 비상 정지 버튼 (노란 베이스 + 큰 빨간 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateBox("eStopBase", {width: w * 0.12, height: h * 0.02, depth: d * 0.12}, scene);
  eStopBase.position = new BABYLON.Vector3(-3.5, 1.6, -(jigSize.depth / 2) - 1.2);
  eStopBase.rotation.x = Math.PI / 12;
  eStopBase.material = yellowBtnMat;
  eStopBase.parent = frameNode;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.04}, scene);
  eStopBtn.position = new BABYLON.Vector3(-3.5, 1.7, -(jigSize.depth / 2) - 1.25);
  eStopBtn.rotation.x = Math.PI / 12 + Math.PI/2;
  eStopBtn.material = redBtnMat;
  eStopBtn.parent = frameNode;

  // 시작 버튼 (녹색)
  const startBtnBase = BABYLON.MeshBuilder.CreateCylinder("startBtnBase", {diameter: w * 0.1, height: h * 0.02}, scene);
  startBtnBase.position = new BABYLON.Vector3(3.5, 1.6, -(jigSize.depth / 2) - 1.2);
  startBtnBase.rotation.x = Math.PI / 12 + Math.PI/2;
  startBtnBase.material = darkMetalMat;
  startBtnBase.parent = frameNode;

  const startBtn = BABYLON.MeshBuilder.CreateCylinder("startBtn", {diameter: w * 0.06999999999999999, height: h * 0.03}, scene);
  startBtn.position = new BABYLON.Vector3(3.5, 1.7, -(jigSize.depth / 2) - 1.25);
  startBtn.rotation.x = Math.PI / 12 + Math.PI/2;
  startBtn.material = greenBtnMat;
  startBtn.parent = frameNode;

  // 7. 타워 램프 (Tower Light - 우측 상단 지지 기둥 위)
  const pole = BABYLON.MeshBuilder.CreateCylinder("pole", {diameter: w * 0.015, height: h * 0.15}, scene);
  pole.position = new BABYLON.Vector3(jigSize.width / 2 - 1, 12.75, -1);
  pole.material = darkMetalMat;
  pole.parent = frameNode;

  const colors = [
    { name: "red", col: new BABYLON.Color3(1, 0, 0), y: 13.8 },
    { name: "yel", col: new BABYLON.Color3(1, 1, 0), y: 13.5 },
    { name: "grn", col: new BABYLON.Color3(0, 1, 0), y: 13.2 }
  ];

  colors.forEach(c => {
    const mat = new BABYLON.StandardMaterial(c.name + "TMat", scene);
    mat.diffuseColor = c.col;
    mat.emissiveColor = c.col;
    const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "TLight", {diameter: w * 0.04, height: h * 0.025}, scene);
    light.position = new BABYLON.Vector3(jigSize.width / 2 - 1, c.y, -1);
    light.material = mat;
    light.parent = frameNode;
  });
};