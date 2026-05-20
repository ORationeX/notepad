// 단일 책임 원칙: 씬 파일들을 호출해 메모리에 쌓거나 파괴하고, 현재 활성화된 씬 층수 식별만 전담
window.initSceneManager = function({ scene, machineDataArray }) {
  let currentFloorRoot = null;
  let currentFloorId = 'EXT';

  const loadSceneData = (floorId) => {
    // 메모리 누수를 방지하기 위해 이전 화면 물리객체 통째로 삭제
    if (currentFloorRoot) {
      currentFloorRoot.dispose();
      currentFloorRoot = null;
    }
    
    // 타겟 구역 렌더링 함수 로드
    if (floorId === 'EXT') {
      currentFloorRoot = window.buildSceneExterior(scene);
    } else if (floorId === 0) {
      currentFloorRoot = window.buildSceneFloor1(scene, machineDataArray);
    } else if (floorId === 20) {
      currentFloorRoot = window.buildSceneFloor2(scene, machineDataArray);
    }
    
    currentFloorId = floorId;
  };

  const getCurrentFloorId = () => currentFloorId;

  return { loadSceneData, getCurrentFloorId };
};
