# Takes <date>, <course>

# /opt/jobs/mail.py
import sys, os, smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from functions import send

#from functions import qr_gen
print(">>> massmail.py executed")

# Length check for argv
if len(sys.argv) != 3:
    print("Usage: qr_gen.py <date> <course>", file=sys.stderr)
    raise SystemExit(2)

# Read tokens passed in the initial script call
date, course = sys.argv[1:3]

# ------------- FILE CONFIGS --------------- 
nfs_dir = Path("/home/attendance/roster_files/spring_25")
file_path = os.path.join(nfs_dir, course, "roster.csv")
# ------------------------------------------ 

# Read roster file into dataframe
try:
    df_0 = pd.read_csv(file_path)
except FileNotFoundError:
    print("Error: File Does not Exist.")
except Exception as e:
    print(f"An error occured: {e}")

# Filtering Columns & Cleaning
df_1 = df_0[['Username', 'Email']]
df_1.columns = ['Username', 'Email'] #Enforce column headers
df_1.loc[:,'Username'] = df_1['Username'].str.lstrip('#').str.strip()
df_1.loc[:,'Email'] = df_1['Email'].str.rstrip('#').str.strip()

# ------------- MAIL CONFIGS --------------- 
SMTP_SERVER ='SMTP SERVER HERE.'
SMTP_PORT = 25
SENDER_EMAIL = 'attendance.noreply@cit.lcl'
QR_DIR = Path("/var/lib/attendance") / course
# ------------------------------------------ 

for index, row in df_1.iterrows():
    STUDENT_EMAIL = row['Email']
    path = os.path.join(QR_DIR, f"{row['Username']}.png")

    # [Call]: Send email to each user
    send(
        SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, STUDENT_EMAIL,

        # [Configuration]: E-mail subject/body
        subject=f"{course} Attendance QR code",
        body = (
            f"Dear {row['Username']},\n\n"
            "Please find your unique QR code below to mark your attendance.\n"
            f"Date: {date}\n"
            f"Course: {course}\n\n"
            "Please scan the attached QR code during lecture to receive attendance credit.\n"
        )
    )
    print(f"QR code for {row['Username']} sent {index + 1}/{len(df_1)}")
