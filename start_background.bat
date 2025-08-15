@echo off
chcp 65001 >nul
title Background Auto Responder
color 0B

echo.
echo ========================================
echo    🤖 BACKGROUND AUTO RESPONDER
echo ========================================
echo.
echo Khởi động Background Service...
echo.

python background_responder.py

echo.
echo Nhấn phím bất kỳ để thoát...
pause >nul
