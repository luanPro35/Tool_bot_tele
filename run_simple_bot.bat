@echo off
chcp 65001 >nul
title Simple Auto Responder
color 0A

echo.
echo ========================================
echo    🤖 SIMPLE AUTO RESPONDER
echo ========================================
echo.
echo Đang khởi động...
echo.

python simple_auto_responder.py

echo.
echo Bot đã dừng. Nhấn phím bất kỳ để thoát...
pause >nul
