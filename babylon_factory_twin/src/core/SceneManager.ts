import * as BABYLON from '@babylonjs/core';
import type { DeviceInfo } from '../main';
import { InputManager } from '../input/InputManager';
import { EnvironmentBuilder } from '../scene/EnvironmentBuilder';

export class SceneManager {
  public scene: BABYLON.Scene;
  private engine: BABYLON.Engine;
  private canvas: HTMLCanvasElement;
  private deviceInfo: DeviceInfo;
  
  public camera!: BABYLON.UniversalCamera;
  public inputManager!: InputManager;
  public envBuilder!: EnvironmentBuilder;
  public currentFloorId: number = 0; // 0 for 1F, 20 for 2F

  constructor(engine: BABYLON.Engine, canvas: HTMLCanvasElement, deviceInfo: DeviceInfo) {
    this.engine = engine;
    this.canvas = canvas;
    this.deviceInfo = deviceInfo;
    this.scene = new BABYLON.Scene(engine);
    
    // Core scene optimizations
    this.scene.clearColor = new BABYLON.Color4(0.12, 0.12, 0.14, 1.0);
    this.scene.collisionsEnabled = true;
    
    // Performance optimization: skip frustum culling if not needed, but we will use mesh visibility
  }

  public async initialize() {
    this.setupCamera();
    this.setupLighting();
    await this.setupEnvironment();
  }

  private setupCamera() {
    // Universal Camera for cross-platform
    this.camera = new BABYLON.UniversalCamera('MainCamera', new BABYLON.Vector3(0, 2, -10), this.scene);
    this.camera.setTarget(BABYLON.Vector3.Zero());
    
    // Collision specs
    this.camera.checkCollisions = true;
    this.camera.applyGravity = true;
    this.camera.ellipsoid = new BABYLON.Vector3(1, 1, 1);
    
    // Gravity for the scene
    this.scene.gravity = new BABYLON.Vector3(0, -0.15, 0);

    // Initialize Input Manager
    this.inputManager = new InputManager(this.camera, this.canvas, this.deviceInfo);
    this.inputManager.attachControls();
  }

  private setupLighting() {
    const hemiLight = new BABYLON.HemisphericLight('hemiLight', new BABYLON.Vector3(0, 1, 0), this.scene);
    hemiLight.intensity = 0.7;

    if (this.deviceInfo.isPC) {
      // Dynamic shadows on PC
      const dirLight = new BABYLON.DirectionalLight('dirLight', new BABYLON.Vector3(-1, -2, -1), this.scene);
      dirLight.position = new BABYLON.Vector3(20, 40, 20);
      dirLight.intensity = 0.8;
      
      const shadowGenerator = new BABYLON.ShadowGenerator(1024, dirLight);
      shadowGenerator.useBlurExponentialShadowMap = true;
      shadowGenerator.blurKernel = 32;
      // Note: objects will need to be added to shadow generator
    }
  }

  private async setupEnvironment() {
    this.envBuilder = new EnvironmentBuilder(this.scene);
    await this.envBuilder.build();
    
    // Initial culling (Show 1F by default)
    this.envBuilder.setVisibleFloor(this.currentFloorId);
  }

  public render() {
    this.scene.render();
  }
}
