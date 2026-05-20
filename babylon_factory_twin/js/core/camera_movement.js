// 단일 책임 원칙: 카메라 생성, 사용자 키보드 입력, 물리적인 아바타 캐릭터 이동 처리만 단독 수행
window.initCameraAndMovement = function({ scene, canvas, deviceInfo }) {
  // 카메라 초기화
  const cameraController = new BABYLON.UniversalCamera('CameraController', new BABYLON.Vector3(0, 2, -180), scene);
  cameraController.checkCollisions = true;
  cameraController.ellipsoid = new BABYLON.Vector3(1, 1, 1);
  cameraController.speed = window.FACTORY_CONFIG.SPEED.COLLISION_TEST;

  const viewCamera = new BABYLON.FreeCamera('ViewCamera', new BABYLON.Vector3(0, 5, -12), scene);
  viewCamera.parent = cameraController; 
  viewCamera.rotation = new BABYLON.Vector3(0.15, 0, 0); 
  scene.activeCamera = viewCamera; 

  // 플레이어 몸통 (아바타)
  const head = BABYLON.MeshBuilder.CreateSphere("head", {diameter: 0.8}, scene);
  head.position.y = 1.3;
  const body = BABYLON.MeshBuilder.CreateCylinder("body", {height: 1.5, diameterTop: 0.6, diameterBottom: 0.8}, scene);
  body.position.y = 0.15;
  const playerMesh = BABYLON.Mesh.MergeMeshes([head, body]);
  const pMat = new BABYLON.StandardMaterial("pMat", scene);
  pMat.diffuseColor = new BABYLON.Color3(1.0, 0.4, 0.0);
  playerMesh.material = pMat;
  playerMesh.isPickable = false;

  scene.onBeforeRenderObservable.add(() => {
    playerMesh.position = cameraController.position.subtract(new BABYLON.Vector3(0, 1.5, 0));
    playerMesh.rotation.y = cameraController.rotation.y;
  });

  const inputKeys = { up: false, down: false, left: false, right: false, w: false, a: false, s: false, d: false };

  // 모바일 및 PC 입력 제어
  if (deviceInfo.isPC) {
    canvas.addEventListener('mousedown', () => canvas.focus());
    canvas.focus();
  } else {
    const leftJoy = new BABYLON.VirtualJoystick(true);
    const rightJoy = new BABYLON.VirtualJoystick(false);
    if(BABYLON.VirtualJoystick.Canvas) {
      BABYLON.VirtualJoystick.Canvas.style.zIndex = '4';
      if(deviceInfo.isPDA) BABYLON.VirtualJoystick.Canvas.style.opacity = '0.6';
    }
    
    let initialDist = 0, initialFov = viewCamera.fov;
    canvas.addEventListener('touchstart', e => {
      if(e.touches.length === 2) {
        initialDist = Math.hypot(e.touches[0].pageX - e.touches[1].pageX, e.touches[0].pageY - e.touches[1].pageY);
        initialFov = viewCamera.fov;
      }
    }, {passive: false});
    canvas.addEventListener('touchmove', e => {
      if(e.touches.length === 2 && initialDist > 0) {
        const currentDist = Math.hypot(e.touches[0].pageX - e.touches[1].pageX, e.touches[0].pageY - e.touches[1].pageY);
        viewCamera.fov = Math.max(0.5, Math.min(initialFov * (initialDist / currentDist), 2.0));
      }
    }, {passive: false});

    scene.onBeforeRenderObservable.add(() => {
      if(leftJoy.pressed) {
        const fwd = cameraController.getDirection(BABYLON.Vector3.Forward()); const rt = cameraController.getDirection(BABYLON.Vector3.Right());
        fwd.y = 0; rt.y = 0; fwd.normalize(); rt.normalize();
        const move = rt.scale(leftJoy.deltaPosition.x).add(fwd.scale(leftJoy.deltaPosition.y));
        cameraController.position.addInPlace(move.scale(window.FACTORY_CONFIG.SPEED.MOVE));
      }
      if(rightJoy.pressed) {
        cameraController.rotation.y += rightJoy.deltaPosition.x * window.FACTORY_CONFIG.SPEED.ROTATE_MOBILE;
        cameraController.rotation.x -= rightJoy.deltaPosition.y * window.FACTORY_CONFIG.SPEED.ROTATE_MOBILE;
      }
    });
  }

  // 키보드 바인딩
  window.addEventListener('keydown', e => {
    if(e.key === 'ArrowUp') { inputKeys.up = true; e.preventDefault(); }
    if(e.key === 'ArrowDown') { inputKeys.down = true; e.preventDefault(); }
    if(e.key === 'ArrowLeft') { inputKeys.left = true; e.preventDefault(); }
    if(e.key === 'ArrowRight') { inputKeys.right = true; e.preventDefault(); }
    const key = e.key.toLowerCase();
    if(key === 'w') inputKeys.w = true;
    if(key === 's') inputKeys.s = true;
    if(key === 'a') inputKeys.a = true;
    if(key === 'd') inputKeys.d = true;
  });
  window.addEventListener('keyup', e => {
    if(e.key === 'ArrowUp') inputKeys.up = false;
    if(e.key === 'ArrowDown') inputKeys.down = false;
    if(e.key === 'ArrowLeft') inputKeys.left = false;
    if(e.key === 'ArrowRight') inputKeys.right = false;
    const key = e.key.toLowerCase();
    if(key === 'w') inputKeys.w = false;
    if(key === 's') inputKeys.s = false;
    if(key === 'a') inputKeys.a = false;
    if(key === 'd') inputKeys.d = false;
  });

  // 이동 실행 루프
  scene.onBeforeRenderObservable.add(() => {
    let moveZ = 0; let moveX = 0;
    if (inputKeys.w) moveZ += 1;
    if (inputKeys.s) moveZ -= 1;
    if (inputKeys.d) moveX += 1;
    if (inputKeys.a) moveX -= 1;

    if (moveZ !== 0 || moveX !== 0) {
      const fwd = cameraController.getDirection(BABYLON.Vector3.Forward()); 
      const rt = cameraController.getDirection(BABYLON.Vector3.Right());
      fwd.y = 0; rt.y = 0; fwd.normalize(); rt.normalize();
      const move = fwd.scale(moveZ).add(rt.scale(moveX));
      cameraController.position.addInPlace(move.scale(window.FACTORY_CONFIG.SPEED.MOVE));
    }

    const rotSpeed = window.FACTORY_CONFIG.SPEED.ROTATE_PC;
    if(inputKeys.up) cameraController.rotation.x -= rotSpeed;
    if(inputKeys.down) cameraController.rotation.x += rotSpeed;
    if(inputKeys.left) cameraController.rotation.y -= rotSpeed;
    if(inputKeys.right) cameraController.rotation.y += rotSpeed;
  });

  return cameraController;
};
