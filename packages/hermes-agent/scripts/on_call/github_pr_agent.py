#!/usr/bin/env python3
"""
GitHub PR Agent — thin Hermes wrapper.
Hermes handles everything: reading diff, code review, posting gh pr review.
"""
import os, subprocess, pathlib, logging, time
from datetime import datetime
from dotenv import load_dotenv
from run_agent import AIAgent
from reporter import send_telegram_message, request_approval, get_global_config, NOUS_API_BASE_URL, OPENROUTER_BASE_URL

load_dotenv()
AGENT_ROOT  = pathlib.Path(__file__).parent.parent.parent.resolve()
DATA_DIR    = AGENT_ROOT.parent.parent.resolve() / ".tmp"
LOG_DIR     = AGENT_ROOT / "agent" / "on_call_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def ensure_repo_cloned(owner: str, repo: str) -> pathlib.Path:
    """Clone or pull the target repository into .tmp/owner/repo"""
    repo_dir = DATA_DIR / owner / repo
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    
    if not repo_dir.exists():
        logging.info(f"🚚 Cloning {owner}/{repo} into {repo_dir}")
        subprocess.run(["git", "clone", f"https://github.com/{owner}/{repo}.git", str(repo_dir)], check=True)
    else:
        logging.info(f"🔄 Updating {owner}/{repo} in {repo_dir}")
        subprocess.run(["git", "-C", str(repo_dir), "pull"], check=True)
    return repo_dir


def handle_pr(pr_number: int, title: str = "", author: str = "", owner: str = None, repo: str = None):
    logging.info(f"🔀 Dispatching Hermes for PR #{pr_number} in {owner}/{repo}")

    # Ensure we are looking at the RIGHT codebase
    repo_path = ensure_repo_cloned(owner, repo)

    send_telegram_message(
        f"🔀 *GitHub PR #{pr_number}* at {owner}/{repo}\n*{title}*\nby {author}\n\n🔍 Hermes reviewing..."
    )

    prompt = f"""A new Pull Request #{pr_number} has been opened in the repository {owner}/{repo}.

Title: {title}
Author: {author}

YOUR TASK:
1. Review the PR:
   - Use `gh pr view {pr_number}` and `gh pr diff {pr_number}` to inspect changes.
   - Look for bugs, security issues, or missing tests.
   - Inspect the local codebase at {repo_path} using file tools.
2. Formulate your review.
3. OUTPUT YOUR PROPOSED REVIEW in this format:
   [VERDICT]: <approve|comment|request-changes>
   [ANALYSIS_START]
   <markdown review body>
   [ANALYSIS_END]

I will present this to the human for approval. DO NOT use the terminal tool to post the review yourself.
"""

    log_file = LOG_DIR / f"pr_{pr_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    main_log = LOG_DIR / "monitoring.jsonl"
    
    try:
        # Diagnostic: Check API Keys
        active_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("NOUS_API_KEY")
        
        # Determine base_url and default model
        is_nous = active_key and active_key.startswith("sk-2yd")
        target_base_url = NOUS_API_BASE_URL if is_nous else OPENROUTER_BASE_URL
        fallback_model   = "Hermes-4-405B" if is_nous else "anthropic/claude-3-5-sonnet"
        target_model     = get_global_config("MODEL") or fallback_model

        # Initialize Agent
        agent = AIAgent(
            model=target_model,
            api_key=active_key,
            base_url=target_base_url,
            quiet_mode=True,
            enabled_toolsets=["terminal", "file", "web"],
            ephemeral_system_prompt="You are an autonomous on-call bot. Your goal is to review Pull Requests and provide structured feedback."
        )
        
        # Execute natively
        result = agent.run_conversation(prompt)
        output_text = result.get("final_response", "")
        
        # Log to private and main monitoring
        with open(log_file, "w") as f, open(main_log, "a") as f_main:
            entry = f"\n🔀 [PR Agent] PR #{pr_number} | {owner}/{repo} | {datetime.now().isoformat()}\n"
            f.write(entry); f.write(output_text)
            f_main.write(entry); f_main.write(f"Title: {title}\nReview complete.\n")

    except Exception as e:
        logging.error(f"PR agent failed: {e}")
        send_telegram_message(f"❌ Hermes analysis failed for PR #{pr_number}: {e}")
        return

    # Extract analysis and verdict
    analysis = ""
    verdict = "comment"

    if "[ANALYSIS_START]" in output_text and "[ANALYSIS_END]" in output_text:
        analysis = output_text.split("[ANALYSIS_START]")[1].split("[ANALYSIS_END]")[0].strip()
    
    if "[VERDICT]:" in output_text:
        v_line = output_text.split("[VERDICT]:")[1].split("\n")[0].strip().lower()
        if "approve" in v_line: verdict = "approve"
        elif "request-changes" in v_line: verdict = "request-changes"
    
    if not analysis:
        analysis = output_text[-2000:]
        logging.warning("Tags [ANALYSIS_START/END] not found for PR. Using fallback.")

    # Request Approval
    approval_text = f"Hermes review for PR #{pr_number} is ready.\n\n*Verdict:* `{verdict.upper()}`\n\n*Review Preview:*\n{analysis[:1000]}..."
    approved = request_approval(approval_text, f"pr_{pr_number}_{int(time.time())}")

    if approved:
        logging.info("🚀 Approved! Posting PR review to GitHub.")
        try:
            flag = "--approve" if verdict == "approve" else "--request-changes" if verdict == "request-changes" else "--comment"
            cmd = ["gh", "pr", "review", str(pr_number), "--repo", f"{owner}/{repo}", flag, "--body", analysis]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            send_telegram_message(f"✅ PR review posted to #{pr_number} ({verdict}).")
        except Exception as e:
            logging.error(f"Failed to post PR review: {e}")
            send_telegram_message(f"❌ Failed to post PR review to #{pr_number}: {e}")
    else:
        logging.info("🛑 Rejected by user. Skipping evaluation.")
        send_telegram_message(f"🛑 Review for PR #{pr_number} was rejected by user.")

    logging.info(f"✅ Hermes done for PR #{pr_number}")


if __name__ == "__main__":
    import sys, time
    if len(sys.argv) < 4:
        print("Usage: python github_pr_agent.py <pr_number> <owner> <repo>")
        sys.exit(1)
    handle_pr(int(sys.argv[1]), owner=sys.argv[2], repo=sys.argv[3])
