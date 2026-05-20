window.onload = function() {
  const machineDataArray = window.getMockMachineData();
  const engineCore = window.initEngineCore("renderCanvas");
  
  const cameraController = window.initCameraAndMovement({
    scene: engineCore.scene,
    canvas: engineCore.canvas,
    deviceInfo: engineCore.deviceInfo
  });

  const sceneManager = window.initSceneManager({
    scene: engineCore.scene,
    machineDataArray: machineDataArray
  });

  const handleTeleportExecution = (floorId, spawnPositionX, spawnPositionZ, systemMessage) => {
    sceneManager.loadSceneData(floorId);
    uiManager.updateFloorBtnState(floorId);
    uiManager.showSystemMessage(systemMessage);
    
    if (floorId === 'EXT') {
      cameraController.position = new BABYLON.Vector3(0, 2, -180);
      cameraController.rotation = new BABYLON.Vector3(0, 0, 0);
    } else {
      cameraController.position = new BABYLON.Vector3(spawnPositionX, parseInt(floorId) + 2, spawnPositionZ);
    }
  };

  const uiManager = window.initUIManager({
    scene: engineCore.scene,
    cameraController: cameraController,
    getFloorIdCallback: sceneManager.getCurrentFloorId,
    onTeleportTrigger: handleTeleportExecution
  });
  
  window.initMinimapManager({
    scene: engineCore.scene,
    cameraController: cameraController,
    getFloorIdCallback: sceneManager.getCurrentFloorId,
    onTeleportTrigger: handleTeleportExecution,
    machineDataArray: machineDataArray
  });

  window.initPortalManager({
    scene: engineCore.scene,
    cameraController: cameraController,
    getFloorIdCallback: sceneManager.getCurrentFloorId,
    onShowPrompt: uiManager.setPrompt,
    onHidePrompt: uiManager.hidePrompt,
    onTeleportTrigger: handleTeleportExecution
  });

  // 초기 렌더링 로드 시작
  sceneManager.loadSceneData('EXT');

  engineCore.scene.executeWhenReady(() => {
    const loadingOverlay = document.getElementById("loading-screen");
    loadingOverlay.style.opacity = "0";
    setTimeout(() => loadingOverlay.style.display = "none", 500);
  });

  engineCore.engine.runRenderLoop(() => {
    engineCore.scene.render();
  });

  window.addEventListener('resize', () => engineCore.engine.resize());
};
