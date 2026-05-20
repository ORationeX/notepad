// 단일 책임 원칙: 플레이어의 현재 위치가 텔레포트 존과 겹치는지만 감시수행 + 포털 시각화 가시성 제어
window.initPortalManager = function({ scene, cameraController, getFloorIdCallback, onShowPrompt, onHidePrompt, onTeleportTrigger }) {
  
  let currentVisuals = [];
  let lastFloorId = null;

  const PORTAL_CONFIG = window.FACTORY_CONFIG.PORTAL;

  // 헬퍼: 텍스트 라벨 메시 생성
  const createPortalLabel = (text, position) => {
    const container = new BABYLON.TransformNode("portal_node", scene);
    container.position = position;

    // 1. 하단 링 (물리적 영역 표시)
    const ring = BABYLON.MeshBuilder.CreateTorus("portal_ring", { diameter: 8, thickness: 0.3, tessellation: 32 }, scene);
    ring.parent = container;
    ring.position.y = 0.1;
    const ringMat = new BABYLON.StandardMaterial("ring_mat", scene);
    ringMat.emissiveColor = new BABYLON.Color3(0, 0.6, 1);
    ringMat.alpha = 0.4;
    ring.material = ringMat;

    // 가벼운 애니메이션 추가
    const observer = scene.onBeforeRenderObservable.add(() => {
      if (ring.isDisposed()) {
        scene.onBeforeRenderObservable.remove(observer);
      } else {
        ring.rotation.y += 0.02;
      }
    });

    // 2. 상단 라벨 (텍스트 표기)
    const plane = BABYLON.MeshBuilder.CreatePlane("portal_label", { width: 12, height: 6 }, scene);
    plane.parent = container;
    plane.position.y = 8;
    plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;

    const texture = new BABYLON.DynamicTexture("portal_tex", { width: 512, height: 256 }, scene);
    const material = new BABYLON.StandardMaterial("portal_label_mat", scene);
    material.diffuseTexture = texture;
    material.emissiveColor = new BABYLON.Color3(1, 1, 1);
    material.opacityTexture = texture;
    material.backFaceCulling = false;
    plane.material = material;

    // 텍스트 그리기 (그림자 효과로 가독성 향상)
    const ctx = texture.getContext();
    ctx.shadowColor = "black";
    ctx.shadowBlur = 10;
    texture.drawText(text, null, null, "bold 100px Inter", "white", "transparent", true);

    currentVisuals.push(container);
  };

  const refreshPortalVisuals = (floorId) => {
    // 기존 가시 객체 삭제
    currentVisuals.forEach(v => v.dispose());
    currentVisuals = [];

    // 현재 층에 맞는 포털 시각물 생성
    if (floorId === 'EXT') {
      // 건물 외벽(Z=-126)보다 바깥쪽인 Z=-140 지점에 배치하여 가려짐 방지
      createPortalLabel("1층 공장", new BABYLON.Vector3(0, 0, PORTAL_CONFIG.EXT_ENTRANCE_Z - 15));
    } else if (floorId === 0) {
      // 1층 출구: 건물 안쪽(Z=-120)에 배치되어 있어 잘 보임
      createPortalLabel("공장 외부", new BABYLON.Vector3(0, 0, PORTAL_CONFIG.FLOOR1_EXIT_Z));
      createPortalLabel("2층 이동", new BABYLON.Vector3(PORTAL_CONFIG.ELEVATOR_1F_X, 0, PORTAL_CONFIG.ELEVATOR_1F_Z));
    } else if (floorId === 20) {
      createPortalLabel("1층 이동", new BABYLON.Vector3(PORTAL_CONFIG.ELEVATOR_2F_X, 20, PORTAL_CONFIG.ELEVATOR_2F_Z));
    }
  };

  scene.onBeforeRenderObservable.add(() => {
    const currentPosition = cameraController.position;
    const currentFloorId = getFloorIdCallback();
    let isCurrentlyNearPortal = false;
    
    // 층이 바뀌었을 때 시각물 교체
    if (currentFloorId !== lastFloorId) {
      refreshPortalVisuals(currentFloorId);
      lastFloorId = currentFloorId;
    }

    const PORTAL = window.FACTORY_CONFIG.PORTAL;

    // 수동 퇴장/입장 문 상호작용
    if (currentFloorId === 'EXT') {
      const entrancePos = new BABYLON.Vector3(0, 2, PORTAL.EXT_ENTRANCE_Z);
      if (BABYLON.Vector3.Distance(currentPosition, entrancePos) < PORTAL.EXT_ENTRANCE_TOLERANCE) {
        isCurrentlyNearPortal = true;
        onShowPrompt(0, 0, PORTAL.FLOOR1_SPAWN_Z, '1층 공장에 입장하시겠습니까?', '입장하기', '1층 공장에 진입했습니다.');
      }
    } else if (currentFloorId === 0) {
      const exitPos = new BABYLON.Vector3(0, 2, PORTAL.FLOOR1_EXIT_Z);
      if (BABYLON.Vector3.Distance(currentPosition, exitPos) < PORTAL.FLOOR1_EXIT_TOLERANCE) {
        isCurrentlyNearPortal = true;
        onShowPrompt('EXT', 0, PORTAL.FLOOR1_EXIT_SPAWN_Z, '공장 외부로 나가시겠습니까?', '퇴장하기', '공장 외부로 퇴장했습니다.');
      }
    }

    if (!isCurrentlyNearPortal) {
      onHidePrompt();
    }

    // 엘리베이터(자동 텔레포트) 진입 체크
    if (currentFloorId === 0) {
      const e1f = new BABYLON.Vector3(PORTAL.ELEVATOR_1F_X, PORTAL.ELEVATOR_1F_Y, PORTAL.ELEVATOR_1F_Z);
      if (BABYLON.Vector3.Distance(currentPosition, e1f) < PORTAL.ELEVATOR_TOLERANCE) {
        onTeleportTrigger(20, PORTAL.ELEVATOR_SPAWN_X, PORTAL.ELEVATOR_2F_Z, '2층으로 이동했습니다.');
      }
    } else if (currentFloorId === 20) {
      const e2f = new BABYLON.Vector3(PORTAL.ELEVATOR_2F_X, PORTAL.ELEVATOR_2F_Y, PORTAL.ELEVATOR_2F_Z);
      if (BABYLON.Vector3.Distance(currentPosition, e2f) < PORTAL.ELEVATOR_TOLERANCE) {
        onTeleportTrigger(0, PORTAL.ELEVATOR_SPAWN_X, PORTAL.ELEVATOR_1F_Z, '1층으로 이동했습니다.');
      }
    }
  });
};
