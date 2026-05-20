import type { IFloor, IMachine } from '../model/Types';

export const floors: IFloor[] = [
  { floorId: 0, name: '1F - 주 조립 라인', yOffset: 0, mapImageUrl: '/minimap_1f.png' },
  { floorId: 20, name: '2F - 정밀 가공 라인', yOffset: 20, mapImageUrl: '/minimap_2f.png' }
];

export const machines: IMachine[] = [
  // 1F Machines (yOffset: 0 + some base height if needed, assuming 0 is floor)
  { machineId: 'M1-1', name: 'CNC 머신 A', type: 'CNC', floorId: 0, position: { x: -10, y: 0, z: 10 }, rotation: { x: 0, y: 0, z: 0 }, status: 'RUNNING' },
  { machineId: 'M1-2', name: 'CNC 머신 B', type: 'CNC', floorId: 0, position: { x: 10, y: 0, z: 10 }, rotation: { x: 0, y: 0, z: 0 }, status: 'IDLE' },
  { machineId: 'M1-3', name: '로봇 암 A', type: 'ROBOT_ARM', floorId: 0, position: { x: 0, y: 0, z: 0 }, rotation: { x: 0, y: Math.PI / 4, z: 0 }, status: 'RUNNING' },
  { machineId: 'M1-4', name: '메인 컨베이어', type: 'CONVEYOR', floorId: 0, position: { x: 0, y: 0, z: -10 }, rotation: { x: 0, y: 0, z: 0 }, status: 'RUNNING' },
  { machineId: 'M1-5', name: '로봇 암 B', type: 'ROBOT_ARM', floorId: 0, position: { x: -15, y: 0, z: -5 }, rotation: { x: 0, y: Math.PI / 2, z: 0 }, status: 'ERROR' },

  // 2F Machines (yOffset: 20)
  { machineId: 'M2-1', name: '정밀 밀링기 A', type: 'CNC', floorId: 20, position: { x: -5, y: 20, z: 5 }, rotation: { x: 0, y: 0, z: 0 }, status: 'RUNNING' },
  { machineId: 'M2-2', name: '정밀 컷팅기 A', type: 'CNC', floorId: 20, position: { x: 5, y: 20, z: 5 }, rotation: { x: 0, y: 0, z: 0 }, status: 'IDLE' },
  { machineId: 'M2-3', name: '조립 로봇 X', type: 'ROBOT_ARM', floorId: 20, position: { x: -10, y: 20, z: -5 }, rotation: { x: 0, y: 0, z: 0 }, status: 'RUNNING' },
  { machineId: 'M2-4', name: '조립 로봇 Y', type: 'ROBOT_ARM', floorId: 20, position: { x: 10, y: 20, z: -5 }, rotation: { x: 0, y: 0, z: 0 }, status: 'ERROR' },
  { machineId: 'M2-5', name: '제품 검수기', type: 'CONVEYOR', floorId: 20, position: { x: 0, y: 20, z: -10 }, rotation: { x: 0, y: Math.PI / 2, z: 0 }, status: 'RUNNING' }
];
