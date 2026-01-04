#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "monitor.log")

CPU_LOAD_THRESHOLD = 2.0
DISK_USED_THRESHOLD = 90.0
RAM_USED_THRESHOLD = 90.0

def read_mem_used_pct() -> float:
    mem_total = None
    mem_avail = None
    with open("/proc/meminfo", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1])  # kB
            elif line.startswith("MemAvailable:"):
                mem_avail = int(line.split()[1])  # kB
    if mem_total is None or mem_avail is None:
        raise RuntimeError("Cannot read /proc/meminfo")
    used = mem_total - mem_avail
    return (used / mem_total) * 100.0

def disk_used_pct(path: str = "/") -> float:
    total, used, _ = shutil.disk_usage(path)
    return (used / total) * 100.0

def cpu_load_1m() -> float:
    return os.getloadavg()[0]

def append_log(line: str) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main() -> int:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    load = cpu_load_1m()
    ram = read_mem_used_pct()
    disk = disk_used_pct("/")

    alerts = []
    if load > CPU_LOAD_THRESHOLD:
        alerts.append(f"CPU_LOAD>{CPU_LOAD_THRESHOLD} (load={load:.2f})")
    if ram > RAM_USED_THRESHOLD:
        alerts.append(f"RAM_USED>{RAM_USED_THRESHOLD}% (ram={ram:.2f}%)")
    if disk > DISK_USED_THRESHOLD:
        alerts.append(f"DISK_USED>{DISK_USED_THRESHOLD}% (disk={disk:.2f}%)")

    status = "OK" if not alerts else "ALERT: " + " | ".join(alerts)
    line = f"[{ts}] load={load:.2f} ram_used={ram:.2f}% disk_used={disk:.2f}% => {status}"
    append_log(line)

    return 0 if not alerts else 2

if __name__ == "__main__":
    raise SystemExit(main())

