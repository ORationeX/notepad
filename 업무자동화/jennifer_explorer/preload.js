const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  showLogin: () => ipcRenderer.invoke('show-login'),
  fetchProfile: (data) => ipcRenderer.invoke('fetch-profile', data),
  getSession: () => ipcRenderer.invoke('get-session'),
});
