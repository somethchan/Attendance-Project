import ipaddress, sys, subprocess
from fastapi import FastAPI, Request, HTTPException

# Instantiate FastAPI object
app = FastAPI(title="Listener API", version='0.1.1')

QR_SCRIPT = "/opt/attendance/jobs/qr_gen.py" # Inputs: date, course
MAIL_SCRIPT = "/opt/attendance/jobs/mail.py" # Inputs: date, course
DB_SCRIPT = "/opt/attendance/jobs/db_gen.py" # Inputs: date, course
READ_SCRIPT = "/opt/attendance/jobs/scan.py" # Inputs: enc_text

# Define list of permitted IPs
IP_ALLOWED = [ipaddress.ip_network(var) for var in [
    "PLACEHOLDER", # TAremote IP 1
    "127.0.0.1/32" # Local Testing
]]

# Helper function to check if IP address is in the list of permitted IPs
def check_ip(ip_str: str):
    ip = ipaddress.ip_address(ip_str)
    return any(ip in net for net in IP_ALLOWED)

# Middleware to handle unpermitted IPs
# custom HTTPException: https://fastapi.tiangolo.com/tutorial/handling-errors/
# middleware: https://fastapi.tiangolo.com/tutorial/middleware/?utm_source=chatgpt.com#creat>
@app.middleware("http")
async def enforce_allowlist(req: Request, call_next):
    client_ip = req.client.host
    if not check_ip(client_ip):
        raise HTTPException(status_code=403, detail="IP not permitted")
    response = await call_next(req)
    return response

# Read json data that has been posted to http://<server-ip>:<port>/data_qr
@app.post("/data_qr")
async def generate_qr(req: Request):
    data = await req.json()

    # Fields extracted from data
    course = str(data.get("course", ""))
    date = str(data.get("date", ""))

    # Define the command to execute and python binary
    # Takes <date>, <course>
    cmd_db = [sys.executable, DB_SCRIPT, date, course]
    cmd_qr = [sys.executable, QR_SCRIPT, date, course]
    # Feedback Output
    try:
        result_db = subprocess.run(
            cmd_db,
            capture_output=True,
            text=True
        )
        result_qr = subprocess.run(
            cmd_qr,
            capture_output=True,
            text=True
        )
        return {
            "status": "ok",
            "stdout_db": result_db.stdout,
            "stderr_db": result_db.stderr,
            "stdout_qr": result_qr.stdout,
            "stderr_qr": result_qr.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Read json data that has been posted to http://<server-ip>:<port>/mail
@app.post("/mail")
async def mass_mail(req: Request):
    data = await req.json()

    # Fields extracted from data
    course = str(data.get("course", ""))
    date = str(data.get("date", ""))

    # Define the command to execute and python binary
    # Takes <date>, <course>
    cmd = [sys.executable, MAIL_SCRIPT, date, course]

    # Feedback Output
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return {
            "status": "ok",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Read json data that has been posted to http://<server-ip>:<port>/scan
@app.post("/scan")
async def scan(req: Request):
    data = await req.json()

    # Fields extracted from data
    enc_text = str(data.get("enc_text", ""))
    course = str(data.get("course", ""))

    # Define the command to execute and python binary
    # Takes <enc_text> <course>
    cmd = [sys.executable, READ_SCRIPT, enc_text, course]

    # Feedback Output
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return {
            "status": "ok",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))