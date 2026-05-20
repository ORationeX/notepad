let currentCookie = '';
let fetchedDataList = [];

// DOM Elements
const btnLogin = document.getElementById('btnLogin');
const loginStatus = document.getElementById('loginStatus');
const stimeInput = document.getElementById('stime');
const etimeInput = document.getElementById('etime');
const sidSelect = document.getElementById('sidSelect');
const oidSelect = document.getElementById('oidSelect');
const instIdSelect = document.getElementById('instIdSelect');
const apiTokenInput = document.getElementById('apiToken');
const btnRefreshTargets = document.getElementById('btnRefreshTargets');
const txidListArea = document.getElementById('txidList');
const btnFetch = document.getElementById('btnFetch');
const btnFetchPeriod = document.getElementById('btnFetchPeriod');
const btnExport = document.getElementById('btnExport');
const btnClear = document.getElementById('btnClear');
const resultsTable = document.getElementById('resultsTable').querySelector('tbody');
const resultCount = document.getElementById('resultCount');
const debugOutput = document.getElementById('debugOutput');
const btnClearLogs = document.getElementById('btnClearLogs');

let domains = [];
let instances = [];

// Helper: Append Token if exists
function withToken(url) {
    const token = apiTokenInput.value.trim();
    if (!token) return url;
    const connector = url.includes('?') ? '&' : '?';
    return `${url}${connector}token=${token}`;
}

// Helper: Logging
function logDebug(msg) {
    const timestamp = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.textContent = `[${timestamp}] ${msg}`;
    debugOutput.prepend(entry);
    console.log(msg);
}

btnClearLogs.addEventListener('click', () => { debugOutput.innerHTML = ''; });

// Initialize Session on Load
window.addEventListener('DOMContentLoaded', async () => {
    // Session setup
    const savedCookie = await window.electronAPI.getSession();
    if (savedCookie) {
        currentCookie = savedCookie;
        loginStatus.textContent = 'Online (Cached)';
        loginStatus.className = 'status online';
        logDebug('Session loaded from cache.');
        loadTargets();
    }
    
    // Set Default Times (Last 1 hour)
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - (60 * 60 * 1000));
    const formatDateTime = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    };
    stimeInput.value = formatDateTime(oneHourAgo);
    etimeInput.value = formatDateTime(now);
});

// Load Domains and Instances
async function loadTargets() {
    if (!currentCookie) {
        logDebug('Cannot load targets: Not logged in.');
        return;
    }
    btnRefreshTargets.disabled = true;
    btnRefreshTargets.textContent = '...';
    sidSelect.innerHTML = '<option value="">Loading Domains...</option>';

    try {
        logDebug('Fetching Domain list...');
        let dData = null;
        const endpoints = [
            withToken('http://14.241.92.211:7900/topology/domain/list?format=json'),
            withToken('http://14.241.92.211:7900/api/domain/list?format=json'),
            withToken('http://14.241.92.211:7900/common/domain/list?format=json'),
            withToken('http://14.241.92.211:7900/common/target/list?format=json')
        ];

        for (const url of endpoints) {
            try {
                dData = await window.electronAPI.fetchProfile({ url, cookie: currentCookie });
                if (dData && !dData.exception) {
                    logDebug(`Domains response received from ${new URL(url).pathname}`);
                    break; 
                }
            } catch (e) { logDebug(`E: Failed ${new URL(url).pathname}`); }
        }
        
        let foundDomains = [];
        if (dData) {
            if (dData.domain) foundDomains = dData.domain;
            else if (dData.items) foundDomains = dData.items;
            else if (Array.isArray(dData)) foundDomains = dData;
        }
        
        domains = foundDomains;
        
        if (domains.length === 0) {
            logDebug('W: Domain response empty or invalid format.');
            sidSelect.innerHTML = '<option value="1000">1000 (Manual Default)</option>';
        } else {
            sidSelect.innerHTML = '';
            domains.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d.id || d.sid || d.domainId;
                opt.textContent = `[${d.id || d.sid || d.domainId}] ${d.name || d.label}`;
                if (d.instances || d.instance || d.agents || d.agentList) {
                    opt.dataset.instances = JSON.stringify(d.instances || d.instance || d.agents || d.agentList);
                }
                sidSelect.appendChild(opt);
            });
            logDebug(`${domains.length} domains added.`);
        }

        if (sidSelect.value) {
            loadInstances(sidSelect.value);
        }
    } catch (err) {
        logDebug(`Critical Error: ${err.message}`);
        sidSelect.innerHTML = '<option value="1000">1000 (Fallback)</option>';
    }

    btnRefreshTargets.disabled = false;
    btnRefreshTargets.textContent = '🔄 Load';
}

