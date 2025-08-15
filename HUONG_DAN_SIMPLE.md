# 🤖 HƯỚNG DẪN SỬ DỤNG SIMPLE AUTO RESPONDER

## 📋 Mô tả

Auto Responder đơn giản cho Telegram với 2 trạng thái:

- **OFFLINE**: Gửi tin nhắn chào hỏi lịch sự và nói đợi
- **ONLINE**: Chào hỏi và nói sẽ trả lời trong 2-3 phút

## 🚀 Cách sử dụng

### 1. Chạy chương trình

```bash
python simple_auto_responder.py
```

### 2. Menu chính

```
🤖 SIMPLE AUTO RESPONDER
==================================================
1. 🚀 Khởi động Auto Responder
2. 🟢 Đặt trạng thái ONLINE
3. 🔴 Đặt trạng thái OFFLINE
4. 📊 Xem trạng thái hiện tại
5. ⚙️  Chỉnh sửa tin nhắn
6. 🚪 Thoát
==================================================
```

### 3. Các chức năng

#### 🚀 Khởi động Auto Responder (Chọn 1)

- Bắt đầu bot tự động trả lời tin nhắn
- Nhấn `Ctrl+C` để dừng

#### 🟢 Đặt trạng thái ONLINE (Chọn 2)

- Bot sẽ trả lời: "Chào [tên]! Tôi sẽ trả lời bạn trong vòng 2-3 phút"

#### 🔴 Đặt trạng thái OFFLINE (Chọn 3)

- Bot sẽ trả lời: "Chào [tên]! Tôi đang offline, vui lòng để lại tin nhắn"

#### 📊 Xem trạng thái hiện tại (Chọn 4)

- Hiển thị trạng thái ONLINE/OFFLINE

#### ⚙️ Chỉnh sửa tin nhắn (Chọn 5)

- Tùy chỉnh tin nhắn OFFLINE và ONLINE

## 📁 Files được tạo

### `simple_config.json`

```json
{
  "telegram_token": "YOUR_BOT_TOKEN",
  "check_interval": 10,
  "messages": {
    "offline": "🤖 Chào {name}!...",
    "online": "👋 Chào {name}!..."
  }
}
```

### `responder_state.json`

```json
{
  "is_online": false,
  "last_update_id": 0,
  "start_time": "2025-08-15T22:48:00"
}
```

### `simple_responder.log`

- File log ghi lại hoạt động của bot

## 🔧 Cấu hình

### Token Telegram Bot

- Token đã được cấu hình sẵn: `8216435475:AAHGgvKc9sFSiF1ejudtBpQx-B7mP8g3muw`
- Có thể thay đổi trong file `simple_config.json`

### Thời gian kiểm tra

- Mặc định: 10 giây
- Có thể thay đổi `check_interval` trong config

## 💡 Lưu ý

1. **Tự động tránh spam**: Bot không trả lời trùng lặp cho cùng 1 tin nhắn
2. **Tên người dùng**: Bot tự động lấy tên từ Telegram profile
3. **Trạng thái lưu trữ**: Trạng thái được lưu và khôi phục khi khởi động lại
4. **Log chi tiết**: Mọi hoạt động được ghi log

## 🎯 Workflow đơn giản

1. **Khởi động**: `python simple_auto_responder.py`
2. **Đặt trạng thái**: Chọn ONLINE (2) hoặc OFFLINE (3)
3. **Chạy bot**: Chọn "Khởi động Auto Responder" (1)
4. **Bot hoạt động**: Tự động trả lời tin nhắn theo trạng thái
5. **Dừng**: Nhấn `Ctrl+C`

## 📱 Tin nhắn mẫu

### Khi OFFLINE:

```
🤖 Chào [Tên]!

Cảm ơn bạn đã nhắn tin! Tôi hiện đang offline và không thể trả lời ngay.

💬 Vui lòng để lại tin nhắn, tôi sẽ phản hồi sớm nhất có thể khi online trở lại.

🙏 Cảm ơn sự kiên nhẫn của bạn!
```

### Khi ONLINE:

```
👋 Chào [Tên]!

Cảm ơn bạn đã nhắn tin! Tôi đã nhận được tin nhắn của bạn.

⏰ Tôi sẽ trả lời bạn trong vòng 2-3 phút.

😊 Cảm ơn bạn đã chờ đợi!
```

## 🛠️ Troubleshooting

### Lỗi kết nối

- Kiểm tra internet
- Kiểm tra token bot

### Bot không trả lời

- Kiểm tra trạng thái bot
- Xem log file để debug

### File config bị lỗi

- Xóa file `simple_config.json` để tạo lại config mặc định
