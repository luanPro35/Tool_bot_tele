# 🤖 Hướng Dẫn Sử Dụng Bot Auto Responder

## 📋 Tổng Quan

Bot Auto Responder là một hệ thống thông minh giúp bạn tự động trả lời tin nhắn Telegram khi bạn offline. Bot sẽ:

- ✅ Tự động phát hiện khi bạn offline (sau 5 phút không hoạt động)
- 🤖 Tự động trả lời tin nhắn với các template thông minh
- 📝 Lưu trữ tất cả tin nhắn để bạn xem lại khi online
- 🚫 Tránh spam bằng cách giới hạn số lần phản hồi cho mỗi user
- 🎯 Phân loại tin nhắn và trả lời phù hợp (khẩn cấp, hỏi giá, đặt hàng...)

## 🚀 Cách Sử Dụng

### 1. Khởi Động Bot (Chế độ tương tác)

```bash
python bot_controller.py
```

Sau đó chọn các tùy chọn từ menu:

- `1` - Khởi động Auto Responder
- `2` - Dừng Auto Responder
- `3` - Đặt trạng thái ONLINE
- `4` - Đặt trạng thái OFFLINE
- `5` - Xem trạng thái hiện tại
- `6` - Xem tin nhắn chờ xử lý
- `7` - Xóa tin nhắn chờ xử lý
- `8` - Thoát

### 2. Khởi Động Bot (Dòng lệnh)

```bash
# Khởi động và để bot tự động phát hiện offline
python bot_controller.py start

# Khởi động và đặt ngay trạng thái offline
python bot_controller.py offline

# Khởi động và đặt ngay trạng thái online
python bot_controller.py online

# Xem trạng thái hiện tại
python bot_controller.py status
```

### 3. Chạy Trực Tiếp Auto Responder

```bash
python offline_auto_responder.py
```

## 🎯 Các Tính Năng Thông Minh

### 1. Phân Loại Tin Nhắn Tự Động

Bot sẽ tự động nhận diện loại tin nhắn và trả lời phù hợp:

- **Tin nhắn khẩn cấp**: Chứa từ "urgent", "khẩn cấp", "gấp", "emergency"
- **Hỏi giá**: Chứa từ "price", "giá", "cost", "bao nhiêu"
- **Chào hỏi**: Chứa từ "hello", "hi", "chào", "xin chào"
- **Đặt hàng**: Chứa từ "buy", "mua", "order", "đặt hàng"
- **Hỗ trợ**: Chứa từ "help", "support", "hỗ trợ", "giúp"

### 2. Giới Hạn Spam

- Mỗi user chỉ nhận tối đa **3 phản hồi tự động**
- Tránh làm phiền user với quá nhiều tin nhắn tự động

### 3. Lưu Trữ Tin Nhắn

- Tất cả tin nhắn nhận được khi offline đều được lưu trữ
- Bạn có thể xem lại khi online
- Giới hạn lưu trữ 100 tin nhắn gần nhất

## ⚙️ Cấu Hình

### 1. Thay Đổi Thời Gian Offline

Mở file `offline_auto_responder.py` và sửa:

```python
self.offline_timeout = 300  # 300 giây = 5 phút
```

### 2. Thay Đổi Số Lần Phản Hồi Tối Đa

```python
self.max_responses_per_user = 3  # Tối đa 3 lần
```

### 3. Tùy Chỉnh Template Phản Hồi

Chỉnh sửa file `templates.json` để thay đổi nội dung phản hồi:

```json
{
  "default_offline": {
    "subject": "Phản hồi tự động - Đang offline",
    "body": "🤖 Xin chào {sender_name}!\n\nTôi hiện đang offline..."
  }
}
```

**Các placeholder có sẵn:**

- `{sender_name}` - Tên người gửi
- `{current_time}` - Thời gian hiện tại
- `{current_date}` - Ngày hiện tại
- `{offline_hours}` - Số giờ đã offline
- `{offline_minutes}` - Số phút đã offline

## 📊 Theo Dõi Hoạt Động

### 1. Xem Log

```bash
# Xem log auto responder
tail -f auto_responder.log

# Xem log bot chính
tail -f improved_bot.log
```

### 2. Kiểm Tra Trạng Thái

File `auto_responder_state.json` lưu trữ:

- Trạng thái online/offline
- Thời gian bắt đầu offline
- Số lần đã phản hồi cho mỗi user
- Tin nhắn chờ xử lý

## 🔧 Xử Lý Sự Cố

### 1. Bot Không Tự Động Trả Lời

- Kiểm tra bot có đang chạy không: `python bot_controller.py status`
- Kiểm tra trạng thái: Phải ở chế độ OFFLINE
- Kiểm tra log: `tail -f auto_responder.log`

### 2. Bot Trả Lời Quá Nhiều

- Kiểm tra cấu hình `max_responses_per_user`
- Reset counter: Xóa file `auto_responder_state.json`

### 3. Tin Nhắn Không Được Lưu

- Kiểm tra quyền ghi file
- Kiểm tra dung lượng ổ cứng

## 📱 Ví Dụ Sử Dụng

### Kịch Bản 1: Đi Ngủ

```bash
# Trước khi đi ngủ
python bot_controller.py offline
```

### Kịch Bản 2: Đi Làm

```bash
# Sáng thức dậy
python bot_controller.py online

# Xem tin nhắn đã nhận
python bot_controller.py
# Chọn option 6 để xem tin nhắn
```

### Kịch Bản 3: Đi Du Lịch

```bash
# Khởi động bot và để tự động
python bot_controller.py start
# Bot sẽ tự động chuyển offline sau 5 phút không hoạt động
```

## 🎨 Tùy Chỉnh Nâng Cao

### 1. Thêm Template Mới

Thêm vào `templates.json`:

```json
"custom_template": {
    "subject": "Template tùy chỉnh",
    "body": "Nội dung tùy chỉnh với {sender_name}"
}
```

### 2. Thêm Từ Khóa Mới

Sửa trong `offline_auto_responder.py`, hàm `create_smart_response()`:

```python
elif any(word in content for word in ["từ_khóa_mới"]):
    template_id = "custom_template"
```

## 🔒 Bảo Mật

- Token bot được lưu trong `config.json` - không chia sẻ file này
- Log file có thể chứa thông tin nhạy cảm - bảo vệ quyền truy cập
- Chỉ chạy bot trên máy tính tin cậy

## 🚀 Khởi Động Nhanh

### Bước 1: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Cấu Hình Token

Sửa file `config.json`, thay `YOUR_BOT_TOKEN` bằng token thật:

```json
{
  "credentials": {
    "telegram": {
      "token": "YOUR_BOT_TOKEN"
    }
  }
}
```

### Bước 3: Chạy Bot

```bash
# Cách 1: Chế độ tương tác (khuyến nghị cho người mới)
python bot_controller.py

# Cách 2: Chạy ngay ở chế độ offline
python bot_controller.py offline

# Cách 3: Chạy và để tự động phát hiện
python bot_controller.py start
```

## 📞 Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề, hãy kiểm tra:

1. Log file: `auto_responder.log`
2. Trạng thái: `python bot_controller.py status`
3. Cấu hình: `config.json` và `templates.json`

**Chúc bạn sử dụng bot thành công! 🎉**
