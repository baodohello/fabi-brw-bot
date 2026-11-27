@echo off
chcp 65001 >nul
cd /d "C:\Users\ADMIN\Documents\fabi-brw-bot"

:: Chạy bằng python.exe để hiện terminal và xem log trực tiếp
".\venv\Scripts\python.exe" -m tasks.fabi_export_4_report

pause