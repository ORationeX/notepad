window.buildConformalCoatingModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 메인 프레임 (밝은 회색)
  const lightGrayMat = new BABYLON.StandardMaterial("lightGrayMat", scene);
  lightGrayMat.diffuseColor = new BABYLON.Color3(0.7, 0.73, 0.75);

  // 하단부 및 조작 패널 (흰색/매우 밝은 회색)
  const whiteMat = new BABYLON.StandardMaterial("whiteMat", scene);
  whiteMat.diffuseColor = new BABYLON.Color3(0.85, 0.85, 0.85);

  // 내부 기구물 및 프레임 (어두운 회색/검정)
  const darkMat = new BABYLON.StandardMaterial("darkMat", scene);
  darkMat.diffuseColor = new BABYLON.Color3(0.2, 0.2, 0.2);

  // 공압 튜브용 재질 (밝은 파란색)
  const blueTubeMat = new BABYLON.StandardMaterial("blueTubeMat", scene);
  blueTubeMat.diffuseColor = new BABYLON.Color3(0.1, 0.4, 0.8);

  // 상부 도어 투명 창 (유리)
  const glassMat = new BABYLON.StandardMaterial("glassMat", scene);
  glassMat.diffuseColor = new BABYLON.Color3(0.8, 0.9, 0.9);
  glassMat.alpha = 0.4;
  glassMat.backFaceCulling = false;

  // 버튼 및 램프, 모니터
  const yellowMat = new BABYLON.StandardMaterial("yellowMat", scene);
  yellowMat.diffuseColor = new BABYLON.Color3(0.9, 0.8, 0.1);
  const redMat = new BABYLON.StandardMaterial("redMat", scene);
  redMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  const greenMat = new BABYLON.StandardMaterial("greenMat", scene);
  greenMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);
  const blackMat = new BABYLON.StandardMaterial("blackMat", scene);
  blackMat.diffuseColor = new BABYLON.Color3(0.05, 0.05, 0.05);
  
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.6, 0.8); // 윈도우 바탕화면 느낌

  // 전체 모델을 그룹화할 TransformNode
  const frame = new BABYLON.TransformNode("coatingMachineFrame", scene);
  frame.parent = machineMesh;

  const frameWidth = 11;
  const frameHeight = 12; // 닫혔을 때 기준
  const frameDepth = 8;

  // 2. 외부 프레임 및 캐비닛 (Base & Body)
  // 하부 캐비닛 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameWidth, height: h * 0.6, depth: frameDepth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = lightGrayMat;
  baseCabinet.parent = frame;

  // 전면 하단 흰색 패널 도어
  const frontDoors = BABYLON.MeshBuilder.CreateBox("frontDoors", {width: frameWidth - 0.5, height: h * 0.55, depth: d * 0.01}, scene);
  frontDoors.position.y = h * 0.3;
  frontDoors.position.z = -(frameDepth / 2) - 0.05;
  frontDoors.material = whiteMat;
  frontDoors.parent = frame;

  // 상부 작업 영역 측면/후면 벽
  const leftWall = BABYLON.MeshBuilder.CreateBox("leftWall", {width: w * 0.1, height: h * 0.6, depth: frameDepth}, scene);
  leftWall.position.x = -(frameWidth / 2) + 0.5;
  leftWall.position.y = h * 0.9;
  leftWall.material = lightGrayMat;
  leftWall.parent = frame;

  const rightWall = BABYLON.MeshBuilder.CreateBox("rightWall", {width: w * 0.1, height: h * 0.6, depth: frameDepth}, scene);
  rightWall.position.x = (frameWidth / 2) - 0.5;
  rightWall.position.y = h * 0.9;
  rightWall.material = lightGrayMat;
  rightWall.parent = frame;

  const backWall = BABYLON.MeshBuilder.CreateBox("backWall", {width: frameWidth - 2, height: h * 0.6, depth: d * 0.1}, scene);
  backWall.position.y = h * 0.9;
  backWall.position.z = (frameDepth / 2) - 0.5;
  backWall.material = darkMat; // 내부는 어둡게
  backWall.parent = frame;

  // 3. 전면 조작 패널 (Front Control Panel)
  const controlPanel = BABYLON.MeshBuilder.CreateBox("controlPanel", {width: frameWidth, height: h * 0.15, depth: d * 0.12}, scene);
  controlPanel.position.y = h * 0.65;
  controlPanel.position.z = -(frameDepth / 2) - 0.2;
  controlPanel.rotation.x = Math.PI / 12; // 살짝 기울어진 디자인
  controlPanel.material = whiteMat;
  controlPanel.parent = frame;

  // 비상 정지 버튼 (노란 베이스 + 빨간 버튼)
  const eStopBase = BABYLON.MeshBuilder.CreateCylinder("eStopBase", {diameter: w * 0.12, height: h * 0.01}, scene);
  eStopBase.position.x = w * -0.4;
  eStopBase.position.y = h * 0.6599999999999999;
  eStopBase.position.z = -(frameDepth / 2) - 0.8;
  eStopBase.rotation.x = Math.PI / 12;
  eStopBase.material = yellowMat;
  eStopBase.parent = frame;

  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.03}, scene);
  eStopBtn.position.x = w * -0.4;
  eStopBtn.position.y = h * 0.67;
  eStopBtn.position.z = -(frameDepth / 2) - 0.85;
  eStopBtn.rotation.x = Math.PI / 12 + Math.PI/2;
  eStopBtn.material = redMat;
  eStopBtn.parent = frame;

  // 작은 조작 버튼들
  for(let i=0; i<4; i++) {
    const btn = BABYLON.MeshBuilder.CreateCylinder(`smallBtn${i}`, {diameter: w * 0.03, height: h * 0.02}, scene);
    btn.position.x = w * -0.1 + (i * 1);
    btn.position.y = h * 0.655;
    btn.position.z = -(frameDepth / 2) - 0.8;
    btn.rotation.x = Math.PI / 12 + Math.PI/2;
    btn.material = i === 0 ? greenMat : (i === 1 ? redMat : whiteMat);
    btn.parent = frame;
  }

  // 4. 위로 열린 상부 도어 (Opened Top Hood)
  const hoodPivot = new BABYLON.TransformNode("hoodPivot", scene);
  hoodPivot.position.y = h * 1.2;
  hoodPivot.position.z = (frameDepth / 2) - 1; // 뒤쪽 상단 힌지
  hoodPivot.parent = frame;
  hoodPivot.rotation.x = -Math.PI / 2.5; // 위로 활짝 열린 각도

  // 도어 프레임
  const hoodFrame = BABYLON.MeshBuilder.CreateBox("hoodFrame", {width: frameWidth, height: h * 0.6, depth: d * 0.05}, scene);
  hoodFrame.position.y = h * -0.3; // 피벗 기준으로 아래로
  hoodFrame.material = lightGrayMat;
  hoodFrame.parent = hoodPivot;

  // 도어 투명 창
  const hoodGlass = BABYLON.MeshBuilder.CreateBox("hoodGlass", {width: frameWidth - 2, height: h * 0.45, depth: d * 0.06}, scene);
  hoodGlass.position.y = h * -0.3;
  hoodGlass.material = glassMat;
  hoodGlass.parent = hoodPivot;

  // 가스 스프링 (Gas Struts - 문을 지탱하는 실린더)
  const strutL = BABYLON.MeshBuilder.CreateCylinder("strutL", {diameter: w * 0.02, height: h * 0.4}, scene);
  strutL.position.x = -(frameWidth / 2) + 0.8;
  strutL.position.y = h * 1.05;
  strutL.position.z = 0;
  strutL.rotation.x = Math.PI / 4;
  strutL.material = blackMat;
  strutL.parent = frame;

  const strutR = BABYLON.MeshBuilder.CreateCylinder("strutR", {diameter: w * 0.02, height: h * 0.4}, scene);
  strutR.position.x = (frameWidth / 2) - 0.8;
  strutR.position.y = h * 1.05;
  strutR.position.z = 0;
  strutR.rotation.x = Math.PI / 4;
  strutR.material = blackMat;
  strutR.parent = frame;

  // 5. 내부 디스펜싱 갠트리 (Internal Dispensing Gantry)
  // X축 가이드 레일
  const xRail = BABYLON.MeshBuilder.CreateBox("xRail", {width: frameWidth - 2.5, height: h * 0.05, depth: d * 0.05}, scene);
  xRail.position.y = h * 0.95;
  xRail.position.z = d * -0.1;
  xRail.material = darkMat;
  xRail.parent = frame;

  // 디스펜서 헤드 블록
  const headBlock = BABYLON.MeshBuilder.CreateBox("headBlock", {width: w * 0.15, height: h * 0.25, depth: d * 0.15}, scene);
  headBlock.position.x = w * -0.2;
  headBlock.position.y = h * 0.9;
  headBlock.position.z = d * -0.15;
  headBlock.material = darkMat;
  headBlock.parent = frame;

  // 코팅 밸브/노즐
  const nozzle = BABYLON.MeshBuilder.CreateCylinder("nozzle", {diameter: w * 0.02, height: h * 0.1}, scene);
  nozzle.position.x = w * -0.22999999999999998;
  nozzle.position.y = h * 0.73;
  nozzle.position.z = d * -0.18;
  nozzle.material = lightGrayMat;
  nozzle.parent = frame;

  // 파란색 공압 튜브들 (시각적 포인트)
  for(let i=0; i<3; i++) {
    const tube = BABYLON.MeshBuilder.CreateCylinder(`tube${i}`, {diameter: w * 0.01, height: h * 0.2}, scene);
    tube.position.x = w * -0.18 + (i * 0.2);
    tube.position.y = h * 1.05;
    tube.position.z = d * -0.15;
    tube.rotation.z = Math.PI / 6;
    tube.material = blueTubeMat;
    tube.parent = frame;
  }

  // 6. 우측 측면 HMI 암 및 패널 (Right Side HMI & MYCRONIC Panel)
  // 지지 암
  const hmiArm = BABYLON.MeshBuilder.CreateBox("hmiArm", {width: w * 0.2, height: h * 0.03, depth: d * 0.03}, scene);
  hmiArm.position.x = (frameWidth / 2) + 0.5;
  hmiArm.position.y = h * 0.8;
  hmiArm.position.z = d * 0.2;
  hmiArm.material = darkMat;
  hmiArm.parent = frame;

  // 로고가 들어가는 검은색 스탠드 패널
  const logoPanel = BABYLON.MeshBuilder.CreateBox("logoPanel", {width: w * 0.02, height: h * 0.35, depth: d * 0.3}, scene);
  logoPanel.position.x = (frameWidth / 2) + 1.5;
  logoPanel.position.y = h * 0.8;
  logoPanel.position.z = d * 0.2;
  logoPanel.material = blackMat; // 이 자리에 파란색 MYCRONIC 로고가 위치함
  logoPanel.parent = frame;

  // 모니터
  const monitor = BABYLON.MeshBuilder.CreateBox("monitor", {width: w * 0.02, height: h * 0.22000000000000003, depth: d * 0.32}, scene);
  monitor.position.x = (frameWidth / 2) + 1.2;
  monitor.position.y = h * 0.95;
  monitor.position.z = d * 0.2;
  monitor.rotation.y = -Math.PI / 8; // 사용자를 향해 살짝 틀어짐
  monitor.material = darkMat;
  monitor.parent = frame;

  const screen = BABYLON.MeshBuilder.CreatePlane("screen", {width: w * 0.3, height: h * 0.2}, scene);
  screen.position.x = (frameWidth / 2) + 1.09;
  screen.position.y = h * 0.95;
  screen.position.z = d * 0.205;
  screen.rotation.y = -Math.PI / 8 - Math.PI/2;
  screen.material = screenMat;
  screen.parent = frame;

  // 키보드 트레이
  const kbdTray = BABYLON.MeshBuilder.CreateBox("kbdTray", {width: w * 0.15, height: h * 0.01, depth: d * 0.3}, scene);
  kbdTray.position.x = (frameWidth / 2) + 0.5;
  kbdTray.position.y = h * 0.75;
  kbdTray.position.z = d * 0.2;
  kbdTray.rotation.y = -Math.PI / 8;
  kbdTray.material = darkMat;
  kbdTray.parent = frame;

  // 7. 타워 램프 (Tower Light - 좌측 상단)
  const towerPole = BABYLON.MeshBuilder.CreateCylinder("towerPole", {diameter: w * 0.015, height: h * 0.1}, scene);
  towerPole.position.x = -(frameWidth / 2) + 0.5;
  towerPole.position.y = h * 1.25;
  towerPole.position.z = 0;
  towerPole.material = darkMat;
  towerPole.parent = frame;

  const colors = [
    { name: "grn", col: new BABYLON.Color3(0, 1, 0), y: 13 },
    { name: "yel", col: new BABYLON.Color3(1, 1, 0), y: 13.3 },
    { name: "red", col: new BABYLON.Color3(1, 0, 0), y: 13.6 }
  ];

  colors.forEach(c => {
    const mat = new BABYLON.StandardMaterial(c.name + "TMat", scene);
    mat.diffuseColor = c.col;
    mat.emissiveColor = c.col;
    const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "TLight", {diameter: w * 0.04, height: h * 0.025}, scene);
    light.position.x = -(frameWidth / 2) + 0.5;
    light.position.y = c.y;
    light.position.z = 0;
    light.material = mat;
    light.parent = frame;
  });
};