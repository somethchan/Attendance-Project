How the script works:

Prerequisites:
Client must upload a roster file RENAMED to Roster.csv to the NFS mount
i.e /NFS-share/<CNIT###>/Roster.csv

1. Client-side initiation

The client executes a script attnednace.py that prompts them for relevant variables i.e <email-body> <date> <course-name>. Each variable is stored to be passed to the attendance server through an HTTP-POST request. Saftey checks are performed throughout attendance.py to confirm the accuracy of user inputs. once the client is satisfied, the script will then send a HTTP-POST request to the production mail-server.

2. Using uvicorn to listen for incoming HTTP requests
The middleware code intercepts the http process and checks if the requestor IP is part of a permitted IP list in http_listener.py.
If the IP is among the list of permitted IPs, the middleware triggers sequentially executed code or blocking code. 

If the uvicorn service is not running on the mail server, ensure that it is available and listening with:
uvicorn app:app --host <mail_server_ip> --port <listen_port> --workers <num_connections>

The number of workers defined for --workers correlates to the number of concurrent sessions are available. 

Uvicorn listens on 3 different post ouptputs:
- http://<mail_server_ip>:<listen_port>/data_qr     # triggers `qr_gen.py` and checks for variables <date>, <course>. 
- http://<mail_server_ip>:<listen_port>/mail        # triggers `mail.py` and checks for variables <date>, <course>. 
- http://<mail_server_ip>:<listen_port>/scan        # triggers `scan.py` and checks for variables <enc_dat>

3. Server processes the request

Once the user passes the initial IP check, the server uses the variables passed in the HTTP POST request to execute requests. The server processes three main HTTP post requests listed below:

qr_gen.py:
    1. searches the NFS-share for the roster file
    2. performs an initial check to determine if folder for QR_codes have been generated
    3. loads the roster file into dataframe df_0
    4. parses data for <Username> column and stores in df_1
    5. encrypts data with a RSA key
    6. calls `qr_gen` function and passes <df_1>, <date>, <course_dir> to generate qr codes
    7. stores qr codes in `/var/lib/attendance/<course>/`

mail.py:
    1. searches the NFS-share for the roster file
    2. performs an initial check to determine if folder for QR_codes have been generated
    3. loads the roster file into dataframe df_0
    4. parses data for <Username>, <E-mail> column and stores in <df_1>
    5. calls `send` function and passes <SMTP_SERVER>, <SMTP_PORT>, <SENDER_EMAIL>, <STUDENT_EMAIL>, <subject>, <body> to maill all users in <df_1>

scan.py:
    1. decrypts data with key
    2. marks student that scanned in as present
    3. updates csv file in the NFS share to mark user as present
