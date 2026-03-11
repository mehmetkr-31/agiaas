#!/usr/bin/env python3
import time
import subprocess
import psutil
import httpx
import os
import logging
import pathlib
from datetime import datetime

# --- Config ---
HERMES_CMD = os.getenv("HERMES_CMD", "/Users/alikar/.local/bin/hermes")
API_URL = os.getenv("API_URL", "http://localhost:8090/logs")  # Example health check
CPU_THRESHOLD = int(os.getenv("CPU_THRESHOLD", 95))
MEM_THRESHOLD = int(os.getenv("MEM_THRESHOLD", 95))
WORKING_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
LOG_FILE = WORKING_DIR / "agent" / "on_call_logs" / "sentinel.log"
MONITORING_JSONL = WORKING_DIR / "agent" / "on_call_logs" / "monitoring.jsonl"

# Setup logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def check_health():
    # 1. Check local API
    try:
        r = httpx.get(API_URL, timeout=5)
        if r.status_code >= 400:
            return f"API returned status {r.status_code}"
    except Exception as e:
        return f"API connection failed: {e}"

    # 2. Check System Stats
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    
    if cpu > CPU_THRESHOLD:
        return f"CPU usage is critical ({cpu}%)"
    if mem > MEM_THRESHOLD:
        return f"Memory usage is critical ({mem}%)"

    return None

def trigger_hermes(issue: str):
    logging.error(f"🚨 SENTINEL ALERT: {issue}. Invoking Hermes On-Call Agent...")
    
    task_prompt = f"""SENTINEL HEALTH MONITOR ALERT:
Issue: {issue}

TASK:
1. INVESTIGATE: Use your tools to check system health, logs, and any provided mock URLs.
2. ANALYZE CODE: You have access to the source code in {WORKING_DIR}. Search and analyze the code to find the root cause of this anomaly.
3. ISOLATION RULES: 
   - ONLY analyze source code files in the project directory.
   - DO NOT attempt to fix the local development environment or Agent's own logs.
4. REPORT: Identify the root cause and suggest a fix. Report back via Telegram.
"""
    
    try:
        # Prepare environment
        env = os.environ.copy()
        
        # Use Popen to stream output to monitoring.jsonl just like the webhook receiver
        proc = subprocess.Popen(
            [HERMES_CMD, "chat", 
             "-q", task_prompt,
             "--model", "Hermes-4-405B",
             "--toolsets", "browser,terminal,file,web"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
            cwd=str(WORKING_DIR)
        )
        
        # Auto-approve prompts
        try:
            proc.stdin.write("s\n" * 10)
            proc.stdin.flush()
        except:
            pass
            
        # Stream the output to the log file in real time
        with open(MONITORING_JSONL, "a", buffering=1) as f:
            f.write(f"\n🚨 Sentinel Monitor triggered Hermes @ {datetime.now().isoformat()}:\n")
            f.write(f"Issue: {issue}\n")
            f.write("─" * 40 + "\n")
            
            for line in proc.stdout:
                if line:
                    f.write(line)
                    f.flush()
        
        proc.wait()
        logging.info(f"✅ Sentinel-triggered Hermes task finished.")
        
    except Exception as e:
        logging.error(f"❌ Failed to trigger Hermes from Sentinel: {e}")

def main():
    logging.info("Sentinel Monitor Active. Watching for anomalies...")
    while True:
        try:
            issue = check_health()
            if issue:
                trigger_hermes(issue)
                # Cool down to avoid spam
                time.sleep(300) 
            else:
                logging.debug("System healthy.")
        except Exception as e:
            logging.error(f"Unexpected error in monitor loop: {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
