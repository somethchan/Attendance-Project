import pandas as pd
import os

from functions import prompt_user
from functions import create_df
from functions import load_rsa_private_key
from functions import decrypt_qr_data

RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[0m'

# [User Input]: file_path
file_path = input("Enter File Path for Roster (.csv format): ").strip()

# [Input Validation]: file_path
if not os.path.isfile(file_path):
    print("Error: File does not exist.")
    exit()
if not file_path.endswith('.csv'):
    print("Error: File is not a .csv file.")
    exit()

# [Error Handling]
try:
    df_0 = pd.read_csv(file_path)
    prompt_user(f"{file_path} is the correct file path")
except FileNotFoundError:
    print("Error: File Does not Exist.")
except Exception as e:
    print(f"An error occured: {e}")

# [Dataframe Manipulation]: Filtering Columns & Cleaning
df_1 = df_0[['Username', 'Email']]
df_1.columns = ['Username', 'Email'] #Enforce column headers
df_1.loc[:,'Username'] = df_1['Username'].str.lstrip('#').str.strip()
df_1.loc[:,'Email'] = df_1['Email'].str.rstrip('#').str.strip()
df_1['Attendance'] = 'Absent'

# [Main Loop]: Scan users for input data
while True:
    scan_input = input("Scan student QR: ").strip()

    # [Break]: Exit parameter to break loop is finish
    if scan_input.lower() == 'finish':
        print("Attendance complete, generating CSV file...\n")
        break
    try:
        # [Error Handling]: Scan and check for valid encrypted input
        decrypted_message = decrypt_qr_data(scan_input, key_dir)
    except Exception as e:
        print(f"An error occured: {e}")

    try:
        # [Error Handling]: Checking if parsed value format matches
        username, email, date = [item.strip() for item in decrypted_message.strip().split('|')]
    except ValueError:
        print("Invalid QR format")

    # [Validate Attendance]:
    match = df_1['Username'] == username
    if match.any():
        df_1['Attendance'] = 'Present'
        df_1['Date'] = date
        print(f"{GREEN}{username} has been marked PRESENT{RESET}")
        print(df_1)
    else:
        print(f"{RED}{username} was not found {RESET}")
