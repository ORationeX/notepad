"""Start Streamlit even when the previous server still holds the port."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREFERRED_PORT = 8501
LAST_PORT = 8510
READY_SEC = 25
RETRIES = 3


def log(msg: str) -> None:
    line = time.strftime("%H:%M:%S") + " " + msg
    print(line, flush=True)
    with (ROOT / "run.log").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def listening_pid(port: int) -> int | None:
    try:
        out = subprocess.check_output(["netstat", "-ano"], text=True, encoding="oem", errors="ignore")
    except (OSError, subprocess.CalledProcessError):
        return None
    suffix = f":{port}"
    for raw in out.splitlines():
        if "LISTENING" not in raw.upper():
            continue
        parts = raw.split()
        if len(parts) < 4:
            continue
        local = parts[1]
        if local.endswith(suffix):
            try:
                pid = int(parts[-1])
            except ValueError:
                continue
            if pid:
                return pid
    return None


def process_command(pid: int) -> str:
    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine",
            ],
            capture_output=True,
            text=True,
            timeout=12,
        )
        return (completed.stdout or "") + (completed.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return ""


def is_our_server(pid: int) -> bool:
    cmd = process_command(pid).lower()
    root = str(ROOT).lower()
    return "streamlit" in cmd or "app.py" in cmd or root in cmd


def kill_pid(pid: int) -> None:
    subprocess.run(["taskkill", "/F", "/PID", str(pid), "/T"], capture_output=True, text=True)


def wait_until_free(port: int, seconds: float = 5.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if listening_pid(port) is None:
            return True
        time.sleep(0.3)
    return listening_pid(port) is None


def pick_port() -> int:
    for port in range(PREFERRED_PORT, LAST_PORT + 1):
        pid = listening_pid(port)
        if pid is None:
            return port
        if is_our_server(pid):
            log(f"port {port} held by old server pid {pid}; stopping it")
            kill_pid(pid)
            if wait_until_free(port):
                return port
        else:
            log(f"port {port} busy (pid {pid}); trying next")
    raise RuntimeError("no free port in 8501-8510")


def port_answers(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def wait_ready(port: int, proc: subprocess.Popen) -> bool:
    deadline = time.time() + READY_SEC
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        if port_answers(port):
            return True
        time.sleep(0.4)
    return port_answers(port)


def run_once() -> int:
    port = pick_port()
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "app.py"),
        "--server.headless=true",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    log("starting: " + " ".join(cmd))
    proc = subprocess.Popen(cmd, cwd=str(ROOT))
    if not wait_ready(port, proc):
        log("server did not become ready; stopping")
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        leftover = listening_pid(port)
        if leftover:
            kill_pid(leftover)
        return proc.returncode or 1
    url = f"http://127.0.0.1:{port}"
    log(f"ready {url}")
    try:
        webbrowser.open(url)
    except Exception as exc:  # noqa: BLE001
        log(f"browser open failed: {exc}")
    try:
        return int(proc.wait())
    except KeyboardInterrupt:
        log("stop requested")
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        return 0


def attach_if_running() -> bool:
    pid = listening_pid(PREFERRED_PORT)
    if pid is None or not is_our_server(pid) or not port_answers(PREFERRED_PORT):
        return False
    url = f"http://127.0.0.1:{PREFERRED_PORT}"
    log(f"already running {url}; opening browser")
    try:
        webbrowser.open(url)
    except Exception as exc:  # noqa: BLE001
        log(f"browser open failed: {exc}")
    while listening_pid(PREFERRED_PORT) == pid:
        time.sleep(1)
    return True


def main() -> int:
    os.chdir(ROOT)
    if attach_if_running():
        return 0
    last = 1
    for attempt in range(1, RETRIES + 1):
        log(f"launch attempt {attempt}/{RETRIES}")
        try:
            last = run_once()
        except Exception as exc:  # noqa: BLE001
            log(f"launch error: {exc}")
            last = 1
        if last == 0:
            return 0
        log(f"exit code {last}; retrying")
        time.sleep(2)
    return last


if __name__ == "__main__":
    sys.exit(main())
