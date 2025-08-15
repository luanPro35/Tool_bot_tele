@echo off
echo ========================================
echo    🤖 BOT AUTO RESPONDER LAUNCHER
echo ========================================
echo.
echo Chọn chế độ khởi động:
echo.
echo 1. Chế độ tương tác (Menu)
echo 2. Khởi động và đặt OFFLINE ngay
echo 3. Khởi động và đặt ONLINE ngay  
echo 4. Khởi động tự động (phát hiện offline sau 5 phút)
echo 5. Xem trạng thái hiện tại
echo 6. Thoát
echo.
set /p choice="👉 Nhập lựa chọn (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Khởi động chế độ tương tác...
    python bot_controller.py
) else if "%choice%"=="2" (
    echo.
    echo 🤖 Khởi động ở chế độ OFFLINE...
    python bot_controller.py offline
) else if "%choice%"=="3" (
    echo.
    echo 💬 Khởi động ở chế độ ONLINE...
    python bot_controller.py online
) else if "%choice%"=="4" (
    echo.
    echo ⚡ Khởi động tự động...
    echo Bot sẽ tự động chuyển offline sau 5 phút không hoạt động
    python bot_controller.py start
) else if "%choice%"=="5" (
    echo.
    echo 📊 Kiểm tra trạng thái...
    python bot_controller.py status
    pause
) else if "%choice%"=="6" (
    echo.
    echo 👋 Tạm biệt!
    exit
) else (
    echo.
    echo ❌ Lựa chọn không hợp lệ!
    pause
)

echo.
pause
