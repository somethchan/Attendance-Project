# [Import Statements]: Libraries
import smtplib
import qrcode
import pandas as pd
import os
import rsa
import re
import base64

# [Import Statements]: Functions
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# [Function]: encryption keygen
def key_gen(course):
    # [Configuration]: Key directory
    key_dir = f"/etc/attendance/keys/{course}"
    os.makedirs(key_dir, exist_ok=True)

    priv_path = os.path.join(key_dir, "private_key.pem")
    pub_path  = os.path.join(key_dir, "public_key.pem")

    if os.path.isfile(priv_path) and os.path.isfile(pub_path):
        print(f"Keys already exist for course {course}, skipping generation.")
        return

    # [Generate]: Public/Private key
    publicKey, privateKey = rsa.newkeys(2048)

    with open(priv_path, "wb") as priv_file:
        priv_file.write(privateKey.save_pkcs1("PEM"))
    with open(pub_path, "wb") as pub_file:
        pub_file.write(publicKey.save_pkcs1("PEM"))

# [Function]: load public key
def load_pubkey(key_dir):
    #  [Configuration]: public key path
    key_path=os.path.join(key_dir, "public_key.pem")
    with open(key_path, "rb") as pub_file:
        key_data = pub_file.read()
        public_key = rsa.PublicKey.load_pkcs1(key_data)
    return public_key

# [Function]: Load RSA Private Key
def load_rsa_private_key(key_dir):
    key_path=os.path.join(key_dir, "private_key.pem")
    with open(key_path, "rb") as priv_file:
        key_data = priv_file.read()
        private_key = rsa.PrivateKey.load_pkcs1(key_data)
    return private_key

# [Function]: QR Generation
def qr_gen(df_1, date, course_dir, key_dir):
    # [Generate]: QR code folder named qr_png
    output_dir = course_dir

    # [Configuration]: Public Key Path
    public_key = load_pubkey(key_dir)

    for index, row in df_1.iterrows():
        # [Configuration]: Initial QR Data
        qr_data = f"{row['Username']}|{date}"

        # [Configuration]: Encrypt QR Data
        encrypted_data = rsa.encrypt(qr_data.encode(), public_key)
        encoded_data = base64.urlsafe_b64encode(encrypted_data).decode()

        # [Configuration]: QR code parameters
        qr = qrcode.QRCode(
                version=6,
                box_size=10,
                border=4,
        )
        qr.add_data(encoded_data)
        qr.make(fit=True)
        print(encoded_data)
        # [Configuration]: QR File name/QR Color
        qr_path = os.path.join(output_dir, f"{row['Username']}.png")
        img = qr.make_image(fill="black", back_color="white")
        img.save(qr_path)

        # [Print]: QR Generation Progress
        print(f"QR code for {row['Username']} generated {index + 1}/{len(df_1)}")

# [Function]: Prompt user to continue
def prompt_user(message):
    while True:
        response = input(f"{message}? (y/n): ").strip().lower()
        if response == 'y':
            print("Proceeding...")
            return
        elif response == 'n':
            print("Operation cancelled.")
            exit()
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

# [Function]: Email skeleton
def send(smtp_server, smtp_port, sender_email, student_email, fpath, subject, body):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = student_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with open(fpath, 'rb') as img:
        img_1 = img.read()
        img_2 = MIMEImage(img_1, _subtype='png')
        img_2.add_header('Content-Disposition', 'attachment', filename=os.path.basename(fpath))
        message.attach(img_2)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.sendmail(sender_email, student_email, message.as_string())

# [Function]: Validate Date
def validate_date(date):
    date_regex = r"^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/\d{4}$"
    if re.match(date_regex, date):
        return True
    else:
        return False
# [Function]: Loading the new attendance file
def create_df(input):
        df = pd.read_csv(input)
        df = df[['StudentID', 'Email']].copy()
        df['Attendance'] = 'Absent'
        df.to_csv(ATTENDANCE_FILE, index=False)
        return df

# [Function]: Decrypt Encrypted QR Data
def decrypt_qr_data(encoded_data, key_dir):
    private_key = load_rsa_private_key(key_dir)

    encoded_data = encoded_data.strip()
    encrypted_data = base64.urlsafe_b64decode(encoded_data)
    decrypted_bytes = rsa.decrypt(encrypted_data, private_key)
    decrypted_message = decrypted_bytes.decode()
    return decrypted_message
