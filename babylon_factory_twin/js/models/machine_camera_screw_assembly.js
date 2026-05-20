window.buildCameraScrewAssemblyModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 폴리싱된 금속 프레임 (회색)
  const polishedMetalMat = new BABYLON.StandardMaterial("polishedMetalMat", scene);
  polishedMetalMat.diffuseColor = new BABYLON.Color3(0.7, 0.7, 0.7);
  polishedMetalMat.specularColor = new BABYLON.Color3(0.9, 0.9, 0.9);
  polishedMetalMat.roughness = 0.2; // 부드러운 반사

  // 내부 기구물 및 어두운 부품 (검은색)
  const darkMat = new BABYLON.StandardMaterial("darkMat", scene);
  darkMat.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.1);
  darkMat.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2);

  // 투명 패널 (아크릴/유리)
  const clearPanelMat = new BABYLON.StandardMaterial("clearPanelMat", scene);
  clearPanelMat.diffuseColor = new BABYLON.Color3(0.8, 0.8, 0.9);
  clearPanelMat.alpha = 0.3; // 반투명
  clearPanelMat.backFaceCulling = false; // 양면 렌더링

  // HMI 모니터 화면 (빛나는 푸른빛)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.05, 0.3, 0.6);

  // 전체 모델을 그룹화할 TransformNode
  const frame = new BABYLON.TransformNode("csAssemblyFrame", scene);
  frame.parent = machineMesh;

  // 2. 외부 프레임 (External Enclosure)
  const frameSize = { width: 14, height: 18, depth: 8 };

  // 하부 제어반/캐비닛 (Base Cabinet)
  const baseCabinet = BABYLON.MeshBuilder.CreateBox("baseCabinet", {width: frameSize.width, height: h * 0.6, depth: frameSize.depth}, scene);
  baseCabinet.position.y = h * 0.3;
  baseCabinet.material = polishedMetalMat;
  baseCabinet.parent = frame;

  // 상부 작업 챔버 프레임 (Upper Chamber Frame)
  const topFrame = BABYLON.MeshBuilder.CreateBox("topFrame", {width: frameSize.width, height: h * 1.2, depth: frameSize.depth}, scene);
  topFrame.position.y = h * 1.2;
  topFrame.material = polishedMetalMat;
  topFrame.parent = frame;
  topFrame.isVisible = false; // 프레임만 잡고 내부는 비움

  // 수직 지지 기둥 (Support Beams)
  const beamDetails = [
    {x: -6.75, z: -3.75}, {x: 6.75, z: -3.75},
    {x: -6.75, z: 3.75}, {x: 6.75, z: 3.75}
  ];
  beamDetails.forEach(beam => {
    const sBeam = BABYLON.MeshBuilder.CreateBox("sBeam", {width: w * 0.05, height: h * 1.2, depth: d * 0.05}, scene);
    sBeam.position = new BABYLON.Vector3(beam.x, 12, beam.z);
    sBeam.material = polishedMetalMat;
    sBeam.parent = frame;
  });

  // 투명 패널 (Clear Panels - 앞, 뒤, 좌, 우)
  const frontPanel = BABYLON.MeshBuilder.CreateBox("frontPanel", {width: frameSize.width - 1, height: h * 1.15, depth: d * 0.01}, scene);
  frontPanel.position = new BABYLON.Vector3(0, 12, -3.95);
  frontPanel.material = clearPanelMat;
  frontPanel.parent = frame;

  const backPanel = BABYLON.MeshBuilder.CreateBox("backPanel", {width: frameSize.width - 1, height: h * 1.15, depth: d * 0.01}, scene);
  backPanel.position = new BABYLON.Vector3(0, 12, 3.95);
  backPanel.material = clearPanelMat;
  backPanel.parent = frame;

  const leftPanel = BABYLON.MeshBuilder.CreateBox("leftPanel", {width: w * 0.01, height: h * 1.15, depth: frameSize.depth - 1}, scene);
  leftPanel.position = new BABYLON.Vector3(-6.95, 12, 0);
  leftPanel.material = clearPanelMat;
  leftPanel.parent = frame;

  const rightPanel = BABYLON.MeshBuilder.CreateBox("rightPanel", {width: w * 0.01, height: h * 1.15, depth: frameSize.depth - 1}, scene);
  rightPanel.position = new BABYLON.Vector3(6.95, 12, 0);
  rightPanel.material = clearPanelMat;
  rightPanel.parent = frame;

  // 3. 내부 액티브 정렬 갠트리 (Internal Gantry & Tooling)
  // X-Y-Z 갠트리 시스템 전체
  const gantrySystem = new BABYLON.TransformNode("gantrySystem", scene);
  gantrySystem.parent = frame;
  gantrySystem.position.y = h * 1.2;

  // Y축 슬라이드 레일 (Y-axis Slide Rail)
  const yRail = BABYLON.MeshBuilder.CreateBox("yRail", {width: frameSize.width - 2, height: h * 0.02, depth: d * 0.6}, scene);
  yRail.position.y = h * 0.3;
  yRail.material = darkMat;
  yRail.parent = gantrySystem;

  // X축 가로 보 (X-axis Bridge)
  const xBridge = BABYLON.MeshBuilder.CreateBox("xBridge", {width: w * 1, height: h * 0.04, depth: d * 0.04}, scene);
  xBridge.position = new BABYLON.Vector3(0, 3.3, 0);
  xBridge.material = polishedMetalMat;
  xBridge.parent = gantrySystem;

  // Z축 정렬 헤드 및 다축 툴 (Z-axis Alignment Head & Tooling)
  const toolHead = new BABYLON.TransformNode("toolHead", scene);
  toolHead.parent = gantrySystem;
  toolHead.position = new BABYLON.Vector3(2, 3.3, -1); // 이미지의 오른쪽 툴링 위치

  // 툴 헤드 베이스
  const toolBase = BABYLON.MeshBuilder.CreateBox("toolBase", {width: w * 0.25, height: h * 0.08, depth: d * 0.25}, scene);
  toolBase.material = darkMat;
  toolBase.parent = toolHead;

  // 다축 툴 구성품 (이미지의 복잡한 툴 묘사)
  // 1: 중앙 정렬 실린더
  const centerCyl = BABYLON.MeshBuilder.CreateCylinder("centerCyl", {diameter: w * 0.08, height: h * 0.3}, scene);
  centerCyl.position.y = h * -0.15;
  centerCyl.material = polishedMetalMat;
  centerCyl.parent = toolHead;

  // 2: 측면 소형 툴 (실린더 어레이)
  const sideToolDetails = [
    {x: -0.8, z: -0.8}, {x: 0.8, z: -0.8},
    {x: -0.8, z: 0.8}, {x: 0.8, z: 0.8}
  ];
  sideToolDetails.forEach((tool, index) => {
    const sTool = BABYLON.MeshBuilder.CreateCylinder(`sTool_${index}`, {diameter: w * 0.04, height: h * 0.25}, scene);
    sTool.position = new BABYLON.Vector3(tool.x, -1.25, tool.z);
    sTool.material = darkMat;
    sTool.parent = toolHead;
  });

  // 3: 카메라 툴 (카메라 모양의 육면체와 렌즈 실린더)
  const camBody = BABYLON.MeshBuilder.CreateBox("camBody", {width: w * 0.1, height: h * 0.15, depth: d * 0.1}, scene);
  camBody.position = new BABYLON.Vector3(0, 0.4, 1);
  camBody.material = darkMat;
  camBody.parent = toolHead;

  const camLens = BABYLON.MeshBuilder.CreateCylinder("camLens", {diameter: w * 0.03, height: h * 0.05}, scene);
  camLens.position = new BABYLON.Vector3(0, -0.6, 1);
  camLens.material = polishedMetalMat;
  camLens.parent = toolHead;

  // 4. 내부 세부 요소 (Interior Details)
  // 작업 표면 (Work Surface)
  const workSurface = BABYLON.MeshBuilder.CreateBox("workSurface", {width: frameSize.width - 2, height: h * 0.01, depth: frameSize.depth - 2}, scene);
  workSurface.position.y = h * 0.605;
  workSurface.material = darkMat;
  workSurface.parent = frame;

  // 내부 돔 조명 (Dome Lights - 이미지의 밝은 부분)
  const lightDetails = [
    {x: -4, z: -2}, {x: 0, z: -2}, {x: 4, z: -2},
    {x: -4, z: 2}, {x: 0, z: 2}, {x: 4, z: 2}
  ];
  lightDetails.forEach((light, index) => {
    const dLight = BABYLON.MeshBuilder.CreateSphere(`dLight_${index}`, {diameter: w * 0.08, segments: 16}, scene);
    dLight.position = new BABYLON.Vector3(light.x, 17.5, light.z);
    dLight.material = screenMat; // emissiveColor를 활용해 조명 효과
    dLight.scaling.y = 0.5; // 납작하게 만들어 돔 형태
    dLight.parent = frame;
  });

  // 5. 측면 HMI 제어대 (HMI Control Station)
  const controlStation = new BABYLON.TransformNode("controlStation", scene);
  controlStation.parent = frame;
  controlStation.position = new BABYLON.Vector3(10, 0, -3); // 이미지의 오른쪽 앞 위치

  // 이동형 카트 (Rolling Cart)
  const cart = BABYLON.MeshBuilder.CreateBox("cart", {width: w * 0.3, height: h * 0.4, depth: d * 0.3}, scene);
  cart.position.y = h * 0.2;
  cart.material = darkMat;
  cart.parent = controlStation;

  // 바퀴 (Wheels)
  const wheelDetails = [
    {x: -1.2, z: -1.2}, {x: 1.2, z: -1.2},
    {x: -1.2, z: 1.2}, {x: 1.2, z: 1.2}
  ];
  wheelDetails.forEach((wheel, index) => {
    const sWheel = BABYLON.MeshBuilder.CreateCylinder(`sWheel_${index}`, {diameter: w * 0.03, height: h * 0.04}, scene);
    sWheel.position = new BABYLON.Vector3(wheel.x, 0.2, wheel.z);
    sWheel.rotation.z = Math.PI / 2; // 가로로 눕힘
    sWheel.material = darkMat;
    sWheel.parent = cart;
  });

  // 모니터 암 (Monitor Arm)
  const arm = BABYLON.MeshBuilder.CreateBox("arm", {width: w * 0.02, height: h * 0.3, depth: d * 0.02}, scene);
  arm.position = new BABYLON.Vector3(0, 5.5, 0);
  arm.material = darkMat;
  arm.parent = controlStation;

  // HMI 모니터 화면 (Monitor Screen)
  const monitor = BABYLON.MeshBuilder.CreateBox("monitor", {width: w * 0.3, height: h * 0.2, depth: d * 0.01}, scene);
  monitor.position = new BABYLON.Vector3(0, 7.1, 0);
  monitor.material = darkMat;
  monitor.parent = controlStation;

  const monitorScreen = BABYLON.MeshBuilder.CreatePlane("monitorScreen", {width: w * 0.27999999999999997, height: h * 0.18}, scene);
  monitorScreen.position = new BABYLON.Vector3(0, 7.1, -0.06); // 모니터 전면에 밀착
  monitorScreen.material = screenMat;
  monitorScreen.parent = controlStation;

  // 키보드 트레이 (Keyboard Tray)
  const keyboardTray = BABYLON.MeshBuilder.CreateBox("keyboardTray", {width: w * 0.3, height: h * 0.005, depth: d * 0.15}, scene);
  keyboardTray.position = new BABYLON.Vector3(0, 4, -1.2);
  keyboardTray.rotation.x = Math.PI / 12; // 살짝 앞쪽으로 꺾인 각도
  keyboardTray.material = darkMat;
  keyboardTray.parent = controlStation;
};