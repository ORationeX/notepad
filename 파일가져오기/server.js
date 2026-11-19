import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { pipeline } from 'node:stream/promises';
import { setDefaultHighWaterMark } from 'node:stream';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const UPLOAD_ROOT = path.join(__dirname, 'uploads');
const INDEX_HTML = fs.readFileSync(path.join(__dirname, 'public', 'index.html'));
const HOST = process.env.HOST || '0.0.0.0';
const PORT = Number(process.env.PORT) || 8086;
const EXTERNAL_PORT = Number(process.env.EXTERNAL_PORT) || 7086;
const FILE_HWM = 8 * 1024 * 1024;
const SOCKET_HWM = 4 * 1024 * 1024;
const OPEN_BROWSER = process.argv.includes('--open') || process.env.OPEN === '1';

setDefaultHighWaterMark(false, SOCKET_HWM);

const RESERVED = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i;
const JSON_HEADERS = {
  'content-type': 'application/json; charset=utf-8',
  'cache-control': 'no-store',
  connection: 'keep-alive',
};

let dayKey = '';
let dayDir = '';

function dayStamp(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}${m}${d}`;
}

async function ensureDayDir() {
  const key = dayStamp();
  if (key !== dayKey) {
    const dir = path.join(UPLOAD_ROOT, key);
    await fs.promises.mkdir(dir, { recursive: true });
    dayKey = key;
    dayDir = dir;
  }
  return dayDir;
}

function safeBaseName(headerValue) {
  let name = decodeURIComponent(headerValue);
  name = name.replaceAll('\\', '/');
  const slash = name.lastIndexOf('/');
  if (slash >= 0) name = name.slice(slash + 1);
  name = name.replace(/[\u0000-\u001f<>:"/\\|?*]/g, '_').replace(/[. ]+$/g, '');
  if (!name || name === '.' || name === '..') name = 'file';
  const dot = name.indexOf('.');
  const stem = dot === -1 ? name : name.slice(0, dot);
  if (RESERVED.test(stem)) name = `_${name}`;
  if (name.length > 160) {
    const extStart = name.lastIndexOf('.');
    const ext = extStart > 0 && name.length - extStart <= 16 ? name.slice(extStart) : '';
    name = name.slice(0, 160 - ext.length) + ext;
  }
  return name;
}

function newId() {
  return `${Date.now().toString(36)}-${randomBytes(4).toString('hex')}`;
}

function sendJson(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    ...JSON_HEADERS,
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
}

const liveJobs = new Map();
let paintTimer = null;
let painted = 0;

function lanUrls() {
  const urls = [];
  for (const entries of Object.values(os.networkInterfaces())) {
    for (const entry of entries || []) {
      if (entry.family === 'IPv4' && !entry.internal) urls.push(`http://${entry.address}:${PORT}`);
    }
  }
  return urls;
}

function clip(text, width) {
  let used = 0;
  let out = '';
  for (const ch of text.replace(/[\r\n]/g, '')) {
    const size = ch.charCodeAt(0) > 255 ? 2 : 1;
    if (used + size > width) {
      out += '..';
      used += 2;
      break;
    }
    out += ch;
    used += size;
  }
  return out + ' '.repeat(Math.max(0, width - used));
}

function sizeText(bytes) {
  if (bytes >= 1024 ** 3) return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
  if (bytes >= 1024 ** 2) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
}

function renderLive(lines) {
  if (!process.stdout.isTTY) {
    if (lines.length) process.stdout.write(`${lines.join(' | ')}\n`);
    return;
  }
  let out = painted > 0 ? `\x1b[${painted}F` : '';
  for (const line of lines) out += `\x1b[2K${line}\n`;
  const extra = painted - lines.length;
  for (let i = 0; i < extra; i += 1) out += '\x1b[2K\n';
  if (extra > 0) out += `\x1b[${extra}F`;
  process.stdout.write(out);
  painted = lines.length;
}

function clearLive() {
  if (!process.stdout.isTTY || painted === 0) {
    painted = 0;
    return;
  }
  process.stdout.write(`\x1b[${painted}F\x1b[J`);
  painted = 0;
}

function paintLive() {
  const now = process.hrtime.bigint();
  const lines = [];
  let totalSpeed = 0;
  for (const job of liveJobs.values()) {
    const raw = Math.max(0, job.socket.bytesRead - job.base);
    job.received = job.total > 0 ? Math.min(raw, job.total) : raw;
    const dt = Number(now - job.markAt) / 1e9;
    if (dt >= 0.2) {
      job.mbps = ((job.received - job.markBytes) / 1048576) / dt;
      job.markBytes = job.received;
      job.markAt = now;
    }
    totalSpeed += job.mbps;
    const pct = job.total > 0 ? Math.min(99.9, (job.received / job.total) * 100) : 0;
    const amount = job.total > 0
      ? `${sizeText(job.received)} / ${sizeText(job.total)}`
      : sizeText(job.received);
    lines.push(`${clip(job.name, 36)} ${job.total > 0 ? `${pct.toFixed(1).padStart(5)}%  ` : ''}${amount}  ${job.mbps.toFixed(1)} MB/s`);
  }
  if (lines.length > 1) lines.unshift(`수신 ${lines.length}건  합계 ${totalSpeed.toFixed(1)} MB/s`);
  renderLive(lines);
  if (liveJobs.size) ensurePaint();
}

