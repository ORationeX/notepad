import './style.css';
import { EngineManager } from './core/EngineManager';

// Device Detection
export interface DeviceInfo {
  isMobile: boolean;
  isPDA: boolean; // Inferring PDA if it's very small screen + touch
  isPC: boolean;
}

export const getDeviceInfo = (): DeviceInfo => {
  const userAgent = navigator.userAgent.toLowerCase();
  const isMobile = /android|webos|iphone|ipad|ipod|blackberry|windows phone/i.test(userAgent);
  
  // A heuristic for PDA: small screen height or specific UA strings often found in enterprise devices
  // Here we use general mobile as a base, but treat low res as PDA constraints
  const isSmallScreen = window.innerWidth <= 768; 
  const isPDA = isMobile && isSmallScreen; 
  
  return {
    isMobile,
    isPDA,
    isPC: !isMobile
  };
};

// Application Bootstrap
const initApp = async () => {
  const deviceInfo = getDeviceInfo();
  console.log('Detected Device Environment:', deviceInfo);

  const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement;
  if (!canvas) throw new Error('Canvas not found');

  // Initialize Engine Manager
  const engineManager = new EngineManager(canvas, deviceInfo);
  await engineManager.start();
};

window.addEventListener('DOMContentLoaded', () => {
  initApp().catch(console.error);
});