async function loadInstances(sid) {
    if (!sid || !currentCookie) return;
    oidSelect.innerHTML = '<option value="">Searching Instances...</option>';
    logDebug(`Searching Instances for SID: ${sid}...`);

    try {
        let iData = null;
        
        // 1. Nested Check
        const selectedSidOpt = sidSelect.options[sidSelect.selectedIndex];
        if (selectedSidOpt && selectedSidOpt.dataset.instances) {
            const nested = JSON.parse(selectedSidOpt.dataset.instances);
            if (nested && nested.length > 0) {
                logDebug(`Using ${nested.length} nested instances from Domain.`);
                populateOidSelect(nested);
                return;
            }
        }

        // 2. HTTP endpoints
        const endpoints = [
            withToken(`http://14.241.92.211:7900/topology/instance/list?format=json&sid=${sid}`),
            withToken(`http://14.241.92.211:7900/topology/instance/list?format=json&domainId=${sid}`),
            withToken(`http://14.241.92.211:7900/api/instance/list?format=json&sid=${sid}`),
            withToken(`http://14.241.92.211:7900/api/instance/list?format=json&domainId=${sid}`),
            withToken(`http://14.241.92.211:7900/common/target/list?format=json&sid=${sid}`),
            withToken(`http://14.241.92.211:7900/common/target/list?format=json&domainId=${sid}`),
            withToken(`http://14.241.92.211:7900/topology/instance/list?format=json`)
        ];

        for (const url of endpoints) {
            try {
                iData = await window.electronAPI.fetchProfile({ url, cookie: currentCookie });
                if (iData && !iData.exception) {
                    logDebug(`Instance response received from ${new URL(url).pathname}`);
                    break;
                }
            } catch (e) { /* silent try */ }
        }
        
        let foundInstances = [];
        if (iData) {
            if (iData.instance) foundInstances = iData.instance;
            else if (iData.instances) foundInstances = iData.instances;
            else if (iData.instanceList) foundInstances = iData.instanceList;
            else if (iData.agents) foundInstances = iData.agents;
            else if (iData.agentList) foundInstances = iData.agentList;
            else if (iData.items) foundInstances = iData.items;
            else if (iData.list) foundInstances = iData.list;
            else if (Array.isArray(iData)) foundInstances = iData;
        }

        populateOidSelect(foundInstances);

    } catch (err) {
        logDebug(`Instance Search Error: ${err.message}`);
        oidSelect.innerHTML = '<option value="">Search Failed</option>';
    }
}

function populateOidSelect(list) {
    if (!list || list.length === 0) {
        logDebug('W: No instance data found after exhaustive search.');
        oidSelect.innerHTML = '<option value="">No instances found</option>';
        return;
    }

    oidSelect.innerHTML = '';
    list.forEach(i => {
        const opt = document.createElement('option');
        opt.value = i.id || i.oid || i.instanceId || i.sid; // Fallback to id
        opt.dataset.instId = i.instId || i.id || i.oid;
        opt.textContent = `[${i.id || i.oid || i.instanceId}] ${i.name || i.label || 'Unknown Agent'}`;
        oidSelect.appendChild(opt);
    });
    logDebug(`${list.length} instances added to dropdown.`);
}

