import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
import subprocess

app = FastAPI()

SECRET = "NicoleSecureRecovery2026!"
BACKUP_DIR = "/mnt/d/backups/daily"

def check_auth(auth):
    if auth != SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return # temporary disable

# ------------------------
# UI
# ------------------------
@app.get("/")
def home():
    path = "/app/ui/index.html"
    if not os.path.exists(path):
        return {"error": "UI not found"}
    return FileResponse(path)

# ------------------------
# Health
# ------------------------
@app.get("/health")   # FIXED spelling
def health():
    return {"status": "ok"}

# ------------------------
# List backups
# ------------------------
@app.get("/backups")
def list_backups(authorization: str = Header(None)):
    check_auth(authorization)

    if not os.path.exists(BACKUP_DIR):
        return {"error": "Backup directory not found"}

    files = []

    for f in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, f)

        if os.path.isfile(path) and f.endswith(".sql.gz"):
            size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)

            files.append({
                "name": f,
                "size_mb": size_mb,
                "modified": os.path.getmtime(path)
            })

    # ✅ Sort newest first
    files.sort(key=lambda x: x["modified"], reverse=True)

    return {"backups": files}

# ------------------------
# Recover selected backup
# ------------------------
@app.post("/recover/{filename}")
def recover_file(filename: str, authorization: str = Header(None)):
    check_auth(authorization)

    filepath = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Backup not found")

    try:
        subprocess.Popen(
            ["/app/scripts/full-recovery.sh", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return {"status": f"Recovery started for {filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------
# Legacy full recovery (optional)
# ------------------------
@app.post("/recover")
def recover_all(authorization: str = Header(None)):
    check_auth(authorization)

    try:
        subprocess.Popen(
            ["/app/scripts/full-recovery.sh"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {"status": "Recovery started (latest backup)"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------
# System status
# ------------------------
@app.get("/status")
def status():
    def check(cmd):
        try:
            subprocess.check_output(cmd, shell=True)
            return "OK"
        except:
            return "FAIL"

    return {
        "n8n": check("docker ps | grep n8n-lab-n8n-1"),
        "postgres": check("docker ps | grep postgres"),
        "cloudflared": check("docker ps | grep cloudflared")
    }