function ensurePaint() {
  if (paintTimer || liveJobs.size === 0) return;
  paintTimer = setTimeout(() => {
    paintTimer = null;
    paintLive();
  }, 200);
}

function logLine(text) {
  if (paintTimer) {
    clearTimeout(paintTimer);
    paintTimer = null;
  }
  clearLive();
  process.stdout.write(`${text}\n`);
  if (liveJobs.size) paintLive();
}

async function handleUpload(req, res) {
  const started = process.hrtime.bigint();
  const rawName = req.headers['x-file-name'];
  if (typeof rawName !== 'string' || rawName.length === 0 || rawName.length > 2048) {
    sendJson(res, 400, { error: 'X-File-Name 헤더가 필요합니다.' });
    req.resume();
    return;
  }

  let original;
  try {
    original = safeBaseName(rawName);
  } catch {
    sendJson(res, 400, { error: '파일 이름을 해석할 수 없습니다.' });
    req.resume();
    return;
  }

  const dir = await ensureDayDir();
  const storedDay = dayKey;
  const id = newId();
  const storedName = `${id}__${original}`;
  const dest = path.join(dir, storedName);
  const headerLen = req.headers['content-length'];
  const known = headerLen !== undefined ? Number(headerLen) : 0;
  const total = Number.isFinite(known) && known >= 0 ? known : 0;
  const job = {
    name: original,
    total,
    base: req.socket.bytesRead,
    socket: req.socket,
    received: 0,
    mbps: 0,
    markBytes: 0,
    markAt: started,
  };
  liveJobs.set(id, job);
  ensurePaint();

  const ws = fs.createWriteStream(dest, { flags: 'w', highWaterMark: FILE_HWM });
  try {
    if (total > 0) {
      await new Promise((resolve) => {
        const onError = () => resolve();
        ws.once('error', onError);
        ws.once('open', () => {
          ws.removeListener('error', onError);
          fs.ftruncate(ws.fd, total, () => resolve());
        });
      });
    }
    await pipeline(req, ws);
  } catch (err) {
    liveJobs.delete(id);
    await fs.promises.rm(dest, { force: true }).catch(() => {});
    logLine(`실패 ${original}: ${err.message}`);
    if (!res.headersSent) sendJson(res, 500, { error: '디스크 저장에 실패했습니다.' });
    else res.destroy();
    return;
  }

  liveJobs.delete(id);
  const size = total > 0 ? total : (await fs.promises.stat(dest)).size;
  const ms = Number(process.hrtime.bigint() - started) / 1e6;
  const relativePath = `${storedDay}/${storedName}`;
  sendJson(res, 201, {
    id,
    name: original,
    size,
    storedName,
    relativePath,
  });
  const mbps = ms > 0 ? (size / (1024 * 1024)) / (ms / 1000) : 0;
  logLine(`완료 ${original}  ${sizeText(size)}  ${mbps.toFixed(1)} MB/s  ${relativePath}`);
}

function openFolder() {
  spawn('explorer.exe', [UPLOAD_ROOT], { detached: true, stdio: 'ignore' }).unref();
}

function openBrowser(url) {
  spawn('cmd', ['/c', 'start', '', url], {
    detached: true,
    stdio: 'ignore',
    windowsHide: true,
  }).unref();
}

const server = http.createServer({
  highWaterMark: SOCKET_HWM,
  requestTimeout: 0,
  headersTimeout: 60_000,
  keepAliveTimeout: 30_000,
  connectionsCheckingInterval: 30_000,
}, (req, res) => {
  const url = req.url.split('?', 1)[0];

  if (req.method === 'POST' && url === '/api/upload') {
    handleUpload(req, res).catch((err) => {
      logLine(`실패: ${err.message}`);
      if (!res.headersSent) sendJson(res, 500, { error: '서버 오류' });
    });
    return;
  }

  if (req.method === 'GET' && url === '/api/info') {
    sendJson(res, 200, {
      uploadRoot: UPLOAD_ROOT,
      host: HOST,
      port: server.address()?.port || PORT,
      lan: lanUrls(),
    });
    return;
  }

  if (req.method === 'POST' && url === '/api/open-folder') {
    openFolder();
    sendJson(res, 200, { ok: true });
    return;
  }

  if (req.method === 'GET' && (url === '/' || url === '/index.html')) {
    res.writeHead(200, {
      'content-type': 'text/html; charset=utf-8',
      'content-length': INDEX_HTML.length,
      'cache-control': 'no-cache',
    });
    res.end(INDEX_HTML);
    return;
  }

  if (req.method === 'GET' && url === '/favicon.ico') {
    res.writeHead(204);
    res.end();
    return;
  }

  res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
  res.end('not found');
});

server.on('connection', (socket) => {
  socket.setNoDelay(true);
  socket.setTimeout(0);
});

await fs.promises.mkdir(UPLOAD_ROOT, { recursive: true });

server.listen(PORT, HOST, () => {
  const localUrl = `http://127.0.0.1:${PORT}`;
  console.log('파일 가져오기 서버');
  console.log(`이 PC: ${localUrl}`);
  for (const lanUrl of lanUrls()) console.log(`같은 망: ${lanUrl}`);
  console.log(`포트포워딩: 외부 ${EXTERNAL_PORT} -> 이 PC ${PORT}`);
  console.log(`저장 위치: ${UPLOAD_ROOT}`);
  console.log('형식 제한 없음. 같은 이름도 각각 저장됩니다.');
  if (OPEN_BROWSER) openBrowser(localUrl);
});
