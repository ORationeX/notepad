// 단일 책임 원칙: 기계 타입에 따른 3D 모델링 생성 및 상태별 머티리얼 적용 전담 (팩토리 패턴)
window.createMachineMesh = function(scene, machineData) {
  const size = machineData.size || { w: 10, h: 10, d: 10 };
  // 1. 투명한 히트박스(Root) 생성 - 모든 기계의 공통 클릭 영역
  const machineMesh = BABYLON.MeshBuilder.CreateBox(machineData.machineId, { width: size.w, height: size.h, depth: size.d }, scene);
  machineMesh.visibility = 0; 

  // 2. 타입별 하위 모델링 호출 (각 전용 스크립트에서 빌드)
  const builders = {
    'WET_CLEANING': window.buildWetCleaningModel,
    'ULTRASONIC_CLEANING': window.buildUltrasonicCleaningModel,
    'PLASMA_CLEANING': window.buildPlasmaCleaningModel,
    'PCB_ASSEMBLY': window.buildPcbAssemblyModel,
    'ACTIVE_ALIGNMENT': window.buildActiveAlignmentModel,
    'CAMERA_SCREW_ASSEMBLY': window.buildCameraScrewAssemblyModel,
    'CURING_OVEN': window.buildCuringOvenModel,
    'FIRMWARE_DOWNLOAD': window.buildFirmwareDownloadModel,
    'INTRINSIC_CALIBRATION': window.buildIntrinsicCalibrationModel,
    'VISION_INSPECTION': window.buildVisionInspectionModel,
    'DIRECTIONAL_ANGLE_TEST': window.buildDirectionalAngleTestModel,
    'PIN_INSPECTION': window.buildPinInspectionModel,
    'FINAL_OPTICAL_TEST': window.buildFinalOpticalTesterModel,
    'EOL_TEST': window.buildEolTesterModel,
    'CONFORMAL_COATING': window.buildConformalCoatingModel,
    'COATING_AOI': window.buildCoatingAoiModel,
    'ANTISTATIC_TRAY': window.buildAntistaticTrayModel
  };

  if (builders[machineData.type]) {
    builders[machineData.type](scene, machineMesh);
  } else {
    // 기본 플레이스홀더
    const placeholder = BABYLON.MeshBuilder.CreateBox("placeholder", { size: 4 }, scene);
    placeholder.parent = machineMesh;
    placeholder.material = new BABYLON.StandardMaterial("phMat", scene);
    placeholder.material.diffuseColor = BABYLON.Color3.Gray();
  }

  // 3. 상태 표시 (타워 램프 제어)
  let activeColor = "grn";
  if (machineData.status === 'RUNNING') activeColor = "grn";
  else if (machineData.status === 'IDLE') activeColor = "yel";
  else activeColor = "red";

  let hasTowerLight = false;
  machineMesh.getChildMeshes().forEach(m => {
    const name = m.name.toLowerCase();
    // 타워램프 조명 매쉬 판별 (redLight, yelLight, grnLight 등)
    if (name.includes("light") && (name.includes("red") || name.includes("yel") || name.includes("grn") || name.includes("toplight"))) {
      hasTowerLight = true;
      if (m.material) {
        if (name.includes(activeColor) || (activeColor === "grn" && name.includes("toplight"))) {
           m.material.emissiveColor = m.material.diffuseColor || new BABYLON.Color3(1,1,1);
        } else {
           m.material.emissiveColor = new BABYLON.Color3(0, 0, 0); // 꺼짐
        }
      }
    }
  });

  // 타워램프가 없는 단순 트레이 등은 전체 색상을 살짝 변경하거나 테두리를 줄 수 있지만 
  // 여기서는 실제 공장처럼 상태 표시등에만 의존합니다.

  // 비율 변환된 모델이므로 자체 크기를 기본 스케일(1)로 사용합니다.
  const scaleFactor = 1.0;
  machineMesh.scaling = new BABYLON.Vector3(scaleFactor, scaleFactor, scaleFactor);

  // y축 하단 기준점의 오프셋 (스케일 적용 후 바닥에 닿도록 조정)
  const pivotOffsetY = 0.5; 
  machineMesh.position = new BABYLON.Vector3(machineData.position.x, machineData.position.y + pivotOffsetY, machineData.position.z);
  machineMesh.rotation = new BABYLON.Vector3(machineData.rotation.x, machineData.rotation.y, machineData.rotation.z);
  machineMesh.checkCollisions = true;
  machineMesh.metadata = { machineData: machineData };

  // 5. 클릭(Raycast) 처리를 위해 모든 하위 메시에도 metadata 부여 및 피킹 허용
  machineMesh.getChildMeshes(false).forEach(m => {
    m.metadata = { machineData: machineData };
    m.isPickable = true;
  });

  return machineMesh;
};
