# Takes <date>, <course>

# /opt/jobs/qr_gen.py
import sys, os 
import pandas as pd
from functions import qr_gen
from functions import key_gen
from pathlib import Path
print(">>> qr_gen.py executed")

# Length check for argv
if len(sys.argv) != 3:
    print("Usage: qr_gen.py <date> <course>", file=sys.stderr)
    raise SystemExit(2)

# Read tokens passed in the initial script call
date, course = sys.argv[1:3]

# ------------- FILE CONFIGS --------------- 
nfs_dir = "/home/attendance/roster_files/spring_25"
file_path = os.path.join(nfs_dir, course, "roster.csv")

# Make folder to store QR codes
course_dir = f"/var/lib/attendance/{course}"
if not os.path.isdir(course_dir):
    os.makedirs(course_dir, exist_ok=True)
# Make folder to store public key
key_dir = f"/etc/attendance/keys/{course}"
if not os.path.isdir(key_dir):
    os.makedirs(key_dir, exist_ok=True)
key_gen(course)
# ------------------------------------------ 

# Read roster file into dataframe
try:
    df_0 = pd.read_csv(file_path)
except FileNotFoundError:
    print("Error: File Does not Exist.")
    sys.exit(1)
except Exception as e:
    print(f"An error occured: {e}")
    sys.exit(1)

# Filtering Columns & Cleaning
df_1 = df_0[['Username']].copy()
df_1['Username'] = df_1['Username'].str.lstrip('#').str.strip()

print(df_1)

# [Call]: QR generation function
qr_gen(df_1,date,course_dir, key_dir)