window.getMockMachineData = function() {
  const machines = [];
  
  // -- 1층: 세정, 조립, 코팅, 경화, 검사 전체 통합 라인 -- //
  
  // 1. 코팅 라인 (좌측 외부 라인: x = -60)
  machines.push({ machineId: `CT-1`, name: `컨포멀 코팅기`, type: 'CONFORMAL_COATING', floorId: 0, position: {x: -60, y: 0, z: -60}, rotation: {x:0, y:Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `CT-2`, name: `코팅 3D 검사기`, type: 'COATING_AOI', floorId: 0, position: {x: -60, y: 0, z: -40}, rotation: {x:0, y:Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `TR-1`, name: `코팅 대기 트레이`, type: 'ANTISTATIC_TRAY', floorId: 0, position: {x: -60, y: 0, z: -20}, rotation: {x:0, y:0, z:0}, status: 'IDLE', size: {w: 10, h: 10, d: 10} });

  // 2. 세정 라인 (좌측 내부 라인: x = -25)
  machines.push({ machineId: `CL-1`, name: `습식 세정기`, type: 'WET_CLEANING', floorId: 0, position: {x: -25, y: 0, z: -60}, rotation: {x:0, y:Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `CL-2`, name: `초음파 세정기`, type: 'ULTRASONIC_CLEANING', floorId: 0, position: {x: -25, y: 0, z: -40}, rotation: {x:0, y:Math.PI/2, z:0}, status: 'IDLE', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `CL-3`, name: `플라즈마 세정`, type: 'PLASMA_CLEANING', floorId: 0, position: {x: -25, y: 0, z: -20}, rotation: {x:0, y:Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });

  // 3. 조립 라인 (우측 내부 라인: x = 25)
  machines.push({ machineId: `AS-1`, name: `PCB 조립기`, type: 'PCB_ASSEMBLY', floorId: 0, position: {x: 25, y: 0, z: -60}, rotation: {x:0, y:-Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `AS-2`, name: `액티브 얼라인`, type: 'ACTIVE_ALIGNMENT', floorId: 0, position: {x: 25, y: 0, z: -40}, rotation: {x:0, y:-Math.PI/2, z:0}, status: 'ERROR', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `AS-3`, name: `카메라 조립`, type: 'CAMERA_SCREW_ASSEMBLY', floorId: 0, position: {x: 25, y: 0, z: -20}, rotation: {x:0, y:-Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });

  // 4. 경화/FW 라인 (우측 외부 라인: x = 60)
  machines.push({ machineId: `CU-1`, name: `경화 오븐`, type: 'CURING_OVEN', floorId: 0, position: {x: 60, y: 0, z: -60}, rotation: {x:0, y:-Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `FW-1`, name: `FW 다운로드`, type: 'FIRMWARE_DOWNLOAD', floorId: 0, position: {x: 60, y: 0, z: -40}, rotation: {x:0, y:-Math.PI/2, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `TR-2`, name: `조립 완료 트레이`, type: 'ANTISTATIC_TRAY', floorId: 0, position: {x: 60, y: 0, z: -20}, rotation: {x:0, y:0, z:0}, status: 'IDLE', size: {w: 10, h: 10, d: 10} });

  // 5. 검사 통합 라인 (중앙 앞쪽 구역, 일렬 횡대)
  let insZ = 25;
  machines.push({ machineId: `IN-1`, name: `내부변수 캘리브레이션`, type: 'INTRINSIC_CALIBRATION', floorId: 0, position: {x: -60, y: 0, z: insZ}, rotation: {x:0, y:0, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `IN-2`, name: `비전 검사기`, type: 'VISION_INSPECTION', floorId: 0, position: {x: -30, y: 0, z: insZ}, rotation: {x:0, y:0, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `IN-3`, name: `지향각 테스트`, type: 'DIRECTIONAL_ANGLE_TEST', floorId: 0, position: {x: 0, y: 0, z: insZ}, rotation: {x:0, y:0, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `IN-4`, name: `핀 검사기`, type: 'PIN_INSPECTION', floorId: 0, position: {x: 30, y: 0, z: insZ}, rotation: {x:0, y:0, z:0}, status: 'IDLE', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `IN-5`, name: `최종 화상 검사`, type: 'FINAL_OPTICAL_TEST', floorId: 0, position: {x: 60, y: 0, z: insZ}, rotation: {x:0, y:0, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  
  // 6. EOL 최종 라인 (가장 앞쪽 중앙)
  machines.push({ machineId: `IN-6`, name: `EOL 종합검사`, type: 'EOL_TEST', floorId: 0, position: {x: -15, y: 0, z: insZ+30}, rotation: {x:0, y:Math.PI, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });
  machines.push({ machineId: `TR-3`, name: `최종 출고 패키징`, type: 'ANTISTATIC_TRAY', floorId: 0, position: {x: 15, y: 0, z: insZ+30}, rotation: {x:0, y:0, z:0}, status: 'RUNNING', size: {w: 10, h: 10, d: 10} });

  return machines;
};
