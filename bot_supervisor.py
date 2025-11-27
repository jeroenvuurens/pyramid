import threading
import subprocess
import time
import os
import signal
from git import Repo

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
BOT_SCRIPT = os.path.join(REPO_PATH, "bot.py")
CHECK_INTERVAL = 60  # seconds

def run_bot():
    return subprocess.Popen(["python3", BOT_SCRIPT])

def get_latest_commit(repo):
    return repo.head.commit.hexsha

def main():
    repo = Repo(REPO_PATH)
    last_commit = get_latest_commit(repo)
    bot_proc = run_bot()
    print(f"Started bot.py with PID {bot_proc.pid}")
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            repo.remotes.origin.fetch()
            new_commit = get_latest_commit(repo)
            if new_commit != last_commit:
                print("Repo updated. Pulling changes and restarting bot.py...")
                bot_proc.terminate()
                bot_proc.wait()
                repo.remotes.origin.pull()
                last_commit = get_latest_commit(repo)
                bot_proc = run_bot()
                print(f"Restarted bot.py with PID {bot_proc.pid}")
    except KeyboardInterrupt:
        print("Terminating bot supervisor...")
        bot_proc.terminate()
        bot_proc.wait()

if __name__ == "__main__":
    main()
