const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 8787);
const ROOT = __dirname;
const ALLOWED_PROXY_HOSTS = new Set([
  'query1.finance.yahoo.com',
  'fred.stlouisfed.org',
  'production.dataviz.cnn.io',
  'polling.finance.naver.com'
]);

const CONTENT_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.js': 'text/javascript; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8'
};

function send(res, status, body, headers = {}) {
  res.writeHead(status, headers);
  res.end(body);
}

function serveStatic(req, res) {
  const requestPath = decodeURIComponent(new URL(req.url, `http://localhost:${PORT}`).pathname);
  const safePath = requestPath === '/' ? '/index.html' : requestPath;
  const filePath = path.normalize(path.join(ROOT, safePath));

  if (!filePath.startsWith(ROOT)) {
    send(res, 403, 'Forbidden', { 'Content-Type': 'text/plain; charset=UTF-8' });
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      send(res, 404, 'Not found', { 'Content-Type': 'text/plain; charset=UTF-8' });
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    send(res, 200, data, {
      'Content-Type': CONTENT_TYPES[ext] || 'application/octet-stream',
      'Cache-Control': 'no-store'
    });
  });
}

async function proxy(req, res) {
  const requestUrl = new URL(req.url, `http://localhost:${PORT}`);
  const targetRaw = requestUrl.searchParams.get('url');

  if (!targetRaw) {
    send(res, 400, 'Missing url', { 'Content-Type': 'text/plain; charset=UTF-8' });
    return;
  }

  let target;
  try {
    target = new URL(targetRaw);
  } catch {
    send(res, 400, 'Invalid url', { 'Content-Type': 'text/plain; charset=UTF-8' });
    return;
  }

  if (!['https:', 'http:'].includes(target.protocol) || !ALLOWED_PROXY_HOSTS.has(target.hostname)) {
    send(res, 403, 'Proxy host is not allowed', { 'Content-Type': 'text/plain; charset=UTF-8' });
    return;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  try {
    const upstream = await fetch(target, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 StockRebalancerLocalProxy/1.0',
        'Accept': '*/*'
      }
    });
    const body = Buffer.from(await upstream.arrayBuffer());
    res.writeHead(upstream.status, {
      'Content-Type': upstream.headers.get('content-type') || 'application/octet-stream',
      'Cache-Control': 'no-store',
      'Access-Control-Allow-Origin': '*'
    });
    res.end(body);
  } catch (err) {
    send(res, 502, `Proxy failed: ${err.message}`, { 'Content-Type': 'text/plain; charset=UTF-8' });
  } finally {
    clearTimeout(timeout);
  }
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith('/proxy?')) {
    proxy(req, res);
    return;
  }
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`Smart Asset Rebalancer: http://localhost:${PORT}/`);
});
