#!/usr/bin/env python3
import os
import subprocess
import logging
import pathlib
from fastapi import FastAPI, BackgroundTasks, Request
import uvicorn
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = FastAPI(title="Hermes Webhook Receiver")
HERMES_CMD = os.getenv("HERMES_CMD", "/Users/alikar/.local/bin/hermes")

def trigger_hermes(payload: dict):
    logging.info(f"🚨 Webhook received! Triggering Hermes for incident...")
    
    working_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
    # Format the payload into a prompt for Hermes with Guidance for Code Analysis
    issue_details = str(payload)[:1000]
    task_prompt = f"""SIMULATED INCIDENT TRIGGER:
{issue_details}

TASK:
1. INVESTIGATE: Use provided mock URL and remote tools (browser, terminal network checks).
2. ANALYZE CODE: You have access to the source code in {working_dir}. If the issue seems related to application logic, search and analyze the code in this directory to find the root cause.
3. ISOLATION RULES: 
   - DO NOT search the local disk for "environment junk" (e.g., old logs, temp files).
   - ONLY analyze source code files (.py, .js, .ts, .tsx) in the project directory.
   - DO NOT attempt to fix the local development environment or Agent's own logs.
4. REPORT: Identify the specific file and line that might be causing the issue (if applicable) and suggest a fix.
5. Focus on infrastructure logic and application source code.
6. Report back via Telegram."""
    
    try:
        # Move to the packages/hermes-agent directory to ensure paths match
        working_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
        log_dir = working_dir / "agent" / "on_call_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / "monitoring.jsonl"
        
        # Prepare environment
        env = os.environ.copy()
        
        # Use Popen to handle auto-approval of sessions via stdin
        proc = subprocess.Popen(
            [HERMES_CMD, "chat", 
             "-q", task_prompt,
             "--model", "Hermes-4-405B",
             "--toolsets", "browser,terminal,file,web"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout for easier streaming
            stdin=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
            cwd=str(working_dir)
        )
        
        # Auto-approve prompts by sending 's\n' (session approval)
        try:
            proc.stdin.write("s\n" * 10)
            proc.stdin.flush()
        except:
            pass
            
        # Stream the output to the log file in real time
        with open(log_file_path, "a", buffering=1) as f:
            f.write(f"\n🚨 Webhook triggered Hermes @ {datetime.now().isoformat()}:\n")
            f.write(f"Query: {task_prompt}\n")
            f.write("─" * 40 + "\n")
            
            for line in proc.stdout:
                if line:
                    f.write(line)
                    f.flush() # Ensure it's written immediately for the UI to see
        
        proc.wait()
        logging.info(f"✅ Hermes Task Finished. Output logged to {log_file_path}")
        
    except Exception as e:
        logging.error(f"⚠️ Hermes Task Error: {str(e)}")

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except:
        payload = {"raw_body": (await request.body()).decode('utf-8')}
    
    background_tasks.add_task(trigger_hermes, payload)
    return {"status": "accepted", "message": "Hermes incident response triggered in background."}

@app.get("/logs")
async def get_logs():
    log_file = pathlib.Path(__file__).parent.parent.parent.resolve() / "agent" / "on_call_logs" / "monitoring.jsonl"
    if log_file.exists():
        with open(log_file, "r") as f:
            return {"logs": f.readlines()}
    return {"logs": []}

if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", 8090))
    logging.info(f"Starting Hermes Webhook Receiver on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
