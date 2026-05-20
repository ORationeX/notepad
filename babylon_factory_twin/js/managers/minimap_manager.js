// 단일 책임 원칙: 미니맵 표시 및 미니맵을 통한 텔레포트 기능 전담
window.initMinimapManager = function({ scene, cameraController, getFloorIdCallback, onTeleportTrigger, machineDataArray }) {
  const playerIndicator = document.getElementById('player-indicator');
  const minimapArea = document.getElementById('minimap-canvas-area');
  const minimapToggle = document.getElementById('minimap-toggle');
  const minimapWrapper = document.getElementById('minimap-wrapper');

  let lastFloorId = null;

  // 1. 공장 외벽 표기 (캔버스 테두리 근처에 상시 배치)
  const factoryWall = document.createElement('div');
  factoryWall.style.position = 'absolute';
  factoryWall.style.left = '1%';
  factoryWall.style.top = '1%';
  factoryWall.style.width = '98%';
  factoryWall.style.height = '98%';
  factoryWall.style.border = '2px solid rgba(255, 255, 255, 0.3)';
  factoryWall.style.borderRadius = '4px';
  factoryWall.style.pointerEvents = 'none';
  minimapArea.appendChild(factoryWall);

  const clearMachineMarkers = () => {
    const oldMarkers = minimapArea.querySelectorAll('.machine-marker');
    oldMarkers.forEach(m => m.remove());
  };

  const drawMachineMarkers = (floorId) => {
    clearMachineMarkers();
    
    // 'EXT' 층일 때에도 미니맵 내부 표기를 완전히 지우고 리턴
    if (floorId === 'EXT') return; 

    const FACTORY_SIZE = window.FACTORY_CONFIG?.WORLD_SIZE || 250;
    
    if (!machineDataArray || machineDataArray.length === 0) return;

    machineDataArray.forEach(m => {
        // 숫자/문자열 타입 불일치 방지 (0 vs "0")
        if (String(m.floorId) === String(floorId)) {
          const marker = document.createElement('div');
          marker.className = 'machine-marker';
          marker.style.position = 'absolute';
          marker.style.width = '12px';
          marker.style.height = '12px';
          marker.style.borderRadius = '50%';
          marker.style.zIndex = '100'; // 격자 위에 확연히 보이도록 설정
          marker.style.border = '2px solid rgba(255, 255, 255, 0.8)';
          marker.style.display = 'block'; 
          marker.style.opacity = '1';
        
        // 마우스 오버 시 정보 표시 속성
        marker.title = `[${m.machineId}] ${m.name}\n상태: ${m.status}`;
        
        // 상태별 색상 (그린/옐로우/레드)
        const color = m.status === 'RUNNING' ? '#28a745' : m.status === 'IDLE' ? '#ffc107' : '#dc3545';
        marker.style.backgroundColor = color;
        marker.style.boxShadow = `0 0 10px ${color}`;

        // 좌표 변환 (Babylon X,Z -> Minimap %, %) - position 객체 안전성 확인
        const posX = m.position?.x || 0;
        const posZ = m.position?.z || 0;
        
        const xp = ((posX + FACTORY_SIZE / 2) / FACTORY_SIZE) * 100;
        const zp = ((-posZ + FACTORY_SIZE / 2) / FACTORY_SIZE) * 100;
        
        marker.style.left = xp + '%';
        marker.style.top = zp + '%';
        marker.style.transform = 'translate(-50%, -50%)';
        // 마커 클릭이나 호버를 위해 pointer-events를 auto로 변경
        marker.style.pointerEvents = 'auto';
        marker.style.cursor = 'pointer';

        // 텍스트 라벨 추가 (설비 ID)
        const label = document.createElement('div');
        label.innerText = m.machineId;
        label.style.position = 'absolute';
        label.style.top = '-16px';
        label.style.left = '50%';
        label.style.transform = 'translateX(-50%)';
        label.style.color = '#fff';
        label.style.fontSize = '9px';
        label.style.whiteSpace = 'nowrap';
        label.style.fontWeight = 'bold';
        label.style.textShadow = '1px 1px 2px #000, -1px -1px 2px #000, 1px -1px 2px #000, -1px 1px 2px #000';
        label.style.pointerEvents = 'none'; // 라벨 자체가 클릭을 가로채지 않게 함
        
        marker.appendChild(label);
        
        // 마커 클릭 시 정보창(좌측 상단 Status Panel) 업데이트 연동 (선택사항)
        marker.addEventListener('click', (e) => {
          e.stopPropagation(); // 텔레포트 클릭 방지
          const machineInfo = document.getElementById('machine-info-content');
          if(machineInfo) {
            machineInfo.innerHTML = `
              <div style="margin-bottom: 8px;"><strong>설비 ID:</strong> ${m.machineId}</div>
              <div style="margin-bottom: 8px;"><strong>설비명칭:</strong> ${m.name}</div>
              <div style="margin-bottom: 8px;"><strong>가동상태:</strong> <span style="color: ${color}; font-weight: bold;">${m.status}</span></div>
            `;
          }
        });
        
        minimapArea.appendChild(marker);
      }
    });
  };

  // 2. 미니맵 네비게이션 루프 (플레이어 위치 및 층 변경 감지)
  scene.onBeforeRenderObservable.add(() => {
    const currentFloorId = getFloorIdCallback();
    
    // 층이 바뀌면 기계 마커 갱신
    if (currentFloorId !== lastFloorId) {
      console.log(`Floor changed to ${currentFloorId}. Redrawing markers.`);
      drawMachineMarkers(currentFloorId);
      lastFloorId = currentFloorId;
    }

    if (!playerIndicator) return;
    
    const cameraPos = cameraController.position;
    const FACTORY_SIZE = window.FACTORY_CONFIG.WORLD_SIZE;
    
    // 월드 좌표를 미니맵 퍼센트 좌표로 변환
    const xp = Math.max(0, Math.min(((cameraPos.x + FACTORY_SIZE / 2) / FACTORY_SIZE) * 100, 100));
    const zp = Math.max(0, Math.min(((-cameraPos.z + FACTORY_SIZE / 2) / FACTORY_SIZE) * 100, 100));
    
    playerIndicator.style.left = xp + '%'; 
    playerIndicator.style.top = zp + '%';
  });

  // 2. 미니맵 클릭 시 해당 위치로 텔레포트
  const doTeleportMap = (x, y, rect) => {
    const FACTORY_SIZE = window.FACTORY_CONFIG.WORLD_SIZE;
    const mapX = (x / rect.width) * FACTORY_SIZE - (FACTORY_SIZE / 2);
    const mapZ = -((y / rect.height) * FACTORY_SIZE - (FACTORY_SIZE / 2));
    
    onTeleportTrigger(getFloorIdCallback(), mapX, mapZ, '선택한 위치로 이동했습니다.');
  };

  minimapArea.addEventListener('click', e => {
    const rect = minimapArea.getBoundingClientRect();
    doTeleportMap(e.clientX - rect.left, e.clientY - rect.top, rect);
  });

  minimapArea.addEventListener('touchstart', e => {
    const rect = minimapArea.getBoundingClientRect();
    doTeleportMap(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top, rect);
    e.preventDefault();
  }, { passive: false });

  // 3. 미니맵 토글 (모바일용)
  if (minimapToggle) {
    minimapToggle.addEventListener('click', () => {
      minimapWrapper.classList.toggle('show');
    });
  }
};
