# --- config -----------------------------------------------------------
$BaseUrl = "http://44.3.2.14:8080"
$Date    = "2025-09-07"   # safer ISO format
$Course  = "CNIT345"

# --- 1) /data_qr ------------------------------------------------------
$qrBody = @{
  date      = $Date
  course    = $Course
} | ConvertTo-Json

$r1 = Invoke-RestMethod -Uri "$BaseUrl/data_qr" -Method Post `
        -ContentType "application/json" -Body $qrBody

# Print everything for inspection
$r1 | Format-List * -Force

# Always dump stdout/stderr to console and files
$r1.stdout  | Out-String -Width 4096 | Tee-Object -FilePath "out_qr.txt"
$r1.stderr  | Out-String -Width 4096 | Tee-Object -FilePath "err_qr.txt"
$r1.stdout_db | Out-String -Width 4096 | Tee-Object -FilePath "out_db.txt"
$r1.stderr_db | Out-String -Width 4096 | Tee-Object -FilePath "err_db.txt"
$r1.stdout_qr | Out-String -Width 4096 | Tee-Object -FilePath "out_qr_gen.txt"
$r1.stderr_qr | Out-String -Width 4096 | Tee-Object -FilePath "err_qr_gen.txt"

# --- 2) /mail ---------------------------------------------------------
$mailBody = @{
  date   = $Date
  course = $Course
} | ConvertTo-Json

$r2 = Invoke-RestMethod -Uri "$BaseUrl/mail" -Method Post `
        -ContentType "application/json" -Body $mailBody

$r2 | Format-List * -Force

$r2.stdout | Out-String -Width 4096 | Tee-Object -FilePath "out_mail.txt"
$r2.stderr | Out-String -Width 4096 | Tee-Object -FilePath "err_mail.txt"