sidSelect.addEventListener('change', (e) => loadInstances(e.target.value));
btnRefreshTargets.addEventListener('click', loadTargets);

// Helper: Get timestamp from input
function getTimestamps() {
    const sVal = stimeInput.value;
    const eVal = etimeInput.value;
    
    const stime = sVal ? new Date(sVal).getTime() : Date.now() - 3600000;
    const etime = eVal ? new Date(eVal).getTime() : Date.now();
    
    return { stime, etime };
}

// Login Logic (with auto load targets)
btnLogin.addEventListener('click', async () => {
  loginStatus.textContent = 'Logging in...';
  loginStatus.className = 'status';
  
  try {
    currentCookie = await window.electronAPI.showLogin();
    if (currentCookie) {
      loginStatus.textContent = 'Online';
      loginStatus.className = 'status online';
      loadTargets(); // Auto load targets on successful login
    } else {
      loginStatus.textContent = 'Failed';
      loginStatus.className = 'status offline';
    }
  } catch (err) {
    console.error(err);
    loginStatus.textContent = 'Error';
    loginStatus.className = 'status offline';
  }
});

// Clear Data
btnClear.addEventListener('click', () => {
  txidListArea.value = '';
  fetchedDataList = [];
  resultsTable.innerHTML = '';
  resultCount.textContent = '0 items';
  btnExport.disabled = true;
});

