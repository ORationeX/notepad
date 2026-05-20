import * as BABYLON from '@babylonjs/core';
import type { DeviceInfo } from '../main';
import { SceneManager } from './SceneManager';
import { UIManager } from '../ui/UIManager';

export class EngineManager {
  public engine: BABYLON.Engine;
  public canvas: HTMLCanvasElement;
  public deviceInfo: DeviceInfo;
  private sceneManager: SceneManager;
  public uiManager!: UIManager;

  constructor(canvas: HTMLCanvasElement, deviceInfo: DeviceInfo) {
    this.canvas = canvas;
    this.deviceInfo = deviceInfo;
    
    // Initialize Engine with Antialiasing configuration based on device
    const options = {
      preserveDrawingBuffer: true,
      stencil: true,
      antialias: deviceInfo.isPC // MSAA only on PC
    };
    
    this.engine = new BABYLON.Engine(canvas, options.antialias, options, true);
    
    // Engine optimization for mobile/PDA
    if (deviceInfo.isMobile || deviceInfo.isPDA) {
       this.engine.setHardwareScalingLevel(1.5); // Downscale resolution slightly to save battery/GPU on PDA
    }

    this.sceneManager = new SceneManager(this.engine, canvas, deviceInfo);
  }

  public async start() {
    await this.sceneManager.initialize();
    
    // Initialize UI Manager
    this.uiManager = new UIManager(this.sceneManager);

    this.engine.runRenderLoop(() => {
      this.sceneManager.render();
    });

    // Resize event
    window.addEventListener('resize', () => {
      this.engine.resize();
    });
  }
}
