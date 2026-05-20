// 단일 책임 원칙: DOM HTML 엘리먼트 통제, 기계 상태 표기, 팝업창(프롬프트) 관리 전담
window.initUIManager = function({ scene, cameraController, getFloorIdCallback, onTeleportTrigger }) {
  const machineInfo = document.getElementById('machine-info-content');
  const floorBtns = document.querySelectorAll('.floor-btn');
  const promptOverlay = document.getElementById('interaction-prompt');
  const btnEnter = document.getElementById('btn-enter-factory');
  const promptTitle = promptOverlay.querySelector('h2');
  
  let pendingTeleport = null;

  // 1. 프롬프트 다이얼로그 기능
  const executeTeleport = () => {
    if(!pendingTeleport) return;
    promptOverlay.style.display = 'none';
    onTeleportTrigger(pendingTeleport.floorId, pendingTeleport.x, pendingTeleport.z, pendingTeleport.msg);
    pendingTeleport = null;
  };

  window.addEventListener('keydown', e => { if(e.key === 'Enter' && pendingTeleport) executeTeleport(); });
  btnEnter.addEventListener('click', () => { if(pendingTeleport) executeTeleport(); });

  const setPrompt = (targetFloor, posX, posZ, title, btnText, msg) => {
    if (!pendingTeleport || pendingTeleport.floorId !== targetFloor) {
      pendingTeleport = { floorId: targetFloor, x: posX, z: posZ, msg: msg };
      promptTitle.innerText = title;
      btnEnter.innerText = btnText;
      promptOverlay.style.display = 'flex';
    }
  };

  const hidePrompt = () => {
    pendingTeleport = null;
    promptOverlay.style.display = 'none';
  };

  // 2. 우측 하단 미니맵 및 층수 버튼 조작
  floorBtns.forEach(btn => btn.addEventListener('click', e => {
    const targetId = e.target.getAttribute('data-floor');
    const fId = targetId === 'EXT' ? 'EXT' : parseInt(targetId);
    let msg = fId === 'EXT' ? '외부 조감도입니다.' : `${fId}층으로 이동했습니다.`;
    onTeleportTrigger(fId, cameraController.position.x, cameraController.position.z, msg);
  }));

  // 4. 설비 3D 폴리곤 클릭(Raycast) 처리
  scene.onPointerObservable.add(pointerInfo => {
    if(pointerInfo.type === BABYLON.PointerEventTypes.POINTERUP && pointerInfo.pickInfo.hit && pointerInfo.pickInfo.pickedMesh) {
      const machineData = pointerInfo.pickInfo.pickedMesh.metadata?.machineData;
      if(machineData) {
        const statusColor = machineData.status === 'RUNNING' ? '#28a745' : machineData.status === 'IDLE' ? '#ffc107' : '#dc3545';
        machineInfo.innerHTML = `
          <div style="margin-bottom: 8px;"><strong>설비 ID:</strong> ${machineData.machineId}</div>
          <div style="margin-bottom: 8px;"><strong>설비명칭:</strong> ${machineData.name}</div>
          <div style="margin-bottom: 8px;"><strong>가동상태:</strong> <span style="color: ${statusColor}; font-weight: bold;">${machineData.status}</span></div>
        `;
      } else {
        machineInfo.innerHTML = '<p>기계를 정확히 선택해 주세요.</p>';
      }
    }
  });

  const updateFloorBtnState = (floorId) => {
    floorBtns.forEach(b => b.classList.remove('active'));
    document.querySelector(`.floor-btn[data-floor="${floorId}"]`).classList.add('active');
  };

  const showSystemMessage = (msg) => { if (msg) machineInfo.innerHTML = `<p>${msg}</p>`; }

  return { setPrompt, hidePrompt, updateFloorBtnState, showSystemMessage };
};
