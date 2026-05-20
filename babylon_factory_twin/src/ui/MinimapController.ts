import * as BABYLON from '@babylonjs/core';
import type { SceneManager } from '../core/SceneManager';

export class MinimapController {
  private sceneManager: SceneManager;
  public minimapWrapper: HTMLElement;
  public playerIndicator: HTMLElement;
  public floorBtns: NodeListOf<HTMLButtonElement>;
  
  // Minimap scale (how much 3D world fits into minimap)
  // Assuming ground is 50x50, and minimap is 250px or 200px.
  private worldSize = 50;

  constructor(sceneManager: SceneManager) {
    this.sceneManager = sceneManager;
    
    this.minimapWrapper = document.getElementById('minimap-wrapper') as HTMLElement;
    this.playerIndicator = document.getElementById('player-indicator') as HTMLElement;
    this.floorBtns = document.querySelectorAll('.floor-btn');
    
    this.setupEvents();
    this.startSync();
  }

  private setupEvents() {
    // 1. Floor toggle buttons
    this.floorBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLButtonElement;
        const floorId = parseInt(target.getAttribute('data-floor') || '0', 10);
        
        // Update UI
        this.floorBtns.forEach(b => b.classList.remove('active'));
        target.classList.add('active');

        // Update Scene Manager
        this.sceneManager.currentFloorId = floorId;
        this.sceneManager.envBuilder.setVisibleFloor(floorId);
        
        // Teleport camera to new floor Y
        const currentPos = this.sceneManager.camera.position.clone();
        currentPos.y = floorId + 2; // +2 for player height
        this.sceneManager.camera.position = currentPos;
      });
    });

    // 2. Minimap Teleport click/touch
    const canvasArea = document.getElementById('minimap-canvas-area');
    if (canvasArea) {
      canvasArea.addEventListener('click', (e) => {
        this.handleTeleport(e, canvasArea);
      });
      // For PDA/Mobile precise touch
      canvasArea.addEventListener('touchstart', (e) => {
        const touch = e.touches[0];
        // Create a dummy event-like object
        this.handleTeleport({ clientX: touch.clientX, clientY: touch.clientY } as MouseEvent, canvasArea);
        e.preventDefault();
      }, { passive: false });
    }
  }

  private handleTeleport(e: MouseEvent, canvasArea: HTMLElement) {
    const rect = canvasArea.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Convert 2D minimap coordinates [0, width] to 3D map coordinates [-25, 25]
    const width = rect.width;
    const height = rect.height;
    
    const mapX = (x / width) * this.worldSize - (this.worldSize / 2);
    const mapZ = -((y / height) * this.worldSize - (this.worldSize / 2)); // Z is inverted on screen vs 3D

    // Move camera
    const floorY = this.sceneManager.currentFloorId + 2;
    this.sceneManager.camera.position = new BABYLON.Vector3(mapX, floorY, mapZ);
  }

  private startSync() {
    this.sceneManager.scene.onBeforeRenderObservable.add(() => {
      if (!this.sceneManager.camera) return;

      const pos = this.sceneManager.camera.position;
      
      // Calculate percentage on map
      const xPercent = ((pos.x + (this.worldSize / 2)) / this.worldSize) * 100;
      // Z inversion
      const zPercent = ((-pos.z + (this.worldSize / 2)) / this.worldSize) * 100;

      // Clamp values so indicator doesn't leave minimap
      const clampedX = Math.max(0, Math.min(xPercent, 100));
      const clampedY = Math.max(0, Math.min(zPercent, 100));

      this.playerIndicator.style.left = `${clampedX}%`;
      this.playerIndicator.style.top = `${clampedY}%`;
    });
  }
}
