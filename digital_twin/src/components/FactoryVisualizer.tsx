import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { useSimulation } from '../context/SimulationContext';
import type { Machine, Part } from '../types';
import { Activity } from 'lucide-react';

interface FactoryVisualizerProps {
  selectedMachineId: string | null;
  onSelectMachine: (id: string | null) => void;
}

export const FactoryVisualizer: React.FC<FactoryVisualizerProps> = ({
  selectedMachineId,
  onSelectMachine,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { machines, parts, isPlaying, speedMultiplier } = useSimulation();

  const selectedMachineIdRef = useRef<string | null>(selectedMachineId);
  useEffect(() => {
    selectedMachineIdRef.current = selectedMachineId;
  }, [selectedMachineId]);

  const onSelectMachineRef = useRef(onSelectMachine);
  useEffect(() => {
    onSelectMachineRef.current = onSelectMachine;
  }, [onSelectMachine]);

  // Keep refs for animation dynamics
  const isPlayingRef = useRef(isPlaying);
  const speedRef = useRef(speedMultiplier);
  useEffect(() => {
    isPlayingRef.current = isPlaying;
    speedRef.current = speedMultiplier;
  }, [isPlaying, speedMultiplier]);

  const machinesRef = useRef<Machine[]>(machines);
  useEffect(() => {
    machinesRef.current = machines;
  }, [machines]);

  const partsRef = useRef<Part[]>(parts);
  useEffect(() => {
    partsRef.current = parts;
  }, [parts]);

  useEffect(() => {
    if (!containerRef.current || !canvasRef.current) return;

    const container = containerRef.current;
    const canvas = canvasRef.current;

    // --- 1. Scene Setup ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0f1d); // cyber dark background
    scene.fog = new THREE.FogExp2(0x0a0f1d, 0.015);

    // --- 2. Camera Setup ---
    const width = container.clientWidth;
    const height = container.clientHeight || 500;
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    // Position camera for an isometric diagonal view
    camera.position.set(-45, 38, 48);

    // --- 3. Renderer Setup ---
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance',
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // --- 4. Controls ---
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.05; // prevent going under floor
    controls.minDistance = 15;
    controls.maxDistance = 120;
    controls.target.set(0, 0, 0);

    // --- 5. Lighting ---
    const ambientLight = new THREE.AmbientLight(0x0f172a, 1.8);
    scene.add(ambientLight);

    // Dynamic directional sun-like light for soft shadows
    const dirLight = new THREE.DirectionalLight(0xffffff, 2.2);
    dirLight.position.set(30, 45, 20);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 150;
    const d = 40;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    dirLight.shadow.bias = -0.0005;
    scene.add(dirLight);

    // Soft colored fill light for shadows
    const fillLight = new THREE.DirectionalLight(0x0ea5e9, 0.6);
    fillLight.position.set(-30, 20, -20);
    scene.add(fillLight);

    // --- 6. Floor & Grid ---
    // Ground mesh
    const groundGeo = new THREE.PlaneGeometry(100, 100);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x0c1020,
      roughness: 0.8,
      metalness: 0.6,
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid Overlay
    const gridHelper = new THREE.GridHelper(90, 45, 0x38bdf8, 0x1e293b);
    gridHelper.position.y = 0.01;
    // Lower grid opacity for styling
    if (Array.isArray(gridHelper.material)) {
      gridHelper.material.forEach((mat) => {
        mat.opacity = 0.15;
        mat.transparent = true;
      });
    } else {
      gridHelper.material.opacity = 0.15;
      gridHelper.material.transparent = true;
    }
    scene.add(gridHelper);

    // --- 7. Conveyor Belts ---
    // Draw 3D Tracks corresponding to the paths
    const TRACKS_CONFIG = [
      { start: new THREE.Vector3(-32, 0.7, -9), end: new THREE.Vector3(-8, 0.7, -9) },  // 0: Intake -> CNC
      { start: new THREE.Vector3(-8, 0.7, -9), end: new THREE.Vector3(16, 0.7, -9) },   // 1: CNC -> Assembly
      { start: new THREE.Vector3(16, 0.7, -9), end: new THREE.Vector3(16, 0.7, 9) },    // 2: Assembly -> Inspection
      { start: new THREE.Vector3(16, 0.7, 9), end: new THREE.Vector3(-8, 0.7, 9) },     // 3: Inspection -> Packaging
      { start: new THREE.Vector3(16, 0.7, 9), end: new THREE.Vector3(32, 0.7, 9) },     // 4: Inspection -> Reject Bin
      { start: new THREE.Vector3(-8, 0.7, 9), end: new THREE.Vector3(-32, 0.7, 9) },    // 5: Packaging -> Exit
    ];

    const rollerMeshes: THREE.Mesh[] = [];

    TRACKS_CONFIG.forEach((config) => {
      const distance = config.start.distanceTo(config.end);
      const center = new THREE.Vector3().addVectors(config.start, config.end).multiplyScalar(0.5);
      
      // Conveyor Base Track
      const trackGeo = new THREE.BoxGeometry(
        Math.abs(config.start.x - config.end.x) === 0 ? 1.4 : distance + 1.4,
        0.4,
        Math.abs(config.start.z - config.end.z) === 0 ? 1.4 : 1.4
      );
      const trackMat = new THREE.MeshStandardMaterial({
        color: 0x1e293b,
        roughness: 0.6,
        metalness: 0.8,
      });
      const trackMesh = new THREE.Mesh(trackGeo, trackMat);
      trackMesh.position.copy(center).y -= 0.2;
      trackMesh.receiveShadow = true;
      scene.add(trackMesh);

      // Side Guardrails
      const sideOffset = 0.75;
      const railMat = new THREE.MeshStandardMaterial({
        color: 0x0ea5e9,
        roughness: 0.2,
        metalness: 0.9,
      });

      if (Math.abs(config.start.x - config.end.x) === 0) {
        // Vertical Rails (Z-aligned)
        const guardGeo = new THREE.BoxGeometry(0.1, 0.4, distance);
        
        const guardLeft = new THREE.Mesh(guardGeo, railMat);
        guardLeft.position.copy(center).add(new THREE.Vector3(-sideOffset, 0, 0));
        scene.add(guardLeft);

        const guardRight = new THREE.Mesh(guardGeo, railMat);
        guardRight.position.copy(center).add(new THREE.Vector3(sideOffset, 0, 0));
        scene.add(guardRight);
      } else {
        // Horizontal Rails (X-aligned)
        const guardGeo = new THREE.BoxGeometry(distance, 0.4, 0.1);

        const guardLeft = new THREE.Mesh(guardGeo, railMat);
        guardLeft.position.copy(center).add(new THREE.Vector3(0, 0, -sideOffset));
        scene.add(guardLeft);

        const guardRight = new THREE.Mesh(guardGeo, railMat);
        guardRight.position.copy(center).add(new THREE.Vector3(0, 0, sideOffset));
        scene.add(guardRight);
      }

      // Add cylinder rollers inside conveyor
      const numRollers = Math.max(5, Math.round(distance / 2));
      const rollerGeo = new THREE.CylinderGeometry(0.15, 0.15, 1.2, 8);
      const rollerMat = new THREE.MeshStandardMaterial({
        color: 0x475569,
        roughness: 0.5,
        metalness: 0.9,
      });

      for (let i = 0; i <= numRollers; i++) {
        const roller = new THREE.Mesh(rollerGeo, rollerMat);
        const t = i / numRollers;
        const pos = new THREE.Vector3().lerpVectors(config.start, config.end, t);
        pos.y -= 0.05;
        roller.position.copy(pos);
        
        // Align roller cylinders perpendicular to travel direction
        if (Math.abs(config.start.x - config.end.x) === 0) {
          roller.rotation.z = Math.PI / 2;
        } else {
          roller.rotation.x = Math.PI / 2;
        }
        
        scene.add(roller);
        rollerMeshes.push(roller);
      }
    });

    // --- 8. Machine Meshes & Animations References ---
    // Machine coordinates in 3D:
    // Intake: (-32, 0, -9)
    // CNC: (-8, 0, -9)
    // Assembly: (16, 0, -9)
    // Inspection: (16, 0, 9)
    // Packaging: (-8, 0, 9)
    // Exit: (-32, 0, 9)
    // Reject Bin: (32, 0, 9)

    const machineGroupMap: Record<string, THREE.Group> = {};
    const machineStatusLights: Record<string, THREE.PointLight> = {};
    const selectionRingMap: Record<string, THREE.Mesh> = {};

    // Animation variables
    let cncGears: THREE.Mesh[] = [];
    let robotArmJoints: THREE.Group[] = [];
    let laserScannerHead: THREE.Mesh | null = null;
    let laserPlane: THREE.Mesh | null = null;
    let packerPiston: THREE.Mesh | null = null;

    const buildFactoryMachines = () => {
      // 1. INTAKE (Material Loader)
      const intakeGroup = new THREE.Group();
      intakeGroup.position.set(-32, 0, -9);
      
      const intakeBase = new THREE.Mesh(new THREE.BoxGeometry(4, 0.6, 4), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 }));
      intakeBase.position.y = 0.3;
      intakeBase.receiveShadow = true;
      intakeBase.castShadow = true;
      intakeGroup.add(intakeBase);

      // Shelving units and supply racks
      const rackMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.8, roughness: 0.3 });
      const crateMat = new THREE.MeshStandardMaterial({ color: 0xa26b38, roughness: 0.8 }); // wood texture box
      
      // Vertical pillars
      for (let xOffset of [-1.6, 1.6]) {
        for (let zOffset of [-1.6, 1.6]) {
          const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 4), rackMat);
          pillar.position.set(xOffset, 2, zOffset);
          pillar.castShadow = true;
          intakeGroup.add(pillar);
        }
      }
      // Shelves
      for (let h of [1.8, 3.4]) {
        const shelf = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.1, 3.6), rackMat);
        shelf.position.set(0, h, 0);
        intakeGroup.add(shelf);
      }
      // Small stock crates on shelves
      const crateGeo = new THREE.BoxGeometry(0.8, 0.8, 0.8);
      const crate1 = new THREE.Mesh(crateGeo, crateMat);
      crate1.position.set(-0.8, 2.2, -0.8);
      intakeGroup.add(crate1);
      
      const crate2 = new THREE.Mesh(crateGeo, crateMat);
      crate2.position.set(0.8, 2.2, 0.5);
      intakeGroup.add(crate2);

      const crate3 = new THREE.Mesh(crateGeo, new THREE.MeshStandardMaterial({ color: 0x475569 }));
      crate3.position.set(0, 3.8, 0);
      intakeGroup.add(crate3);

      scene.add(intakeGroup);
      machineGroupMap['intake'] = intakeGroup;
      intakeGroup.userData = { machineId: 'intake' };

      // 2. CNC MACHINING CENTER
      const cncGroup = new THREE.Group();
      cncGroup.position.set(-8, 0, -9);

      // Machine Body
      const cncBody = new THREE.Mesh(new THREE.BoxGeometry(5.2, 4.2, 5.2), new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8, roughness: 0.4 }));
      cncBody.position.y = 2.1;
      cncBody.receiveShadow = true;
      cncBody.castShadow = true;
      cncGroup.add(cncBody);

      // Chamber glass window
      const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x0ea5e9,
        transparent: true,
        opacity: 0.35,
        roughness: 0.1,
        metalness: 0.1,
        transmission: 0.9,
        ior: 1.5,
      });
      const windowMesh = new THREE.Mesh(new THREE.BoxGeometry(4.2, 2.2, 0.1), glassMat);
      windowMesh.position.set(0, 2.3, 2.6);
      cncGroup.add(windowMesh);

      // Rotating Gears Inside CNC Chamber
      const gearMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.9, roughness: 0.2 });
      const gearGeo = new THREE.CylinderGeometry(1.2, 1.2, 0.2, 16);
      
      const gear1 = new THREE.Mesh(gearGeo, gearMat);
      gear1.position.set(-1.0, 1.8, 0);
      cncGroup.add(gear1);
      cncGears.push(gear1);

      const gear2 = new THREE.Mesh(gearGeo, gearMat);
      gear2.position.set(1.0, 1.8, 0.3);
      cncGroup.add(gear2);
      cncGears.push(gear2);

      scene.add(cncGroup);
      machineGroupMap['cnc'] = cncGroup;
      cncGroup.userData = { machineId: 'cnc' };

      // 3. ASSEMBLY ROBOTIC ARM
      const assemblyGroup = new THREE.Group();
      assemblyGroup.position.set(16, 0, -9);

      const assemblyBase = new THREE.Mesh(new THREE.BoxGeometry(5, 0.8, 5), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 }));
      assemblyBase.position.y = 0.4;
      assemblyBase.receiveShadow = true;
      assemblyBase.castShadow = true;
      assemblyGroup.add(assemblyBase);

      // Robotic Joint Structure
      const armColorMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, metalness: 0.5, roughness: 0.4 }); // robotics blue
      const jointMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.9, roughness: 0.2 });

      // Base Pivot Group
      const basePivot = new THREE.Group();
      basePivot.position.set(0, 0.8, 0);
      assemblyGroup.add(basePivot);
      robotArmJoints.push(basePivot); // joint index 0 (Y-axis swivel)

      const standGeo = new THREE.CylinderGeometry(0.8, 0.9, 1.2, 16);
      const standMesh = new THREE.Mesh(standGeo, jointMat);
      standMesh.position.y = 0.6;
      standMesh.castShadow = true;
      basePivot.add(standMesh);

      // Shoulder joint Group
      const shoulderPivot = new THREE.Group();
      shoulderPivot.position.set(0, 1.2, 0);
      basePivot.add(shoulderPivot);
      robotArmJoints.push(shoulderPivot); // joint index 1 (Pitch-axis rotate)

      const arm1Geo = new THREE.CylinderGeometry(0.3, 0.3, 3.2, 8);
      const arm1Mesh = new THREE.Mesh(arm1Geo, armColorMat);
      arm1Mesh.position.y = 1.6;
      arm1Mesh.castShadow = true;
      shoulderPivot.add(arm1Mesh);

      // Elbow joint Group
      const elbowPivot = new THREE.Group();
      elbowPivot.position.set(0, 3.2, 0);
      shoulderPivot.add(elbowPivot);
      robotArmJoints.push(elbowPivot); // joint index 2 (Pitch-axis elbow)

      const elbowSph = new THREE.Mesh(new THREE.SphereGeometry(0.4, 16, 16), jointMat);
      elbowPivot.add(elbowSph);

      const arm2Geo = new THREE.CylinderGeometry(0.22, 0.22, 2.8, 8);
      const arm2Mesh = new THREE.Mesh(arm2Geo, armColorMat);
      arm2Mesh.position.y = 1.4;
      arm2Mesh.castShadow = true;
      elbowPivot.add(arm2Mesh);

      // Wrist Gripper assembly
      const gripper = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.3, 0.8), jointMat);
      gripper.position.y = 2.8;
      elbowPivot.add(gripper);

      scene.add(assemblyGroup);
      machineGroupMap['assembly'] = assemblyGroup;
      assemblyGroup.userData = { machineId: 'assembly' };

      // 4. INSPECTION SCANNER (Laser Gantry)
      const inspectionGroup = new THREE.Group();
      inspectionGroup.position.set(16, 0, 9);

      const inspectionBase = new THREE.Mesh(new THREE.BoxGeometry(5, 0.6, 5), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 }));
      inspectionBase.position.y = 0.3;
      inspectionBase.receiveShadow = true;
      inspectionBase.castShadow = true;
      inspectionGroup.add(inspectionBase);

      // Gantry framing (Arch spanning Z axis)
      const archMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8, roughness: 0.3 });
      
      const pillarLeft = new THREE.Mesh(new THREE.BoxGeometry(0.4, 4.6, 0.8), archMat);
      pillarLeft.position.set(0, 2.3, -2.1);
      pillarLeft.castShadow = true;
      inspectionGroup.add(pillarLeft);

      const pillarRight = new THREE.Mesh(new THREE.BoxGeometry(0.4, 4.6, 0.8), archMat);
      pillarRight.position.set(0, 2.3, 2.1);
      pillarRight.castShadow = true;
      inspectionGroup.add(pillarRight);

      const topBeam = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 5.0), archMat);
      topBeam.position.set(0, 4.5, 0);
      inspectionGroup.add(topBeam);

      // Scanner Head
      const headGeo = new THREE.BoxGeometry(1.2, 0.8, 1.2);
      const headMat = new THREE.MeshStandardMaterial({ color: 0x0ea5e9, roughness: 0.4 });
      laserScannerHead = new THREE.Mesh(headGeo, headMat);
      laserScannerHead.position.set(0, 4.1, 0);
      laserScannerHead.castShadow = true;
      inspectionGroup.add(laserScannerHead);

      // Translucent laser sweep plane
      const planeGeo = new THREE.BoxGeometry(0.02, 3.8, 3.4);
      const planeMat = new THREE.MeshBasicMaterial({
        color: 0x10b981,
        transparent: true,
        opacity: 0.25,
        side: THREE.DoubleSide,
      });
      laserPlane = new THREE.Mesh(planeGeo, planeMat);
      laserPlane.position.set(0, -1.9, 0); // attached under head
      laserScannerHead.add(laserPlane);

      scene.add(inspectionGroup);
      machineGroupMap['inspection'] = inspectionGroup;
      inspectionGroup.userData = { machineId: 'inspection' };

      // 5. PACKAGING UNIT (Hydraulic Press)
      const packagingGroup = new THREE.Group();
      packagingGroup.position.set(-8, 0, 9);

      const packagingBase = new THREE.Mesh(new THREE.BoxGeometry(5.2, 0.8, 5.2), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7 }));
      packagingBase.position.y = 0.4;
      packagingBase.receiveShadow = true;
      packagingBase.castShadow = true;
      packagingGroup.add(packagingBase);

      // Large Press Framework
      const pressMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.9, roughness: 0.3 });
      
      const pressFrame = new THREE.Mesh(new THREE.BoxGeometry(4.4, 4.8, 4.4), pressMat);
      pressFrame.position.y = 2.8;
      pressFrame.castShadow = true;
      packagingGroup.add(pressFrame);

      // Hollow inner chamber cutout
      const chamberMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 });
      const innerChamber = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.6, 4.5), chamberMat);
      innerChamber.position.y = 2.2;
      packagingGroup.add(innerChamber);

      // Hydraulic metal piston
      const pistonGeo = new THREE.CylinderGeometry(0.5, 0.5, 2.0, 16);
      const pistonMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.98, roughness: 0.05 });
      packerPiston = new THREE.Mesh(pistonGeo, pistonMat);
      packerPiston.position.set(0, 3.0, 0);
      packagingGroup.add(packerPiston);

      const stampGeo = new THREE.BoxGeometry(2.4, 0.4, 2.4);
      const stampMesh = new THREE.Mesh(stampGeo, new THREE.MeshStandardMaterial({ color: 0x475569 }));
      stampMesh.position.y = -1.0;
      packerPiston.add(stampMesh);

      scene.add(packagingGroup);
      machineGroupMap['packaging'] = packagingGroup;
      packagingGroup.userData = { machineId: 'packaging' };

      // 6. EXIT LOADING DOCK (Storage pallets)
      const exitGroup = new THREE.Group();
      exitGroup.position.set(-32, 0, 9);
      
      const exitBase = new THREE.Mesh(new THREE.BoxGeometry(6, 0.4, 6), new THREE.MeshStandardMaterial({ color: 0x1e293b }));
      exitBase.position.y = 0.2;
      exitGroup.add(exitBase);

      // Cargo palettes
      for (let i = 0; i < 3; i++) {
        const pallet = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.15, 1.8), new THREE.MeshStandardMaterial({ color: 0x854d0e }));
        pallet.position.set(-1.6 + i * 1.6, 0.35, 1.5);
        pallet.castShadow = true;
        exitGroup.add(pallet);

        // Crates stacked on pallets
        const stackCrate = new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.4, 1.4), crateMat);
        stackCrate.position.copy(pallet.position).y += 0.8;
        stackCrate.castShadow = true;
        exitGroup.add(stackCrate);
      }

      scene.add(exitGroup);
      machineGroupMap['exit'] = exitGroup;

      // 7. REJECT BIN
      const rejectGroup = new THREE.Group();
      rejectGroup.position.set(32, 0, 9);
      
      // Create red hollow recycling bin shapes
      const binMat = new THREE.MeshStandardMaterial({ color: 0xef4444, metalness: 0.1, roughness: 0.5 });
      const binBase = new THREE.Mesh(new THREE.BoxGeometry(3, 0.15, 3), binMat);
      binBase.position.y = 0.1;
      rejectGroup.add(binBase);
      
      // Walls
      const wallBack = new THREE.Mesh(new THREE.BoxGeometry(3, 2, 0.15), binMat);
      wallBack.position.set(0, 1.0, -1.4);
      rejectGroup.add(wallBack);

      const wallFront = new THREE.Mesh(new THREE.BoxGeometry(3, 2, 0.15), binMat);
      wallFront.position.set(0, 1.0, 1.4);
      rejectGroup.add(wallFront);

      const wallLeft = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2, 3), binMat);
      wallLeft.position.set(-1.4, 1.0, 0);
      rejectGroup.add(wallLeft);

      const wallRight = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2, 3), binMat);
      wallRight.position.set(1.4, 1.0, 0);
      rejectGroup.add(wallRight);

      scene.add(rejectGroup);
      machineGroupMap['reject'] = rejectGroup;

      // Create glowing selection indicator rings for selectable machines
      const ringGeo = new THREE.RingGeometry(3.6, 3.8, 32);
      ringGeo.rotateX(-Math.PI / 2);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, side: THREE.DoubleSide, transparent: true, opacity: 0 });
      
      Object.keys(machineGroupMap).forEach((id) => {
        // Skip warehouses and exit docks for overrides if desired, but we support selecting selectable ones
        if (id === 'exit' || id === 'reject') return;
        const ring = new THREE.Mesh(ringGeo, ringMat.clone());
        ring.position.copy(machineGroupMap[id].position);
        ring.position.y = 0.05; // float slightly above grid
        scene.add(ring);
        selectionRingMap[id] = ring;
      });

      // Assemble Point Lights for statuses
      Object.keys(machineGroupMap).forEach((id) => {
        if (id === 'exit' || id === 'reject') return;
        
        const bulb = new THREE.Mesh(
          new THREE.SphereGeometry(0.15, 8, 8),
          new THREE.MeshBasicMaterial({ color: 0x10b981 })
        );
        bulb.position.set(0, 4.4, 0);
        if (id === 'cnc') bulb.position.set(0, 4.4, 0);
        else if (id === 'intake') bulb.position.set(0, 4.4, 0);
        else if (id === 'assembly') bulb.position.set(0, 4.6, 0);
        else if (id === 'inspection') bulb.position.set(0, 4.9, 0);
        else if (id === 'packaging') bulb.position.set(0, 5.4, 0);

        machineGroupMap[id].add(bulb);

        const pointLight = new THREE.PointLight(0x10b981, 2.5, 8);
        pointLight.position.copy(bulb.position).y += 0.2;
        pointLight.castShadow = false;
        machineGroupMap[id].add(pointLight);
        machineStatusLights[id] = pointLight;
      });
    };

    buildFactoryMachines();

    // --- 9. Raycast Selection Mouse Event Handler ---
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleCanvasClick = (event: MouseEvent) => {
      // Calculate mouse position in normalized device coordinates (-1 to +1)
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);

      // Find all objects intersecting the ray
      const intersects = raycaster.intersectObjects(scene.children, true);

      if (intersects.length > 0) {
        // Find which machine base group is the parent
        let foundNode: THREE.Object3D | null = intersects[0].object;
        let machineId: string | null = null;
        
        while (foundNode && foundNode !== scene) {
          if (foundNode.userData && foundNode.userData.machineId) {
            machineId = foundNode.userData.machineId;
            break;
          }
          foundNode = foundNode.parent;
        }

        if (machineId) {
          const currentSelected = selectedMachineIdRef.current;
          if (currentSelected === machineId) {
            // Deselect on clicking again
            onSelectMachineRef.current(null);
          } else {
            // Select machine
            onSelectMachineRef.current(machineId);
          }
        }
      }
    };

    renderer.domElement.addEventListener('click', handleCanvasClick);

    // --- 10. Moving Parts Reconciler ---
    const partMeshes: Record<string, THREE.Mesh> = {};
    const partGeo = new THREE.BoxGeometry(0.7, 0.7, 0.7);

    const updatePartsInScene = (currentParts: Part[]) => {
      // 1. Identify which meshes to delete
      const currentPartIds = new Set(currentParts.map((p) => p.id));
      Object.keys(partMeshes).forEach((id) => {
        if (!currentPartIds.has(id)) {
          scene.remove(partMeshes[id]);
          partMeshes[id].geometry.dispose();
          if (Array.isArray(partMeshes[id].material)) {
            (partMeshes[id].material as THREE.Material[]).forEach((m) => m.dispose());
          } else {
            (partMeshes[id].material as THREE.Material).dispose();
          }
          delete partMeshes[id];
        }
      });

      // 2. Add or update meshes
      currentParts.forEach((part) => {
        let mesh = partMeshes[part.id];
        
        // Stage coloring matching design
        let colorVal = 0x94a3b8; // raw (slate)
        let isDefective = false;

        switch (part.stage) {
          case 'MACHINED': colorVal = 0xf59e0b; break; // amber
          case 'ASSEMBLED': colorVal = 0x0ea5e9; break; // cyan
          case 'INSPECTED': colorVal = 0x10b981; break; // green
          case 'DEFECTIVE': 
            colorVal = 0xef4444; // red
            isDefective = true;
            break;
          case 'PACKAGED': colorVal = 0x854d0e; break; // brown
        }

        if (!mesh) {
          const mat = new THREE.MeshStandardMaterial({
            color: colorVal,
            roughness: 0.2,
            metalness: 0.6,
          });
          mesh = new THREE.Mesh(partGeo, mat);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          scene.add(mesh);
          partMeshes[part.id] = mesh;
        } else {
          // Update color if stage changes
          const mat = mesh.material as THREE.MeshStandardMaterial;
          if (mat.color.getHex() !== colorVal) {
            mat.color.setHex(colorVal);
          }
          // Defective flashing effect
          if (isDefective) {
            const pulse = 0.5 + Math.abs(Math.sin(Date.now() * 0.015)) * 0.5;
            mat.emissive.setHex(0x990000).multiplyScalar(pulse);
          } else {
            mat.emissive.setHex(0x000000);
          }
        }

        // Map 2D coordinates to 3D positions
        // x goes from 120 to 760 -> Map to X axis
        // y goes from 180 to 360 -> Map to Z axis
        const x3d = (part.x - 440) / 10;
        const z3d = (part.y - 270) / 10;
        let y3d = 0.9; // resting on conveyor top height

        // If docked inside a machine, animate a visual processing state (slightly sink or raise)
        if (part.progress > 1.0) {
          // Hidden/submerged or hovering inside machine chamber
          y3d = 0.75;
          mesh.scale.set(0.8, 0.8, 0.8);
        } else {
          mesh.scale.set(1, 1, 1);
        }

        mesh.position.set(x3d, y3d, z3d);
      });
    };

    // --- 11. Animation Loop ---
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      
      const time = clock.getElapsedTime();
      const isSimPlaying = isPlayingRef.current;
      const simSpeed = speedRef.current;

      // 1. Rotate rollers if simulation is active
      if (isSimPlaying) {
        rollerMeshes.forEach((roller) => {
          roller.rotation.y += 0.05 * simSpeed;
        });
      }

      // 2. Animate machine states
      const currentMachines = machinesRef.current;
      
      currentMachines.forEach((mach) => {
        const light = machineStatusLights[mach.id];
        const group = machineGroupMap[mach.id];
        
        if (!light || !group) return;

        // Visual highlights for selection ring
        const currentSelectedId = selectedMachineIdRef.current;
        const ring = selectionRingMap[mach.id];
        if (ring) {
          if (currentSelectedId === mach.id) {
            ring.rotation.y += 0.01;
            const pulse = 0.6 + Math.abs(Math.sin(time * 3)) * 0.4;
            (ring.material as THREE.MeshBasicMaterial).opacity = pulse;
          } else {
            (ring.material as THREE.MeshBasicMaterial).opacity = 0;
          }
        }

        // Status color mapping for LED light
        let colorHex = 0x10b981; // green
        let lightIntensity = 2.5;

        if (mach.status === 'IDLE') {
          colorHex = 0x0ea5e9; // cyan
          lightIntensity = 1.0;
        } else if (mach.status === 'MAINTENANCE') {
          colorHex = 0xf59e0b; // yellow/orange
          // Blink light slowly
          const blink = 0.5 + Math.sin(time * 4) * 0.5;
          lightIntensity = blink * 3.0;
        } else if (mach.status === 'ERROR') {
          colorHex = 0xef4444; // red
          // Flash light rapidly
          const flash = Math.round(time * 8) % 2;
          lightIntensity = flash * 5.0;
        }

        light.color.setHex(colorHex);
        light.intensity = lightIntensity;
        
        // Update bulb geometry mesh material color too
        const bulbMesh = group.children.find((c) => c instanceof THREE.Mesh && c.material instanceof THREE.MeshBasicMaterial) as THREE.Mesh | undefined;
        if (bulbMesh) {
          (bulbMesh.material as THREE.MeshBasicMaterial).color.setHex(colorHex);
        }

        // --- SPECIFIC MACHINE ANIMATIONS ---
        const isActive = mach.status === 'RUNNING' && isSimPlaying;

        // CNC gears spinning
        if (mach.id === 'cnc' && cncGears.length >= 2) {
          if (isActive) {
            cncGears[0].rotation.y += 0.1 * simSpeed;
            cncGears[1].rotation.y -= 0.1 * simSpeed;
            cncGears[0].position.y = 1.8 + Math.sin(time * 10) * 0.05;
          }
        }

        // Robotic Arm movement
        if (mach.id === 'assembly' && robotArmJoints.length >= 3) {
          if (isActive) {
            // Make base swivel back and forth
            robotArmJoints[0].rotation.y = Math.sin(time * 1.5 * simSpeed) * 0.7;
            // Shoulder angle articulation
            robotArmJoints[1].rotation.z = Math.sin(time * 2.0 * simSpeed) * 0.3 + 0.3;
            // Elbow joint articulation
            robotArmJoints[2].rotation.z = Math.cos(time * 2.0 * simSpeed) * 0.4 - 0.4;
          } else if (mach.status === 'MAINTENANCE') {
            // Calm folded maintenance pose
            robotArmJoints[0].rotation.y = 0;
            robotArmJoints[1].rotation.z = 0.8;
            robotArmJoints[2].rotation.z = -1.2;
          } else if (mach.status === 'ERROR') {
            // Drooped broken pose
            robotArmJoints[0].rotation.y = 0.4;
            robotArmJoints[1].rotation.z = 1.2;
            robotArmJoints[2].rotation.z = -0.4;
          } else {
            // Idle position
            robotArmJoints[0].rotation.y = 0;
            robotArmJoints[1].rotation.z = 0.2;
            robotArmJoints[2].rotation.z = -0.2;
          }
        }

        // Inspection scan head sliding
        if (mach.id === 'inspection' && laserScannerHead && laserPlane) {
          if (isActive) {
            laserPlane.visible = true;
            // Sweep scan head along Z axis
            laserScannerHead.position.z = Math.sin(time * 2.5 * simSpeed) * 1.8;
          } else {
            laserPlane.visible = false;
            laserScannerHead.position.z = 0;
          }
        }

        // Packaging Press Stamp
        if (mach.id === 'packaging' && packerPiston) {
          if (isActive) {
            // Press down and lift up rhythmic motion
            const pressCycle = Math.abs(Math.sin(time * 3.5 * simSpeed));
            packerPiston.position.y = 3.6 - pressCycle * 1.8;
          } else {
            packerPiston.position.y = 3.6;
          }
        }
      });

      // 3. Update active parts list
      updatePartsInScene(partsRef.current);

      // 4. Update Orbit Controls & Render
      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    // --- 12. Window Resize Handler ---
    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight || 500;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    
    // Resize observer is more reliable inside layout flex grids
    const resizeObserver = new ResizeObserver(() => {
      handleResize();
    });
    resizeObserver.observe(container);

    // --- 13. Cleanup ---
    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      renderer.domElement.removeEventListener('click', handleCanvasClick);
      
      // Dispose meshes, geometries, and materials
      scene.traverse((obj) => {
        if (obj instanceof THREE.Mesh) {
          obj.geometry.dispose();
          if (Array.isArray(obj.material)) {
            obj.material.forEach((mat) => mat.dispose());
          } else {
            obj.material.dispose();
          }
        }
      });

      // Remove selection rings
      Object.keys(selectionRingMap).forEach((id) => {
        scene.remove(selectionRingMap[id]);
        selectionRingMap[id].geometry.dispose();
        (selectionRingMap[id].material as THREE.Material).dispose();
      });

      // Clear lights and renderer
      renderer.dispose();
    };
  }, []);

  return (
    <div ref={containerRef} className="glass-panel panel-container relative w-full flex-1 flex flex-col min-h-[500px]">
      <div className="px-6 py-4 border-b border-[var(--border-soft)] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="text-[var(--color-blue)] w-5 h-5 animate-pulse" />
          <h2 className="text-xl font-bold uppercase tracking-wider font-mono m-0 text-slate-100">
            Interactive 3D Digital Twin
          </h2>
        </div>
        <div className="flex gap-4 text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]" /> Running
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0ea5e9]" /> Idle
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]" /> Maint.
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]" /> Error
          </div>
        </div>
      </div>

      {/* 3D WebGL Canvas container */}
      <div className="flex-1 relative bg-slate-950/40 overflow-hidden">
        <canvas ref={canvasRef} className="w-full h-full block" style={{ outline: 'none' }} />

        {/* Floating 3D overlay controls info */}
        <div className="absolute bottom-4 left-6 pointer-events-none text-slate-400 text-xs flex flex-col gap-1.5 font-mono bg-slate-950/80 p-2.5 rounded border border-white/5 backdrop-blur-md">
          <span className="text-slate-200 font-bold uppercase tracking-wider text-[10px] mb-1">🎮 Orbit Navigation</span>
          <span>• Left-Click & Drag: Rotate Camera</span>
          <span>• Scroll Wheel: Zoom In / Out</span>
          <span>• Right-Click & Drag: Pan Scene</span>
          <span className="mt-1 text-[var(--color-blue)] font-bold">• Click any machine to inspect & override</span>
        </div>
      </div>
    </div>
  );
};
