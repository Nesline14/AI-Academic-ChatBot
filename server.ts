import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

const app = express();
const PORT = 3000;
const FLASK_PORT = 5000;
const FLASK_URL = `http://127.0.0.1:${FLASK_PORT}`;

let flaskProcess: ChildProcess | null = null;

function startFlaskServer() {
  console.log('[CampusConnect Bridge] Starting Python Flask backend on port ' + FLASK_PORT + '...');
  
  // Set FLASK_PORT and FLASK_RUN_PORT in environment
  const env = {
    ...process.env,
    PORT: `${FLASK_PORT}`,
    FLASK_RUN_PORT: `${FLASK_PORT}`,
    PYTHONUNBUFFERED: '1'
  };

  flaskProcess = spawn('python3', ['app.py'], {
    env,
    cwd: process.cwd(),
    stdio: 'inherit'
  });

  flaskProcess.on('error', (err) => {
    console.error('[CampusConnect Bridge] Failed to start Python Flask process:', err);
  });

  flaskProcess.on('exit', (code, signal) => {
    console.log(`[CampusConnect Bridge] Python Flask process exited with code ${code} (signal: ${signal})`);
    if (code !== 0 && !signal) {
      console.log('[CampusConnect Bridge] Restarting Python Flask backend in 2 seconds...');
      setTimeout(startFlaskServer, 2000);
    }
  });
}

// Start Flask process
startFlaskServer();

// Clean up on process exit
process.on('SIGINT', () => {
  if (flaskProcess) flaskProcess.kill('SIGINT');
  process.exit();
});
process.on('SIGTERM', () => {
  if (flaskProcess) flaskProcess.kill('SIGTERM');
  process.exit();
});

// Proxy all requests to Flask app
const flaskProxy = createProxyMiddleware({
  target: FLASK_URL,
  changeOrigin: true,
  ws: true,
  xfwd: true,
  cookieDomainRewrite: '',
  cookiePathRewrite: '/',
  on: {
    error: (err, req, res) => {
      console.error('[CampusConnect Proxy Error]:', err.message);
      const httpRes = res as import('http').ServerResponse;
      if (httpRes && !httpRes.headersSent && typeof httpRes.writeHead === 'function') {
        httpRes.writeHead(502, { 'Content-Type': 'text/html' });
        httpRes.end(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>CampusConnect Starting...</title>
            <meta http-equiv="refresh" content="2">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
          </head>
          <body class="bg-light d-flex align-items-center justify-content-center" style="min-height: 100vh;">
            <div class="card p-4 shadow-sm text-center" style="max-width: 420px;">
              <div class="spinner-border text-primary mb-3 mx-auto" role="status"></div>
              <h4 class="fw-bold mb-1">Starting CampusConnect</h4>
              <p class="text-muted small mb-0">Initializing Python Flask server and seeding SQLite database...</p>
            </div>
          </body>
          </html>
        `);
      }
    }
  }
});

app.use(flaskProxy);

app.listen(PORT, '0.0.0.0', () => {
  console.log(`CampusConnect Gateway running on http://0.0.0.0:${PORT} -> Forwarding to Flask :${FLASK_PORT}`);
});
