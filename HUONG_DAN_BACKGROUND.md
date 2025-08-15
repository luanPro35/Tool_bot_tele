# 🤖 HƯỚNG DẪN SỬ DỤNG BACKGROUND AUTO RESPONDER

## 📋 Mô tả

Background Auto Responder chạy ngầm trên máy tính, tự động trả lời tin nhắn Telegram khi bạn offline mà **KHÔNG CẦN MỞ TERMINAL**.

## ✨ Tính năng chính

- ✅ **Chạy ngầm**: Không cần terminal mở
- ✅ **Tự động khởi động**: Có thể tự động chạy khi khởi động máy
- ✅ **Trả lời offline**: Tự động gửi tin nhắn khi bạn không có mặt
- ✅ **Quản lý dễ dàng**: Menu điều khiển đơn giản
- ✅ **Log chi tiết**: Ghi lại mọi hoạt động

## 🚀 Cách sử dụng

### 1. Khởi động lần đầu

```bash
python background_responder.py
```

Hoặc double-click file: `start_background.bat`

### 2. Menu điều khiển

```
🤖 BACKGROUND AUTO RESPONDER
==================================================
1. 🚀 Khởi động Background Service
2. 🛑 Dừng Background Service
3. 📊 Xem trạng thái
4. 🔧 Bật/Tắt Auto Reply
5. ⚙️  Chỉnh sửa tin nhắn
6. 🚪 Thoát
==================================================
```

### 3. Workflow đơn giản

1. **Khởi động service**: Chọn (1) - Bot sẽ chạy ngầm
2. **Đóng terminal**: Có thể đóng terminal, bot vẫn hoạt động
3. **Kiểm tra trạng thái**: Mở lại và chọn (3) để xem
4. **Dừng khi cần**: Chọn (2) để dừng bot

## 🔧 Các chức năng

### 🚀 Khởi động Background Service (Chọn 1)

- Bot sẽ chạy ngầm trên máy tính
- Không cần giữ terminal mở
- Tự động trả lời tin nhắn 24/7

### 🛑 Dừng Background Service (Chọn 2)

- Dừng bot hoàn toàn
- Không trả lời tin nhắn nữa

### 📊 Xem trạng thái (Chọn 3)

```
📊 TRẠNG THÁI BACKGROUND RESPONDER
==================================================
🟢 Trạng thái: ĐANG CHẠY
⏰ Khởi động: 2025-08-15T22:52:00
📨 Tin nhắn đã trả lời: 15
🔧 Trạng thái: BẬT
==================================================
```

### 🔧 Bật/Tắt Auto Reply (Chọn 4)

- Tạm thời tắt/bật tính năng trả lời tự động
- Bot vẫn chạy nhưng không trả lời

### ⚙️ Chỉnh sửa tin nhắn (Chọn 5)

- Tùy chỉnh nội dung tin nhắn offline
- Thay đổi ngay lập tức

## 📁 Files được tạo

### `background_config.json`

```json
{
  "telegram_token": "YOUR_BOT_TOKEN",
  "check_interval": 15,
  "auto_offline_message": "🤖 Chào {name}!...",
  "enabled": true
}
```

### `background_state.json`

```json
{
  "last_update_id": 0,
  "start_time": "2025-08-15T22:52:00",
  "message_count": 15
}
```

### `responder.pid`

- File chứa Process ID của service đang chạy
- Dùng để kiểm tra và dừng service

### `background_responder.log`

- Log chi tiết mọi hoạt động
- Ghi lại tin nhắn đã trả lời, lỗi (nếu có)

## 💡 Ưu điểm so với Simple Responder

| Tính năng                 | Simple Responder | Background Responder |
| ------------------------- | ---------------- | -------------------- |
| Cần terminal mở           | ✅ Có            | ❌ Không             |
| Chạy ngầm                 | ❌ Không         | ✅ Có                |
| Tự động khởi động         | ❌ Không         | ✅ Có thể            |
| Quản lý service           | ❌ Không         | ✅ Có                |
| Trạng thái ONLINE/OFFLINE | ✅ Có            | ❌ Chỉ OFFLINE       |

## 🎯 Khi nào sử dụng Background Responder?

✅ **Nên dùng khi:**

- Muốn bot chạy 24/7 mà không cần mở terminal
- Cần trả lời tự động khi offline
- Muốn tiết kiệm tài nguyên máy tính
- Cần bot ổn định, không bị gián đoạn

❌ **Không nên dùng khi:**

- Cần chuyển đổi giữa ONLINE/OFFLINE thường xuyên
- Muốn tùy chỉnh tin nhắn theo từng trường hợp
- Cần tương tác trực tiếp với bot

## 📱 Tin nhắn mẫu

```
🤖 Chào [Tên]!

Cảm ơn bạn đã nhắn tin! Tôi hiện không có mặt và không thể trả lời ngay.

💬 Tin nhắn của bạn đã được ghi nhận, tôi sẽ phản hồi sớm nhất có thể.

🙏 Cảm ơn sự kiên nhẫn của bạn!
```

## 🔄 Tự động khởi động cùng Windows

### Cách 1: Thêm vào Startup folder

1. Nhấn `Win + R`, gõ: `shell:startup`
2. Copy file `start_background.bat` vào thư mục này
3. Bot sẽ tự động chạy khi khởi động Windows

### Cách 2: Tạo Task Scheduler

1. Mở Task Scheduler
2. Tạo Basic Task
3. Chọn "When the computer starts"
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `background_responder.py --daemon`
7. Start in: Thư mục chứa file

## 🛠️ Troubleshooting

### Service không khởi động được

```bash
# Kiểm tra Python
python --version

# Kiểm tra thư viện
pip install requests

# Chạy thủ công để xem lỗi
python background_responder.py --daemon
```

### Bot không trả lời

1. Kiểm tra trạng thái: Chọn (3)
2. Xem log file: `background_responder.log`
3. Kiểm tra kết nối internet
4. Kiểm tra token bot

### Không dừng được service

```bash
# Xóa file PID và thử lại
del responder.pid

# Hoặc dừng thủ công
taskkill /f /im python.exe
```

### File config bị lỗi

```bash
# Xóa config để tạo lại
del background_config.json
del background_state.json
```

## 🔒 Bảo mật

- Token bot được lưu trong file config local
- Không gửi dữ liệu lên server nào khác
- Chỉ sử dụng Telegram API chính thức
- Log file chỉ lưu trên máy tính của bạn

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra file log: `background_responder.log`
2. Xem trạng thái service: Chọn (3)
3. Thử khởi động lại service
4. Kiểm tra kết nối internet và token bot
