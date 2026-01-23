# Takes <enc_text> <date> <course>

# /opt/jobs/scan.py
import sys, os, sqlite3
import pandas as pd
from functions import decrypt_qr_data
from pathlib import Path
print(">>> scan.py executed")

# Length check for argv
if len(sys.argv) != 4:
    print("Usage: scan.py <enc_text> <date> <course>", file=sys.stderr)
    raise SystemExit(2)

# Read tokens passed in the initial script call
enc_text = sys.argv[1]
date     = sys.argv[2]
course   = sys.argv[3]


# ------------- FILE CONFIGS ---------------
key_dir = f"/tmp/attendance/keys/{course}/"
safe_date = date.replace("/", "-")

# This matches db_gen.py’s output structure
db_dir = Path("/home/nfs") / course
db_path = db_dir / f"{safe_date}.db"
if not db_path.is_file():
    print(f"Error: DB not found at {db_path}")
    sys.exit(1)
# ------------------------------------------

try:
    plaintext = decrypt_qr_data(enc_text, key_dir)
except Exception as e:
    print(f"Error during decryption: {e}", file=sys.stderr)
    sys.exit(1)

try:
    parts = plaintext.split("|")
    Username = parts[0].strip().lstrip("#")

except ValueError:
    print(f"Error: malformed decrypted string: {plaintext!r}")

conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()

    # Ensure Attendance column exists
    cur.execute("PRAGMA table_info(roster);")
    cols = [row[1] for row in cur.fetchall()]
    if "Attendance" not in cols:
        cur.execute("ALTER TABLE roster ADD COLUMN Attendance INTEGER DEFAULT 0;")

    Username = Username.strip().lstrip("#")
    cur.execute(
        "UPDATE roster SET Attendance = 1 WHERE Username = ?;",
        (Username,)
    )

    if cur.rowcount == 0:
        print(f"Warning: Username {Username!r} not found in DB.")
    else:
        print(f"Marked {Username} present in {db_path}")
    conn.commit()
finally:
    conn.close()
