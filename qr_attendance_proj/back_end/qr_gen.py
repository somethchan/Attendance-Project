# Takes <date>, <course>

# /opt/jobs/qr_gen.py
import sys, os
import pandas as pd
import base64
import qrcode

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Length check for argv
if len(sys.argv) != 3:
    print("Usage: qr_gen.py <date> <course>", file=sys.stderr)
    raise SystemExit(2)

# Variables
date     = sys.argv[1]
course   = sys.argv[2]
nfs_dir = "/home/nfs"
csv_path = os.path.join(nfs_dir, course, "roster.csv")

print("Verifying QR code directory . . . ")
png_dir = f"/var/lib/attendance/{course}"
if not os.path.isdir(png_dir):
    print("QR code directory not detected generating . . .")
    os.makedirs(png_dir, exist_ok=True)
print("Verifying encryption key directory . . . ")
key_dir = f"/tmp/attendance/keys/{course}"
if not os.path.isdir(key_dir):
    print("Encryption key directory not detected generating . . .")
    os.makedirs(key_dir, exist_ok=True)
try:
    print("Attempting to read .csv file . . .")
    df_0 = pd.read_csv(csv_path)
    print("Success")
except FileNotFoundError:
    print("Error: File Does not Exist.")
    sys.exit(1)
except Exception as e:
    print(f"An error occured: {e}")
    sys.exit(1)

print("Starting QR generation . . .")

def key_gen(key_dir):
    os.makedirs(key_dir, exist_ok=True)

    priv_pem = os.path.join(key_dir, "private_key.pem")
    pub_pem  = os.path.join(key_dir, "public_key.pem")

    if os.path.isfile(priv_pem) and os.path.isfile(pub_pem):
        print(f"Encryption keys exists, skipping generation.")
        return priv_pem, pub_pem

    print(f"Generating private key . . . ")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    print(f"Generating public key . . . ")
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    print(f"Saving keys to disk . . . ")
    with open(priv_pem, "wb") as f:
        f.write(private_pem)
    with open(pub_pem, "wb") as f:
        f.write(public_pem)
    return priv_pem, pub_pem

def load_pub_key(pub_pem_path):
    with open(pub_pem_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def encrypt_qr_data(plaintext: str, key_path: str) -> str:
    encrypt_key = load_pub_key(key_path)
    plaintext_bytes = plaintext.encode("utf-8")
    ciphertext = encrypt_key.encrypt(
        plaintext_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ),
    )

    urlsafe_cipher = base64.urlsafe_b64encode(ciphertext).decode("ascii")
    return urlsafe_cipher

def qr_gen(df_1, date, png_dir, pub_pem):
    for index, row in df_1.iterrows():
        qr_data = f"{row['Username']}|{date}"
        qr_path = os.path.join(png_dir, f"{row['Username']}.png")
        encoded_data = encrypt_qr_data(qr_data, pub_pem)

        qr = qrcode.QRCode(
            box_size=10,
            border=4,
        )
        qr.add_data(encoded_data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        img.save(qr_path)

        print(f"QR code for {row['Username']} generated {index + 1}/{len(df_1)}")


# ------------------------------------------ MAIN ------------------------------------------

print("Checking encryption keys . . . ")
priv_pem, pub_pem = key_gen(key_dir)

print(f"Cleaning dataframe . . . ")
df_1 = df_0[['Username']].copy()
df_1['Username'] = df_1['Username'].str.lstrip('#').str.strip()

print("Generating QR codes . . . ")
qr_gen(df_1, date, png_dir, pub_pem)
