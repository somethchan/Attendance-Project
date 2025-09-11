For future developers:

1. Upgrade protocol from HTTP to HTTPS
2. Move IP addresses to environment variables
3. Make authentication based checks on who can send to which classes
4. look into changing permissions for key storage from /etc/attendance/ since attendance user should not have access to edit /etc/ files
5. Clean up variable passing between functions
6. Take inventory of all checks and determine which checks are missing from script 

TODO LIST:
1. make a file checker for deployment on user side. Create a file in the NFS share for the course if it does not already exist
2. finish encryption for QR being generated
3. Make send portion from UI to http post, powershell/python
4. make NFS share
    a. make scan recieve portion
    b. make scan and send portion
5. make a way to check student scan progress

