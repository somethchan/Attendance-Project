# Takes <enc_text> <course>

# /opt/jobs/scan.py
import sys, os, sqlite3
import base64

from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Length check for argv
if len(sys.argv) != 4:
    print("Usage: scan.py <enc_text> <date> <course>", file=sys.stderr)
    raise SystemExit(2)

# Variables
enc_text = sys.argv[1]
date     = sys.argv[2]
course   = sys.argv[3]
key_dir = f"/tmp/attendance/keys/{course}"
safe_date = date.replace("/", "-")
db_dir = Path("/home/nfs") / course
db_path = db_dir / f"{safe_date}.db"
priv_pem = os.path.join(key_dir, "private_key.pem")

if not db_path.is_file():
    print(f"Error: DB not found at {db_path}")
    sys.exit(1)
if not os.path.isfile(priv_pem):
    print(f"Error: private key not found at {priv_pem}", file=sys.stderr)
    sys.exit(1)

def load_priv_key(priv_pem_path):
    with open(priv_pem_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_qr_data(encoded_data: str, key_path: str) -> str:
    decrypt_key = load_priv_key(key_path)
    ciphertext = base64.urlsafe_b64decode(encoded_data)
    print("Ciphertext length (bytes):", len(ciphertext))
    plaintext_bytes = decrypt_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plaintext_bytes.decode("utf-8")

# ------------------------------------------ MAIN ------------------------------                                                                                                             ------------

try:
    plaintext = decrypt_qr_data(enc_text, priv_pem)
except Exception as e:
    print(f"Error during decryption: {e}", file=sys.stderr)
    sys.exit(1)
parts = plaintext.split("|")
Username = parts[0].strip().lstrip("#")

conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()

    # Ensure Attendance column exists
    cur.execute("PRAGMA table_info(roster);")
    cols = [row[1] for row in cur.fetchall()]
    if "Attendance" not in cols:
        cur.execute("ALTER TABLE roster ADD COLUMN Attendance INTEGER DEFAULT 0;                                                                                                             ")

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
