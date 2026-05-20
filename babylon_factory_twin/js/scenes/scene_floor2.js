window.buildSceneFloor2 = function(scene, machineDataArray) {
  const rootNode = new BABYLON.TransformNode("floor2Root", scene);
  scene.clearColor = window.FACTORY_CONFIG.COLORS.INTERIOR;

  const interiorEnclosure = BABYLON.MeshBuilder.CreateBox("interiorEnclosure2F", {width: window.FACTORY_CONFIG.WORLD_SIZE, height: 20, depth: window.FACTORY_CONFIG.WORLD_SIZE, sideOrientation: BABYLON.Mesh.BACKSIDE}, scene);
  interiorEnclosure.position = new BABYLON.Vector3(0, 30, 0); 
  interiorEnclosure.checkCollisions = true; 
  const enclosureMaterial = new BABYLON.StandardMaterial("encMat2F", scene);
  enclosureMaterial.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.9); 
  interiorEnclosure.material = enclosureMaterial;
  interiorEnclosure.parent = rootNode;

  const floorGround = BABYLON.MeshBuilder.CreateGround("ground_2F", { width: window.FACTORY_CONFIG.WORLD_SIZE, height: window.FACTORY_CONFIG.WORLD_SIZE }, scene);
  floorGround.position.y = 20.05; 
  floorGround.checkCollisions = true; 
  floorGround.parent = rootNode;
  const floorMaterial = new BABYLON.StandardMaterial("gMat_2F", scene);
  floorMaterial.diffuseColor = new BABYLON.Color3(0.5, 0.5, 0.6); 
  floorGround.material = floorMaterial;



  const safetyPathMaterial = new BABYLON.StandardMaterial("pathMat", scene);
  safetyPathMaterial.diffuseColor = new BABYLON.Color3(0.8, 0.8, 0.1);
  const safetyPathCenter = BABYLON.MeshBuilder.CreateBox("pathCenter2F", {width: 4, height: 0.1, depth: window.FACTORY_CONFIG.WORLD_SIZE}, scene);
  safetyPathCenter.position = new BABYLON.Vector3(0, 20.1, 0);
  safetyPathCenter.material = safetyPathMaterial; 
  safetyPathCenter.parent = rootNode;

  // 설비(기계) 생성 - 공통 빌더 모듈 사용
  machineDataArray.filter(machineData => machineData.floorId === 20).forEach(machineData => {
    const machineMesh = window.createMachineMesh(scene, machineData);
    machineMesh.parent = rootNode;
  });

  const previousFloorElevator = BABYLON.MeshBuilder.CreateCylinder("portal_20", {diameter: 10, height: 6}, scene);
  previousFloorElevator.position = new BABYLON.Vector3(window.FACTORY_CONFIG.PORTAL.ELEVATOR_2F_X, window.FACTORY_CONFIG.PORTAL.ELEVATOR_2F_Y + 1, window.FACTORY_CONFIG.PORTAL.ELEVATOR_2F_Z); 
  const elevatorMaterial = new BABYLON.StandardMaterial("portalMat_20", scene);
  elevatorMaterial.diffuseColor = BABYLON.Color3.Purple(); 
  elevatorMaterial.alpha = 0.4; 
  previousFloorElevator.material = elevatorMaterial;
  previousFloorElevator.parent = rootNode; 
  previousFloorElevator.checkCollisions = false;

  return rootNode;
};