// Fetch Period Logic
btnFetchPeriod.addEventListener('click', async () => {
    if (!currentCookie) return alert('Please login first!');
    if (!sidSelect.value || !oidSelect.value) return alert('Please select Domain and Instance!');
    
    const { stime, etime } = getTimestamps();
    const sid = sidSelect.value;
    const oid = oidSelect.value;
    // instId is often needed as a separate param in some JENNIFER5 versions
    const selectedOidOpt = oidSelect.options[oidSelect.selectedIndex];
    const instId = selectedOidOpt.dataset.instId || oid;

    btnFetchPeriod.disabled = true;
    btnFetchPeriod.textContent = 'Fetching...';

    const url = withToken(`http://14.241.92.211:7900/xview/point?format=json&sid=${sid}&oid=${oid}&instId=${instId}&stime=${stime}&etime=${etime}`);
    
    addResultRow(`Period ${new Date(stime).toLocaleString()}-${new Date(etime).toLocaleString()}`, 'Fetching Points...');

    try {
        const data = await window.electronAPI.fetchProfile({ url, cookie: currentCookie });
        
        let txidsFound = [];
        
        if (Array.isArray(data)) {
            txidsFound = data.map(item => item.txid || item.transactionId || item.id).filter(Boolean);
        } else if (data && Array.isArray(data.items)) {
             txidsFound = data.items.map(item => item.txid || item.transactionId || item.id).filter(Boolean);
        } else if (typeof data === 'string') {
            const matches = [...data.matchAll(/txid["']?\s*[:=]\s*["']?(\d+)/gi)];
            txidsFound = matches.map(m => m[1]);
        }

        txidsFound = [...new Set(txidsFound)];

        if (txidsFound.length > 0) {
           txidsFound.forEach(tx => {
               fetchedDataList.push({ TXID: tx, FullData: 'Fetched via period search' });
           });
           updateRowStatus(`Period ${new Date(stime).toLocaleString()}-${new Date(etime).toLocaleString()}`, `Success (${txidsFound.length} found)`);
        } else {
             updateRowStatus(`Period ${new Date(stime).toLocaleString()}-${new Date(etime).toLocaleString()}`, `Success (0 found)`);
        }
    } catch (err) {
        console.error(err);
        updateRowStatus(`Period ${new Date(stime).toLocaleString()}-${new Date(etime).toLocaleString()}`, 'Error');
    }

    btnFetchPeriod.disabled = false;
    btnFetchPeriod.textContent = '🕒 Fetch All in Period';
    btnExport.disabled = fetchedDataList.length === 0;
    resultCount.textContent = `${fetchedDataList.length} items`;
});

// Fetch Logic (Specific TXIDs)
btnFetch.addEventListener('click', async () => {
  const txidRaw = txidListArea.value.trim();
  if (!txidRaw) return alert('Please enter TXIDs!');
  if (!currentCookie) return alert('Please login first!');
  if (!sidSelect.value || !oidSelect.value) return alert('Please select Domain and Instance!');

  const txids = txidRaw.split(/\n|,/).map(tx => tx.trim()).filter(tx => tx.length > 0);
  btnFetch.disabled = true;
  btnFetch.textContent = 'Processing...';

  const { stime, etime } = getTimestamps();
  const sid = sidSelect.value;
  const oid = oidSelect.value;
  const selectedOidOpt = oidSelect.options[oidSelect.selectedIndex];
  const instId = selectedOidOpt.dataset.instId || oid;

  for (const txid of txids) {
    let finalTxid = txid;
    if (txid.includes('txid=')) {
        finalTxid = new URLSearchParams(txid.split('?')[1]).get('txid');
    }

    const url = withToken(`http://14.241.92.211:7900/xview/profile/text?format=json&sid=${sid}&oid=${oid}&instId=${instId}&stime=${stime}&etime=${etime}&txid=${finalTxid}`);
    
    addResultRow(finalTxid, 'Fetching...');

    try {
      const data = await window.electronAPI.fetchProfile({ url, cookie: currentCookie });
      
      let foundTxid = '';
      if (typeof data === 'string') {
          const match = data.match(/TXID\s*:\s*(\d+)/i);
          foundTxid = match ? match[1] : finalTxid;
      } else if (data && data.txid) {
          foundTxid = data.txid;
      } else {
          foundTxid = finalTxid;
      }

      fetchedDataList.push({ TXID: foundTxid, FullData: typeof data === 'string' ? data.substring(0, 100) : JSON.stringify(data).substring(0, 100) + '...' });
      updateRowStatus(finalTxid, 'Success', foundTxid);
    } catch (err) {
      console.error(err);
      updateRowStatus(finalTxid, 'Error');
    }
  }

  btnFetch.disabled = false;
  btnFetch.textContent = '🚀 Start Fetching Profiles';
  btnExport.disabled = fetchedDataList.length === 0;
  resultCount.textContent = `${fetchedDataList.length} items`;
});

function addResultRow(txid, status) {
  const row = document.createElement('tr');
  // Safe ID creation for period
  const safeId = String(txid).replace(/[^a-zA-Z0-9_-]/g, '-');
  row.id = `row-${safeId}`;
  row.innerHTML = `
    <td>${txid}</td>
    <td class="status-cell">${status}</td>
    <td>${new Date().toLocaleTimeString()}</td>
  `;
  resultsTable.appendChild(row);
}

function updateRowStatus(txid, status, actualTxid = '') {
  const safeId = String(txid).replace(/[^a-zA-Z0-9_-]/g, '-');
  const row = document.getElementById(`row-${safeId}`);
  if (row) {
    const statusCell = row.querySelector('.status-cell');
    statusCell.textContent = status;
    statusCell.style.color = status.includes('Success') ? '#50fa7b' : '#ff5555';
    if (actualTxid) {
        row.firstChild.textContent = actualTxid;
    }
  }
}

// Export Logic
btnExport.addEventListener('click', () => {
  if (fetchedDataList.length === 0) return;
  
  const worksheet = XLSX.utils.json_to_sheet(fetchedDataList.map(item => ({ 'TXID': item.TXID })));
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "TXID List");
  
  const filename = `Jennifer_TXIDs_${Date.now()}.xlsx`;
  XLSX.writeFile(workbook, filename);
  alert(`Exported to ${filename}`);
});
