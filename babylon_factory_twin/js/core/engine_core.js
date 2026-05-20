// 단일 책임 원칙: Engine 초기화와 Scene의 물리환경, 조명 세팅만 전담
window.initEngineCore = function(canvasId) {
  const deviceInfo = (() => {
    const userAgent = navigator.userAgent.toLowerCase();
    const isMobile = /android|webos|iphone|ipad|ipod|blackberry|windows phone/i.test(userAgent);
    return { isMobile, isPDA: isMobile && window.innerWidth <= 768, isPC: !isMobile };
  })();

  const canvas = document.getElementById(canvasId);
  const engine = new BABYLON.Engine(canvas, deviceInfo.isPC);
  if(deviceInfo.isMobile) engine.setHardwareScalingLevel(1.5);

  const scene = new BABYLON.Scene(engine);
  scene.collisionsEnabled = true;

  const hemiLight = new BABYLON.HemisphericLight('hemiLight', new BABYLON.Vector3(0, 1, 0), scene);
  hemiLight.intensity = 0.7;

  return { engine, scene, canvas, deviceInfo };
};
