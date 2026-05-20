import * as BABYLON from '@babylonjs/core';
import { DeviceInfo } from '../main';

export class InputManager {
  private camera: BABYLON.UniversalCamera;
  private canvas: HTMLCanvasElement;
  private deviceInfo: DeviceInfo;
  
  // Babylon native virtual joystick
  private leftJoystick: BABYLON.VirtualJoystick | null = null;
  private rightJoystick: BABYLON.VirtualJoystick | null = null;

  constructor(camera: BABYLON.UniversalCamera, canvas: HTMLCanvasElement, deviceInfo: DeviceInfo) {
    this.camera = camera;
    this.canvas = canvas;
    this.deviceInfo = deviceInfo;

    // Movement speed settings
    this.camera.speed = 0.3;
    this.camera.angularSensibility = 4000;
  }

  public attachControls() {
    if (this.deviceInfo.isPC) {
      this.attachPCControls();
    } else {
      this.attachMobileControls();
    }
  }

  private attachPCControls() {
    // Default attach uses WASD or Arrows if configured
    this.camera.attachControl(this.canvas, true);
    
    // Explicitly set WASD
    this.camera.keysUp = [87];    // W
    this.camera.keysDown = [83];  // S
    this.camera.keysLeft = [65];  // A
    this.camera.keysRight = [68]; // D
  }

  private attachMobileControls() {
    // On mobile, we use virtual joysticks for movement/rotation
    // Note: Babylon's VirtualJoystick automatically creates a canvas overlay globally
    this.leftJoystick = new BABYLON.VirtualJoystick(true); // Left for movement
    this.rightJoystick = new BABYLON.VirtualJoystick(false); // Right for rotation/pan
    
    if (BABYLON.VirtualJoystick.Canvas) BABYLON.VirtualJoystick.Canvas.style.zIndex = '4'; // Ensure it's under our UI layer (z-index: 10)

    // Optional: We can adjust VirtualJoystick size for PDA
    if (this.deviceInfo.isPDA) {
      if (BABYLON.VirtualJoystick.Canvas) BABYLON.VirtualJoystick.Canvas.style.opacity = '0.6';
    }

    // Attach touch control mapping to camera
    // Normally, the universal camera uses VirtualJoysticksCamera inputs if we swap it,
    // but we can manually map joystick deltas to camera pos/rot in scene 'onBeforeRender' loop.
    this.camera.getScene().onBeforeRenderObservable.add(() => this.updateJoystickTransform());
    
    // For pinch-to-zoom (FOV change as requested for mobile)
    this.setupPinchZoom();
  }

  private updateJoystickTransform() {
    if (this.leftJoystick && this.leftJoystick.pressed) {
      // Move camera based on left joystick using camera direction vectors
      const forward = this.camera.getDirection(BABYLON.Vector3.Forward());
      const right = this.camera.getDirection(BABYLON.Vector3.Right());
      
      forward.y = 0; right.y = 0; // Prevent flying
      forward.normalize(); right.normalize();

      const deltaX = this.leftJoystick.deltaPosition.x;
      const deltaY = this.leftJoystick.deltaPosition.y;

      const moveVec = right.scale(deltaX).add(forward.scale(deltaY));
      this.camera.cameraDirection.addInPlace(moveVec.scale(this.camera.speed * 0.1));
    }

    if (this.rightJoystick && this.rightJoystick.pressed) {
      // Rotate camera based on right joystick
      const deltaX = this.rightJoystick.deltaPosition.x;
      const deltaY = this.rightJoystick.deltaPosition.y;
      
      this.camera.cameraRotation.y += deltaX * 0.05;
      this.camera.cameraRotation.x -= deltaY * 0.05; // Invert Y
    }
  }

  private setupPinchZoom() {
    // Add simple multipoint touch for FOV zooming
    let initialDistance = 0;
    let initialFov = this.camera.fov;

    this.canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 2) {
        initialDistance = Math.hypot(
          e.touches[0].pageX - e.touches[1].pageX,
          e.touches[0].pageY - e.touches[1].pageY
        );
        initialFov = this.camera.fov;
      }
    }, { passive: false });

    this.canvas.addEventListener('touchmove', (e) => {
      if (e.touches.length === 2) {
        const currentDistance = Math.hypot(
          e.touches[0].pageX - e.touches[1].pageX,
          e.touches[0].pageY - e.touches[1].pageY
        );
        
        const zoomFactor = initialDistance / currentDistance;
        let newFov = initialFov * zoomFactor;
        
        // Clamp FOV
        newFov = Math.max(0.5, Math.min(newFov, 2.0));
        this.camera.fov = newFov;
        // Don't prevent default if it breaks joysticks, just manage FOV
      }
    }, { passive: false });
  }

  public dispose() {
    this.camera.detachControl();
    if (this.leftJoystick) this.leftJoystick.releaseCanvas();
    if (this.rightJoystick) this.rightJoystick.releaseCanvas();
  }
}
