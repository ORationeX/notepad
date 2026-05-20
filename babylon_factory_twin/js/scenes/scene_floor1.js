window.buildSceneFloor1 = function(scene, machineDataArray) {
  const rootNode = new BABYLON.TransformNode("floor1Root", scene);
  
  // 첨단 산업 / 클린룸 느낌을 위한 밝은 실내 컬러 설정
  scene.clearColor = new BABYLON.Color4(0.95, 0.95, 0.98, 1);

  // 공장 외벽 (밝고 깨끗한 화이트톤 벽면)
  const enclosedBox = BABYLON.MeshBuilder.CreateBox("interiorEnclosure1F", {width: window.FACTORY_CONFIG.WORLD_SIZE, height: 20, depth: window.FACTORY_CONFIG.WORLD_SIZE, sideOrientation: BABYLON.Mesh.BACKSIDE}, scene);
  enclosedBox.position = new BABYLON.Vector3(0, 10, 0);
  enclosedBox.checkCollisions = true; 
  const enclosureMaterial = new BABYLON.StandardMaterial("encMat1F", scene);
  enclosureMaterial.diffuseColor = new BABYLON.Color3(0.92, 0.93, 0.95); 
  enclosureMaterial.emissiveColor = new BABYLON.Color3(0.1, 0.1, 0.12); // 실내 전체가 살짝 밝은 느낌
  enclosedBox.material = enclosureMaterial;
  enclosedBox.parent = rootNode;

  // 바닥 (광택이 나는 밝은 에폭시 바닥)
  const floorGround = BABYLON.MeshBuilder.CreateGround("ground_1F", { width: window.FACTORY_CONFIG.WORLD_SIZE, height: window.FACTORY_CONFIG.WORLD_SIZE }, scene);
  floorGround.position.y = 0.05; 
  floorGround.checkCollisions = true; 
  floorGround.parent = rootNode;
  const floorMaterial = new BABYLON.StandardMaterial("gMat_1F", scene);
  floorMaterial.diffuseColor = new BABYLON.Color3(0.85, 0.88, 0.9); // 약간 푸른빛이 도는 밝은 회색
  floorMaterial.specularColor = new BABYLON.Color3(0.8, 0.8, 0.8);
  floorMaterial.specularPower = 32; // 반사광을 선명하게
  floorGround.material = floorMaterial;



  // 동선 마킹 (파란색 클린룸 가이드 라인)
  const safetyPathMaterial = new BABYLON.StandardMaterial("pathMat", scene);
  safetyPathMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.5, 0.9);
  safetyPathMaterial.emissiveColor = new BABYLON.Color3(0.1, 0.2, 0.4);
  const safetyPathCenter = BABYLON.MeshBuilder.CreateBox("pathCenter", {width: 8, height: 0.1, depth: window.FACTORY_CONFIG.WORLD_SIZE}, scene);
  safetyPathCenter.position = new BABYLON.Vector3(0, 0.1, 0);
  safetyPathCenter.material = safetyPathMaterial; 
  safetyPathCenter.parent = rootNode;

  // 설비(기계) 생성 - 공통 빌더 모듈 사용
  machineDataArray.filter(machineData => machineData.floorId === 0).forEach(machineData => {
    const machineMesh = window.createMachineMesh(scene, machineData);
    machineMesh.parent = rootNode;
  });

  const nextFloorElevator = BABYLON.MeshBuilder.CreateCylinder("portal_0", {diameter: 10, height: 6}, scene);
  nextFloorElevator.position = new BABYLON.Vector3(window.FACTORY_CONFIG.PORTAL.ELEVATOR_1F_X, window.FACTORY_CONFIG.PORTAL.ELEVATOR_1F_Y + 1, window.FACTORY_CONFIG.PORTAL.ELEVATOR_1F_Z);
  const elevatorMaterial = new BABYLON.StandardMaterial("portalMat_0", scene);
  elevatorMaterial.diffuseColor = BABYLON.Color3.Teal(); 
  elevatorMaterial.alpha = 0.4; 
  nextFloorElevator.material = elevatorMaterial;
  nextFloorElevator.parent = rootNode; 
  nextFloorElevator.checkCollisions = false;

  const backExitDoor = BABYLON.MeshBuilder.CreateBox("exit_EXT", {width: 15, height: 10, depth: 1}, scene);
  backExitDoor.position = new BABYLON.Vector3(0, 5, window.FACTORY_CONFIG.PORTAL.FLOOR1_EXIT_Z - 4.5); 
  const doorPanelMaterial = new BABYLON.StandardMaterial("exitMat", scene);
  doorPanelMaterial.diffuseColor = new BABYLON.Color3(0.9, 0.1, 0.1); 
  doorPanelMaterial.emissiveColor = new BABYLON.Color3(0.4, 0, 0);
  backExitDoor.material = doorPanelMaterial;
  backExitDoor.checkCollisions = false;
  backExitDoor.parent = rootNode;

  const backExitMarkerArea = BABYLON.MeshBuilder.CreateBox("exitMarker", {width: 20, height: 0.2, depth: 10}, scene);
  backExitMarkerArea.position = new BABYLON.Vector3(0, 0.15, window.FACTORY_CONFIG.PORTAL.FLOOR1_EXIT_Z);
  backExitMarkerArea.material = doorPanelMaterial; 
  backExitMarkerArea.parent = rootNode;

  return rootNode;
};
