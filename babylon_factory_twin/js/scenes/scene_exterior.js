window.buildSceneExterior = function(scene) {
  const rootNode = new BABYLON.TransformNode("extRoot", scene);

  scene.clearColor = window.FACTORY_CONFIG.COLORS.SKY;

  const worldGround = BABYLON.MeshBuilder.CreateGround("worldGround", {width: 2000, height: 2000}, scene);
  worldGround.position.y = -0.1;
  const worldMaterial = new BABYLON.StandardMaterial("wMat", scene);
  worldMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.4, 0.2); 
  worldGround.material = worldMaterial;
  worldGround.checkCollisions = true; 
  worldGround.parent = rootNode;

  const exteriorBox = BABYLON.MeshBuilder.CreateBox("factoryExt", {width: window.FACTORY_CONFIG.WORLD_SIZE + 2, height: 40, depth: window.FACTORY_CONFIG.WORLD_SIZE + 2}, scene);
  exteriorBox.position = new BABYLON.Vector3(0, 20, 0); 
  const exteriorMaterial = new BABYLON.StandardMaterial("matExt", scene);
  exteriorMaterial.diffuseColor = new BABYLON.Color3(0.7, 0.72, 0.75); 
  exteriorMaterial.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2); 
  exteriorBox.material = exteriorMaterial; 
  exteriorBox.checkCollisions = true; 
  exteriorBox.parent = rootNode;

  const redDividerStripe = BABYLON.MeshBuilder.CreateBox("divider", {width: window.FACTORY_CONFIG.WORLD_SIZE + 3, height: 1.5, depth: window.FACTORY_CONFIG.WORLD_SIZE + 3}, scene);
  redDividerStripe.position = new BABYLON.Vector3(0, 20, 0);
  const dividerMaterial = new BABYLON.StandardMaterial("divMat", scene);
  dividerMaterial.diffuseColor = new BABYLON.Color3(0.8, 0.2, 0.2); 
  redDividerStripe.material = dividerMaterial; 
  redDividerStripe.parent = rootNode;

  const factoryRoof = BABYLON.MeshBuilder.CreateBox("roof", {width: window.FACTORY_CONFIG.WORLD_SIZE + 4, height: 2, depth: window.FACTORY_CONFIG.WORLD_SIZE + 4}, scene);
  factoryRoof.position = new BABYLON.Vector3(0, 41, 0);
  const roofMaterial = new BABYLON.StandardMaterial("roofMat", scene);
  roofMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.2, 0.22); 
  factoryRoof.material = roofMaterial; 
  factoryRoof.parent = rootNode;

  const mainEntranceDoor = BABYLON.MeshBuilder.CreateBox("entranceDoor", {width: 30, height: 12, depth: 2}, scene);
  mainEntranceDoor.position = new BABYLON.Vector3(0, 6, window.FACTORY_CONFIG.PORTAL.EXT_ENTRANCE_Z - 1); 
  const doorPanelMaterial = new BABYLON.StandardMaterial("doorMat", scene);
  doorPanelMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.25, 0.3); 
  mainEntranceDoor.material = doorPanelMaterial;
  mainEntranceDoor.parent = rootNode;

  const entranceMarkerArea = BABYLON.MeshBuilder.CreateBox("entranceMarker", {width: 40, height: 0.2, depth: 15}, scene);
  entranceMarkerArea.position = new BABYLON.Vector3(0, 0.1, window.FACTORY_CONFIG.PORTAL.EXT_ENTRANCE_Z - 7);
  const markerMaterial = new BABYLON.StandardMaterial("entMat", scene);
  markerMaterial.diffuseColor = new BABYLON.Color3(0.1, 0.5, 0.9);
  entranceMarkerArea.material = markerMaterial; 
  entranceMarkerArea.parent = rootNode;

  return rootNode;
};
