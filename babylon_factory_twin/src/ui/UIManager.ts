import * as BABYLON from '@babylonjs/core';
import type { SceneManager } from '../core/SceneManager';
import { MinimapController } from './MinimapController';
import type { IMachine } from '../data/model/Types';

export class UIManager {
  private sceneManager: SceneManager;
  private minimapController: MinimapController;
  
  private toggleBtn: HTMLElement;
  private minimapWrapper: HTMLElement;
  private machineInfoContent: HTMLElement;

  constructor(sceneManager: SceneManager) {
    this.sceneManager = sceneManager;
    
    this.toggleBtn = document.getElementById('minimap-toggle') as HTMLElement;
    this.minimapWrapper = document.getElementById('minimap-wrapper') as HTMLElement;
    this.machineInfoContent = document.getElementById('machine-info-content') as HTMLElement;

    this.minimapController = new MinimapController(sceneManager);
    
    this.setupEvents();
    this.setupRaycasting();
  }

  private setupEvents() {
    // Media query toggle for minimap on mobile
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => {
        this.minimapWrapper.classList.toggle('show');
      });
    }
  }

  private setupRaycasting() {
    // When clicking on canvas, raycast to find machine metadata
    this.sceneManager.scene.onPointerObservable.add((pointerInfo) => {
      if (pointerInfo.type === BABYLON.PointerEventTypes.POINTERUP) {
        if (pointerInfo.pickInfo?.hit && pointerInfo.pickInfo.pickedMesh) {
          const mesh = pointerInfo.pickInfo.pickedMesh;
          if (mesh.metadata && mesh.metadata.machineData) {
            this.updateMachineInfo(mesh.metadata.machineData);
          } else {
            // Clicked empty ground
            this.machineInfoContent.innerHTML = '<p>기계를 선택해 주세요.</p>';
          }
        }
      }
    });
  }

  private updateMachineInfo(data: IMachine) {
    let color = '';
    if (data.status === 'RUNNING') color = '#28a745';
    else if (data.status === 'IDLE') color = '#ffc107';
    else color = '#dc3545';

    this.machineInfoContent.innerHTML = `
      <div style="margin-bottom: 8px;"><strong>ID:</strong> ${data.machineId}</div>
      <div style="margin-bottom: 8px;"><strong>설비명:</strong> ${data.name}</div>
      <div style="margin-bottom: 8px;"><strong>유형:</strong> ${data.type}</div>
      <div style="margin-bottom: 8px;">
        <strong>상태:</strong> 
        <span style="color: ${color}; font-weight: bold;">${data.status}</span>
      </div>
      <div style="font-size: 0.8rem; color: #aaa; margin-top: 12px;">
        좌표: { X: ${data.position.x}, Z: ${data.position.z} }
      </div>
    `;
  }
}
