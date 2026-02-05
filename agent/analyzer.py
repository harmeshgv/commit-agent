import subprocess


def analyze_diff():
    diff = subprocess.getoutput("git diff --staged")
    status = subprocess.getoutput("git status --short")

    return {"diff": diff, "status": status}
