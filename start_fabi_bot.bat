@echo off
:: Di chuyển vào đúng thư mục dự án trên ổ C của anh
cd /d "C:\Users\ADMIN\Documents\fabi-brw-bot"

:: Kích hoạt venv và chạy ẩn bằng pythonw
start /b "" ".\venv\Scripts\pythonw.exe" main.py