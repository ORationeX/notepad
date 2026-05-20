import * as BABYLON from '@babylonjs/core';
import { ApiService } from '../data/service/ApiService';
import type { IMachine, IFloor } from '../data/model/Types';

export class EnvironmentBuilder {
  private scene: BABYLON.Scene;
  private apiService: ApiService;
  
  // Floor and Machine root nodes for culling
  public floorNodes: Map<number, BABYLON.TransformNode> = new Map();

  constructor(scene: BABYLON.Scene) {
    this.scene = scene;
    this.apiService = new ApiService();
  }

  public async build() {
    // 1. Fetch data
    const floors = await this.apiService.getFloors();
    const machines = await this.apiService.getAllMachines();

    // 2. Build Floor base meshes
    for (const floor of floors) {
      const floorNode = new BABYLON.TransformNode(`floor_${floor.floorId}_node`, this.scene);
      this.floorNodes.set(floor.floorId, floorNode);

      // Create ground mesh for this floor
      const ground = BABYLON.MeshBuilder.CreateGround(`ground_${floor.floorId}`, { width: 50, height: 50 }, this.scene);
      ground.position.y = floor.yOffset;
      ground.checkCollisions = true; // Prevents camera falling
      
      const mat = new BABYLON.StandardMaterial(`groundMat_${floor.floorId}`, this.scene);
      mat.diffuseColor = floor.floorId === 0 ? new BABYLON.Color3(0.3, 0.35, 0.4) : new BABYLON.Color3(0.4, 0.35, 0.3); // Diff colors
      mat.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1);
      ground.material = mat;
      
      ground.parent = floorNode;

      // Create dummy walls
      this.createWalls(floor, floorNode);
    }

    // 3. Build Machines based on Mock DB
    for (const machine of machines) {
      this.buildMachineProxy(machine);
    }
  }

  private createWalls(floor: IFloor, parentNode: BABYLON.TransformNode) {
    // North Wall
    const northWall = BABYLON.MeshBuilder.CreateBox(`nWall_${floor.floorId}`, { width: 50, height: 10, depth: 1 }, this.scene);
    northWall.position = new BABYLON.Vector3(0, floor.yOffset + 5, 25);
    northWall.checkCollisions = true;
    northWall.parent = parentNode;

    // South Wall
    const southWall = BABYLON.MeshBuilder.CreateBox(`sWall_${floor.floorId}`, { width: 50, height: 10, depth: 1 }, this.scene);
    southWall.position = new BABYLON.Vector3(0, floor.yOffset + 5, -25);
    southWall.checkCollisions = true;
    southWall.parent = parentNode;
    
    // East Wall
    const eastWall = BABYLON.MeshBuilder.CreateBox(`eWall_${floor.floorId}`, { width: 1, height: 10, depth: 50 }, this.scene);
    eastWall.position = new BABYLON.Vector3(25, floor.yOffset + 5, 0);
    eastWall.checkCollisions = true;
    eastWall.parent = parentNode;

    // West Wall
    const westWall = BABYLON.MeshBuilder.CreateBox(`wWall_${floor.floorId}`, { width: 1, height: 10, depth: 50 }, this.scene);
    westWall.position = new BABYLON.Vector3(-25, floor.yOffset + 5, 0);
    westWall.checkCollisions = true;
    westWall.parent = parentNode;
  }

  private buildMachineProxy(machine: IMachine) {
    let mesh: BABYLON.Mesh;
    
    // Phase 4 Proxy: Will be replaced by GLB actual loading later
    switch(machine.type) {
      case 'CNC':
        mesh = BABYLON.MeshBuilder.CreateBox(machine.machineId, { width: 4, height: 4, depth: 3 }, this.scene);
        break;
      case 'ROBOT_ARM':
        mesh = BABYLON.MeshBuilder.CreateCylinder(machine.machineId, { height: 5, diameterTop: 0.5, diameterBottom: 1.5 }, this.scene);
        break;
      case 'CONVEYOR':
        mesh = BABYLON.MeshBuilder.CreateBox(machine.machineId, { width: 10, height: 1, depth: 2 }, this.scene);
        break;
    }

    // Set Status Color Material
    const mat = new BABYLON.StandardMaterial(`${machine.machineId}_mat`, this.scene);
    if (machine.status === 'RUNNING') mat.diffuseColor = BABYLON.Color3.Green();
    else if (machine.status === 'IDLE') mat.diffuseColor = BABYLON.Color3.Yellow();
    else mat.diffuseColor = BABYLON.Color3.Red();
    mesh.material = mat;

    // Set Position & Rotation (y needs to account for floor yOffset and half-height for primitive meshes so they sit on floor)
    let yBase = machine.position.y; // Usually this is already floorHeight offset in our DB
    
    // Calculate half-height offset because origin of babylon prims is center
    let yOffsetForOrigin = 0;
    if (machine.type === 'CNC') yOffsetForOrigin = 2; // half of 4
    if (machine.type === 'ROBOT_ARM') yOffsetForOrigin = 2.5; // half of 5
    if (machine.type === 'CONVEYOR') yOffsetForOrigin = 0.5; // half of 1

    mesh.position = new BABYLON.Vector3(machine.position.x, yBase + yOffsetForOrigin, machine.position.z);
    mesh.rotation = new BABYLON.Vector3(machine.rotation.x, machine.rotation.y, machine.rotation.z);
    
    mesh.checkCollisions = true;

    // Attach to correct Floor Node for Culling
    const parentNode = this.floorNodes.get(machine.floorId);
    if (parentNode) {
      mesh.parent = parentNode;
    }

    // Add metadata for picking/UI Raycast
    mesh.metadata = { machineData: machine };
  }

  // Floor Culling: Hides inactive floors to save draw calls
  public setVisibleFloor(floorId: number) {
    this.floorNodes.forEach((node, id) => {
      node.setEnabled(id === floorId);
    });
  }
}
