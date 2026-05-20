const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const axios = require('axios');

let store;
(async () => {
    const StoreModule = await import('electron-store');
    store = new StoreModule.default();
})();

let mainWindow;
let loginWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    title: 'JENNIFER 5 Explorer',
    backgroundColor: '#1e1e2e',
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createMainWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// IPC handlers
ipcMain.handle('get-session', () => {
    return store.get('jennifer_cookie') || '';
});

ipcMain.handle('show-login', async () => {
  loginWindow = new BrowserWindow({
    width: 600,
    height: 700,
    parent: mainWindow,
    modal: true,
    title: 'Jennifer Login',
  });

  loginWindow.loadURL('http://14.241.92.211:7900/login');

  return new Promise((resolve) => {
    loginWindow.on('closed', async () => {
      const cookies = await session.defaultSession.cookies.get({ url: 'http://14.241.92.211:7900' });
      const cookieStr = cookies.map(c => `${c.name}=${c.value}`).join('; ');
      
      if (cookieStr) {
          store.set('jennifer_cookie', cookieStr);
      }
      resolve(cookieStr);
    });
  });
});

ipcMain.handle('fetch-profile', async (event, { url, cookie }) => {
  try {
    const response = await axios.get(url, {
      headers: {
        'Cookie': cookie,
        'Accept': 'application/json, text/plain, */*'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Fetch error:', error.message);
    throw error;
  }
});

// New handler for fetching timeline based xview data
ipcMain.handle('fetch-xview-period', async (event, { stime, etime, sid, oid, instId, cookie }) => {
    // The JENNIFER5 XView data can be retrieved by searching the xview list
    // A common endpoint for this is /xview/point or /xview/timeline, but based on user prompt we need to extract TXID
    // from all xview texts. The user specified:
    // http://14.241.92.211:7900/xview/profile/text?format=json... which requires a TXID.
    // If the user meant fetching *all* TXIDs in a period, we usually need a search API first (like /xview/point).
    // Let's assume the user has a way to get the TXIDs, OR we just expose an API to fetch a period's TXIDs.
    // Given the prompt: "JENNIFER5의 특정 기간 베이스의 모든 xview text 중 transaction을 추출하여 excel에 저장하는 버튼을 하나 만든다."
    // We actually need to hit an endpoint that returns all XView transactions for a period, OR we just fetch the period points.
    
    // For now, let's implement a wrapper. Actually, doing it in renderer is easier if we just need axios. 
    // Wait, the renderer can just call fetch-profile multiple times. Let's keep it here just in case, but return it directly.
});
