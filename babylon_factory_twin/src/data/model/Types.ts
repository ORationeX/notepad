// 1. 층(Floor) 정보 DB
export interface IFloor {
  floorId: number;
  name: string;
  yOffset: number; // 3D 공간의 Y축 높이 (예: 1층은 0, 2층은 20)
  mapImageUrl: string; // 미니맵 2D 도면 이미지
}

// 2. 기계 및 설비(Machine) 정보 DB
export interface IMachine {
  machineId: string;
  name: string;
  type: 'CNC' | 'ROBOT_ARM' | 'CONVEYOR';
  floorId: number; // 0 for 1F, 20 for 2F usually maps to IFloor.yOffset/floorId
  position: { x: number, y: number, z: number };
  rotation: { x: number, y: number, z: number };
  status: 'RUNNING' | 'IDLE' | 'ERROR';
}
