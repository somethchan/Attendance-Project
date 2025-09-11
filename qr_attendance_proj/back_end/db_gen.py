# Takes <date>, <course>
import sys, os
import pandas as pd
import sqlite3
from pathlib import Path

# Length check for argv
if len(sys.argv) != 3:
    print("Usage: db_gen.py <date> <course>", file=sys.stderr)
    raise SystemExit(2)

# Read tokens passed in the initial script call
date, course = sys.argv[1:3]

print(">>> db_gen.py executed")

# ------------- FILE CONFIGS ---------------
nfs_dir = Path("/home/attendance/roster_files/spring_25")
file_path = os.path.join(nfs_dir, course, "roster.csv")

safe_date = date.replace("/", "-") 
db_dir = Path("/var/lib/attendance") / course
db_dir.mkdir(parents=True, exist_ok=True)
db_path = db_dir / f"{safe_date}.db"
# ------------------------------------------

# Read roster file into dataframe
try:
    df_0 = pd.read_csv(file_path)
except FileNotFoundError:
    print("Error: File Does not Exist.")
except Exception as e:
    print(f"An error occured: {e}")

# Filtering Columns & Cleaning
df_1 = df_0[['Username']].copy()
df_1['Username'] = df_1['Username'].str.lstrip('#').str.strip()
df_1['Attendance'] = 0

# Write to SQLite
conn = sqlite3.connect(db_path)
try:
    df_1.to_sql("roster", conn, if_exists="replace", index=False)
finally:
    conn.close()
