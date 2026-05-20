window.buildCoatingAoiModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 기본 프레임 (다크 그레이/블랙 무광 톤)
  const darkFrameMat = new BABYLON.StandardMaterial("darkFrameMat", scene);
  darkFrameMat.diffuseColor = new BABYLON.Color3(0.15, 0.16, 0.18);
  darkFrameMat.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1);
  darkFrameMat.roughness = 0.7;

  // 하단 통풍구 쪽 패널 (약간 더 어두운 톤)
  const ventPanelMat = new BABYLON.StandardMaterial("ventPanelMat", scene);
  ventPanelMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.12);

  // 전면 관찰창 (어두운 틴팅 유리 느낌)
  const darkGlassMat = new BABYLON.StandardMaterial("darkGlassMat", scene);
  darkGlassMat.diffuseColor = new BABYLON.Color3(0.05, 0.05, 0.05);
  darkGlassMat.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);
  darkGlassMat.alpha = 0.85; // 내부가 거의 안 보이는 짙은 틴팅

  // 손잡이 및 금속 부품
  const metalMat = new BABYLON.StandardMaterial("metalMat", scene);
  metalMat.diffuseColor = new BABYLON.Color3(0.75, 0.75, 0.75);

  // 버튼 및 램프 색상
  const redMat = new BABYLON.StandardMaterial("redMat", scene);
  redMat.diffuseColor = new BABYLON.Color3(0.8, 0.1, 0.1);
  const greenMat = new BABYLON.StandardMaterial("greenMat", scene);
  greenMat.diffuseColor = new BABYLON.Color3(0.1, 0.8, 0.2);
  greenMat.emissiveColor = new BABYLON.Color3(0.1, 0.5, 0.1);

  // 모니터 화면 (빛나는 푸른빛)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.2, 0.4);

  // 전체 모델을 그룹화할 TransformNode
  const frame = new BABYLON.TransformNode("coatingAoiFrame", scene);
  frame.parent = machineMesh;

  const frameSize = { width: 9, height: 14, depth: 7 };

  // 2. 메인 바디 (Main Enclosure)
  // 하단 캐비닛 (Base Cabinet - 벤틸레이션 홀이 있는 부분)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameSize.width, height: h * 0.5, depth: frameSize.depth}, scene);
  baseCabinet.position.y = h * 0.25;
  baseCabinet.material = ventPanelMat;
  baseCabinet.parent = frame;

  // 상단 메인 챔버 (Upper Chamber)
  const upperChamber = BABYLON.MeshBuilder.CreateBox("upperChamber", {width: frameSize.width, height: h * 0.9, depth: frameSize.depth}, scene);
  upperChamber.position.y = h * 0.95;
  upperChamber.material = darkFrameMat;
  upperChamber.parent = frame;

  // 3. 전면 도어 및 관찰창 (Front Door & Window)
  // 짙은 틴팅 유리창
  const frontWindow = BABYLON.MeshBuilder.CreateBox("frontWindow", {width: w * 0.75, height: h * 0.55, depth: d * 0.02}, scene);
  frontWindow.position.y = h * 1.05;
  frontWindow.position.z = -(frameSize.depth / 2) - 0.05; // 앞으로 살짝 돌출
  frontWindow.material = darkGlassMat;
  frontWindow.parent = frame;

  // 도어 가로 손잡이 (은색)
  const handle = BABYLON.MeshBuilder.CreateBox("handle", {width: w * 0.6, height: h * 0.02, depth: d * 0.03}, scene);
  handle.position.y = h * 0.75;
  handle.position.z = -(frameSize.depth / 2) - 0.2;
  handle.material = metalMat;
  handle.parent = frame;

  // 4. 좌측 제어 패널 (Left Control Panel)
  const controlPanel = BABYLON.MeshBuilder.CreateBox("controlPanel", {width: w * 0.15, height: h * 0.6, depth: d * 0.1}, scene);
  controlPanel.position.x = -(frameSize.width / 2) - 0.5;
  controlPanel.position.y = h * 0.8;
  controlPanel.position.z = -(frameSize.depth / 2) + 0.5;
  controlPanel.material = darkFrameMat;
  controlPanel.parent = frame;

  // 비상 정지 버튼 (큰 빨간색)
  const eStopBtn = BABYLON.MeshBuilder.CreateCylinder("eStopBtn", {diameter: w * 0.08, height: h * 0.02}, scene);
  eStopBtn.position.x = -(frameSize.width / 2) - 0.5;
  eStopBtn.position.y = h * 0.95;
  eStopBtn.position.z = -(frameSize.depth / 2) - 0.05;
  eStopBtn.rotation.x = Math.PI / 2;
  eStopBtn.material = redMat;
  eStopBtn.parent = frame;

  // Start / Stop 조작 버튼들
  const startBtn = BABYLON.MeshBuilder.CreateCylinder("startBtn", {diameter: w * 0.04, height: h * 0.02}, scene);
  startBtn.position.x = -(frameSize.width / 2) - 0.5;
  startBtn.position.y = h * 0.85;
  startBtn.position.z = -(frameSize.depth / 2) - 0.05;
  startBtn.rotation.x = Math.PI / 2;
  startBtn.material = greenMat;
  startBtn.parent = frame;

  const stopBtn = BABYLON.MeshBuilder.CreateCylinder("stopBtn", {diameter: w * 0.04, height: h * 0.02}, scene);
  stopBtn.position.x = -(frameSize.width / 2) - 0.5;
  stopBtn.position.y = h * 0.78;
  stopBtn.position.z = -(frameSize.depth / 2) - 0.05;
  stopBtn.rotation.x = Math.PI / 2;
  stopBtn.material = redMat;
  stopBtn.parent = frame;

  // 5. 상단 모니터 (Top Monitor)
  const monitorArm = BABYLON.MeshBuilder.CreateBox("monitorArm", {width: w * 0.03, height: h * 0.2, depth: d * 0.03}, scene);
  monitorArm.position.x = w * 0.35;
  monitorArm.position.y = h * 1.5;
  monitorArm.position.z = d * -0.1;
  monitorArm.material = metalMat;
  monitorArm.parent = frame;

  const monitor = BABYLON.MeshBuilder.CreateBox("monitor", {width: w * 0.4, height: h * 0.25, depth: d * 0.02}, scene);
  monitor.position.x = w * 0.35;
  monitor.position.y = h * 1.6;
  monitor.position.z = d * -0.1;
  monitor.rotation.x = -Math.PI / 18; // 살짝 위를 향함 (사용자 시야각)
  monitor.material = darkFrameMat;
  monitor.parent = frame;

  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.38, height: h * 0.22999999999999998}, scene);
  monitorScreen.position.x = w * 0.35;
  monitorScreen.position.y = h * 1.6;
  monitorScreen.position.z = d * -0.11100000000000002;
  monitorScreen.rotation.x = -Math.PI / 18;
  monitorScreen.material = screenMat;
  monitorScreen.parent = frame;

  // 6. 타워 램프 (Tower Light)
  const pole = BABYLON.MeshBuilder.CreateCylinder("pole", {diameter: w * 0.015, height: h * 0.15}, scene);
  pole.position.x = w * -0.35;
  pole.position.y = h * 1.475;
  pole.position.z = 0;
  pole.material = metalMat;
  pole.parent = frame;

  const lightColors = [
      { name: "red", col: new BABYLON.Color3(1, 0, 0), yPos: h * 1.6 },
      { name: "yel", col: new BABYLON.Color3(1, 1, 0), yPos: h * 1.5699999999999998 },
      { name: "grn", col: new BABYLON.Color3(0, 1, 0), yPos: h * 1.54 }
  ];

  lightColors.forEach(c => {
      const lightMat = new BABYLON.StandardMaterial(c.name + "Mat", scene);
      lightMat.emissiveColor = c.col;
      lightMat.diffuseColor = c.col;
      
      const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "Light", {diameter: w * 0.04, height: h * 0.025}, scene);
      light.position.x = w * -0.35;
      light.position.y = c.yPos;
      light.position.z = 0;
      light.material = lightMat;
      light.parent = frame;
  });
};