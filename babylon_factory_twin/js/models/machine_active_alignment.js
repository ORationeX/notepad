window.buildActiveAlignmentModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 장비 외관 (메탈릭/스테인리스 스틸 느낌)
  const metalMat = new BABYLON.StandardMaterial("metalMat", scene);
  metalMat.diffuseColor = new BABYLON.Color3(0.8, 0.8, 0.85);
  metalMat.specularColor = new BABYLON.Color3(0.9, 0.9, 0.9);

  // 내부 어두운 기구물 및 작업대
  const darkMat = new BABYLON.StandardMaterial("darkMat", scene);
  darkMat.diffuseColor = new BABYLON.Color3(0.15, 0.15, 0.15);

  // 모니터 화면 (빛나는 푸른빛)
  const screenMat = new BABYLON.StandardMaterial("screenMat", scene);
  screenMat.emissiveColor = new BABYLON.Color3(0.1, 0.4, 0.8);

  // 전체 모델을 그룹화할 TransformNode
  const frame = new BABYLON.TransformNode("aa_frame", scene);
  frame.parent = machineMesh;

  // 2. 장비 외함 (Enclosure)
  // 베이스 (하단부)
  const base = BABYLON.MeshBuilder.CreateBox("base", {width: w * 1, height: h * 0.2, depth: d * 0.6}, scene);
  base.position.y = h * 0.1;
  base.material = metalMat;
  base.parent = frame;

  // 상단 덮개
  const top = BABYLON.MeshBuilder.CreateBox("top", {width: w * 1, height: h * 0.05, depth: d * 0.6}, scene);
  top.position.y = h * 0.675;
  top.material = metalMat;
  top.parent = frame;

  // 뒷면 벽
  const back = BABYLON.MeshBuilder.CreateBox("back", {width: w * 1, height: h * 0.45, depth: d * 0.05}, scene);
  back.position.y = h * 0.425;
  back.position.z = d * 0.275;
  back.material = metalMat;
  back.parent = frame;

  // 좌/우측 벽 (전면은 개방된 형태로 구성)
  const leftWall = BABYLON.MeshBuilder.CreateBox("leftWall", {width: w * 0.05, height: h * 0.45, depth: d * 0.6}, scene);
  leftWall.position.y = h * 0.425;
  leftWall.position.x = w * -0.475;
  leftWall.material = metalMat;
  leftWall.parent = frame;

  const rightWall = BABYLON.MeshBuilder.CreateBox("rightWall", {width: w * 0.05, height: h * 0.45, depth: d * 0.6}, scene);
  rightWall.position.y = h * 0.425;
  rightWall.position.x = w * 0.475;
  rightWall.material = metalMat;
  rightWall.parent = frame;

  // 3. 내부 액티브 얼라인 기구부 (Inner Gantry & Stage)
  // 자재가 놓이는 하단 스테이지
  const stage = BABYLON.MeshBuilder.CreateBox("stage", {width: w * 0.7, height: h * 0.02, depth: d * 0.3}, scene);
  stage.position.y = h * 0.21000000000000002;
  stage.position.z = 0;
  stage.material = darkMat;
  stage.parent = frame;

  // 상단 X축 갠트리 빔
  const gantryX = BABYLON.MeshBuilder.CreateBox("gantryX", {width: w * 0.8, height: h * 0.05, depth: d * 0.08}, scene);
  gantryX.position.y = h * 0.55;
  gantryX.position.z = d * -0.05;
  gantryX.material = metalMat;
  gantryX.parent = frame;

  // Z축 정렬 헤드 (카메라/렌즈 툴)
  const alignHead = BABYLON.MeshBuilder.CreateBox("alignHead", {width: w * 0.15, height: h * 0.25, depth: d * 0.15}, scene);
  alignHead.position.y = h * 0.42000000000000004;
  alignHead.position.z = d * -0.05;
  alignHead.material = darkMat;
  alignHead.parent = frame;

  // 렌즈를 잡는 툴링부 (실린더)
  const tool = BABYLON.MeshBuilder.CreateCylinder("tool", {diameter: w * 0.04, height: h * 0.1}, scene);
  tool.position.y = h * 0.26;
  tool.position.z = d * -0.05;
  tool.material = metalMat;
  tool.parent = frame;

  // 4. 측면 모니터 및 키보드 트레이 (Side Monitor Station)
  // 모니터 지지 암
  const arm = BABYLON.MeshBuilder.CreateBox("arm", {width: w * 0.15, height: h * 0.02, depth: d * 0.02}, scene);
  arm.position.x = w * 0.55;
  arm.position.y = h * 0.4;
  arm.position.z = d * 0.1;
  arm.material = darkMat;
  arm.parent = frame;

  // 모니터 패널
  const monitor = BABYLON.MeshBuilder.CreateBox("monitor", {width: w * 0.01, height: h * 0.15, depth: d * 0.22000000000000003}, scene);
  monitor.position.x = w * 0.62;
  monitor.position.y = h * 0.45;
  monitor.position.z = d * 0.1;
  monitor.rotation.y = Math.PI / 12; // 살짝 앞쪽으로 꺾인 각도
  monitor.material = screenMat;
  monitor.parent = frame;

  // 키보드 트레이
  const keyboardTray = BABYLON.MeshBuilder.CreateBox("kbd", {width: w * 0.08, height: h * 0.005, depth: d * 0.2}, scene);
  keyboardTray.position.x = w * 0.67;
  keyboardTray.position.y = h * 0.35;
  keyboardTray.position.z = d * 0.1;
  keyboardTray.material = darkMat;
  keyboardTray.parent = frame;

  // 5. 상단 타워 램프 (Tower Light - 녹/황/적)
  const pole = BABYLON.MeshBuilder.CreateCylinder("pole", {diameter: w * 0.01, height: h * 0.1}, scene);
  pole.position.x = w * 0.4;
  pole.position.y = h * 0.75;
  pole.position.z = d * 0.2;
  pole.material = darkMat;
  pole.parent = frame;

  const lightColors = [
      { name: "red", col: new BABYLON.Color3(1, 0, 0), yPos: h * 0.85 },
      { name: "yel", col: new BABYLON.Color3(1, 1, 0), yPos: h * 0.825 },
      { name: "grn", col: new BABYLON.Color3(0, 1, 0), yPos: h * 0.8 }
  ];

  lightColors.forEach(c => {
      const lightMat = new BABYLON.StandardMaterial(c.name + "Mat", scene);
      lightMat.emissiveColor = c.col; // 자체 발광 효과
      lightMat.diffuseColor = c.col;
      
      const light = BABYLON.MeshBuilder.CreateCylinder(c.name + "Light", {diameter: w * 0.03, height: h * 0.02}, scene);
      light.position.x = w * 0.4;
      light.position.y = c.yPos;
      light.position.z = d * 0.2;
      light.material = lightMat;
      light.parent = frame;
  });
};