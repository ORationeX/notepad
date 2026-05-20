window.buildAntistaticTrayModel = function(scene, machineMesh) {
  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};
  const w = size.w; const h = size.h; const d = size.d;

  // 1. 재질(Materials) 정의
  // 무광택 정전기 방지 플라스틱 재질 (어두운 회색/검정)
  const trayMat = new BABYLON.StandardMaterial("trayMat", scene);
  trayMat.diffuseColor = new BABYLON.Color3(0.08, 0.08, 0.1); // 매우 어두운 색
  trayMat.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1); // 낮은 반사광
  trayMat.roughness = 0.8; // 무광택 표면

  // 식별 라벨 재질 (흰색 바탕, 자체 발광 효과로 가독성 확보)
  const labelMat = new BABYLON.StandardMaterial("labelMat", scene);
  labelMat.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.9);
  labelMat.emissiveColor = new BABYLON.Color3(0.1, 0.1, 0.1); // 미세한 자체 발광
  // 실제 텍스처를 넣고 싶다면 라벨 이미지를 사용:
  // labelMat.diffuseTexture = new BABYLON.Texture("path/to/your/label_texture.png", scene);

  // 전체 트레이 모델을 그룹화할 TransformNode
  const trayFrame = new BABYLON.TransformNode("antiStaticTray", scene);
  trayFrame.parent = machineMesh;

  // 2. 기본 형태 (외형 및 하판)
  // 전체 크기 설정 (이미지를 기준으로 얇고 넓게)
  const trayWidth = 12;
  const trayDepth = 8;
  const trayHeight = 0.8;
  const rimThickness = 0.15;

  // 바닥판
  const bottom = BABYLON.MeshBuilder.CreateBox("bottom", {width: trayWidth, height: h * 0.01, depth: trayDepth}, scene);
  bottom.position.y = h * 0.005;
  bottom.material = trayMat;
  bottom.parent = trayFrame;

  // 외곽 테두리 (Rim)
  const backRim = BABYLON.MeshBuilder.CreateBox("backRim", {width: trayWidth, height: trayHeight, depth: rimThickness}, scene);
  backRim.position.y = trayHeight / 2;
  backRim.position.z = trayDepth / 2 - rimThickness / 2;
  backRim.material = trayMat;
  backRim.parent = trayFrame;

  const frontRim = BABYLON.MeshBuilder.CreateBox("frontRim", {width: trayWidth, height: trayHeight, depth: rimThickness}, scene);
  frontRim.position.y = trayHeight / 2;
  frontRim.position.z = -(trayDepth / 2 - rimThickness / 2);
  frontRim.material = trayMat;
  frontRim.parent = trayFrame;

  const leftRim = BABYLON.MeshBuilder.CreateBox("leftRim", {width: rimThickness, height: trayHeight, depth: trayDepth - rimThickness * 2}, scene);
  leftRim.position.y = trayHeight / 2;
  leftRim.position.x = -(trayWidth / 2 - rimThickness / 2);
  leftRim.material = trayMat;
  leftRim.parent = trayFrame;

  const rightRim = BABYLON.MeshBuilder.CreateBox("rightRim", {width: rimThickness, height: trayHeight, depth: trayDepth - rimThickness * 2}, scene);
  rightRim.position.y = trayHeight / 2;
  rightRim.position.x = trayWidth / 2 - rimThickness / 2;
  rightRim.material = trayMat;
  rightRim.parent = trayFrame;

  // 3. 복합 계단식 성형 포켓 (Intricate Pocket Steps)
  // 이미지에서 볼 수 있는 복잡한 계단식 격자 패턴을 단순화하여 구현
  const gridRows = 4;
  const gridCols = 3;
  const pocketWidth = (trayWidth - rimThickness * 3) / gridCols;
  const pocketDepth = (trayDepth - rimThickness * 5) / gridRows;
  
  // 포켓 계단 높이
  const stepHeight = 0.2; 

  for (let r = 0; r < gridRows; r++) {
    for (let c = 0; c < gridCols; c++) {
      // 각 포켓의 중심 좌표 계산
      const posX = -(trayWidth / 2) + rimThickness + pocketWidth / 2 + c * (pocketWidth + rimThickness / 2);
      const posZ = (trayDepth / 2) - rimThickness - pocketDepth / 2 - r * (pocketDepth + rimThickness / 2);

      // 1단계: 하단 좁은 단계 (Inner Step)
      const step1 = BABYLON.MeshBuilder.CreateBox(`pocket_r${r}_c${c}_step1`, {width: pocketWidth * 0.7, height: stepHeight, depth: pocketDepth * 0.7}, scene);
      step1.position.x = posX;
      step1.position.y = stepHeight / 2 + 0.1; // 바닥판 바로 위
      step1.position.z = posZ;
      step1.material = trayMat;
      step1.parent = trayFrame;

      // 2단계: 상단 넓은 단계 (Outer Step)
      const step2 = BABYLON.MeshBuilder.CreateBox(`pocket_r${r}_c${c}_step2`, {width: pocketWidth, height: stepHeight, depth: pocketDepth}, scene);
      step2.position.x = posX;
      step2.position.y = stepHeight * 1.5 + 0.1;
      step2.position.z = posZ;
      step2.material = trayMat;
      step2.parent = trayFrame;
    }
  }

  // 4. 측면 식별 라벨 (Identification Label)
  // 이미지의 정면 하단 테두리에 라벨 추가
  const label = BABYLON.MeshBuilder.CreateBox("label", {width: w * 0.15, height: h * 0.05, depth: d * 0.002}, scene);
  label.position.y = trayHeight / 2;
  label.position.z = -(trayDepth / 2); // 정면 테두리 표면에 밀착
  label.position.x = -trayWidth * 0.3; // 왼쪽으로 약간 치우친 위치
  label.material = labelMat;
  label.parent = trayFrame;
};