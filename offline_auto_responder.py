#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Auto Responder Bot - Tự động trả lời khi offline
"""

import json
import time
import logging
import requests
import urllib3
from datetime import datetime, timedelta
from response_templates import ResponseTemplates
from config import Config
import os
import threading
from typing import Dict, List, Optional

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_responder.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OfflineAutoResponder:
    """Auto Responder Bot với tính năng offline thông minh"""
    
    def __init__(self):
        self.config = Config()
        self.templates = ResponseTemplates()
        self.token = self.config.get("credentials.telegram.token")
        self.last_update_id = self.config.get("telegram.last_update_id", 0)
        self.session = requests.Session()
        
        # Trạng thái offline/online
        self.is_offline = True
        self.offline_start_time = datetime.now()
        self.last_activity_time = datetime.now()
        
        # Lưu trữ tin nhắn
        self.pending_messages = []
        self.responded_users = set()  # Tránh spam cùng một user
        
        # Cấu hình
        self.offline_timeout = 300  # 5 phút không hoạt động = offline
        self.max_responses_per_user = 3  # Tối đa 3 phản hồi tự động cho mỗi user
        self.user_response_count = {}
        
        # Cấu hình session
        self.session.headers.update({
            'User-Agent': 'OfflineAutoResponder/1.0',
            'Connection': 'keep-alive'
        })
        
        # Cấu hình adapter với retry
        adapter = requests.adapters.HTTPAdapter(
            max_retries=urllib3.util.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('https://', adapter)
        
        # Load trạng thái từ file
        self.load_state()
        
        logger.info("OfflineAutoResponder đã được khởi tạo")
    
    def load_state(self):
        """Load trạng thái từ file"""
        try:
            if os.path.exists("auto_responder_state.json"):
                with open("auto_responder_state.json", "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.is_offline = state.get("is_offline", True)
                    self.user_response_count = state.get("user_response_count", {})
                    self.pending_messages = state.get("pending_messages", [])
                    
                    # Parse datetime
                    if state.get("offline_start_time"):
                        self.offline_start_time = datetime.fromisoformat(state["offline_start_time"])
                    if state.get("last_activity_time"):
                        self.last_activity_time = datetime.fromisoformat(state["last_activity_time"])
                        
                logger.info("Đã load trạng thái từ file")
        except Exception as e:
            logger.error(f"Lỗi khi load trạng thái: {e}")
    
    def save_state(self):
        """Lưu trạng thái vào file"""
        try:
            state = {
                "is_offline": self.is_offline,
                "offline_start_time": self.offline_start_time.isoformat(),
                "last_activity_time": self.last_activity_time.isoformat(),
                "user_response_count": self.user_response_count,
                "pending_messages": self.pending_messages
            }
            with open("auto_responder_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Lỗi khi lưu trạng thái: {e}")
    
    def check_offline_status(self):
        """Kiểm tra trạng thái offline dựa trên thời gian không hoạt động"""
        now = datetime.now()
        time_since_activity = (now - self.last_activity_time).total_seconds()
        
        if time_since_activity > self.offline_timeout and not self.is_offline:
            self.is_offline = True
            self.offline_start_time = now
            logger.info("Chuyển sang trạng thái OFFLINE")
            self.save_state()
    
    def set_online(self):
        """Đặt trạng thái online (có thể gọi từ bên ngoài)"""
        if self.is_offline:
            self.is_offline = False
            self.last_activity_time = datetime.now()
            logger.info("Chuyển sang trạng thái ONLINE")
            
            # Reset counter cho ngày mới
            self.reset_daily_counters()
            self.save_state()
    
    def set_offline(self):
        """Đặt trạng thái offline thủ công"""
        if not self.is_offline:
            self.is_offline = True
            self.offline_start_time = datetime.now()
            logger.info("Chuyển sang trạng thái OFFLINE (thủ công)")
            self.save_state()
    
    def reset_daily_counters(self):
        """Reset counter hàng ngày"""
        self.user_response_count = {}
        self.responded_users = set()
    
    def get_updates_simple(self):
        """Lấy updates từ Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "limit": 10,
                "timeout": 0
            }
            
            response = self.session.get(
                url, 
                params=params, 
                timeout=15,
                verify=False
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                logger.error(f"Telegram API error: {data.get('description')}")
                return []
            
            updates = data.get('result', [])
            messages = []
            
            for update in updates:
                self.last_update_id = update['update_id']
                self.config.set("telegram.last_update_id", self.last_update_id)
                
                if 'message' in update and 'text' in update['message']:
                    message = update['message']
                    messages.append({
                        "platform": "telegram",
                        "chat_id": message["chat"]["id"],
                        "user_id": message["from"]["id"],
                        "sender": message["from"].get("username", message["from"].get("first_name", "Unknown")),
                        "content": message.get("text", ""),
                        "timestamp": datetime.fromtimestamp(message["date"]).isoformat(),
                        "message_id": message["message_id"]
                    })
            
            return messages
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy updates: {e}")
            return []
    
    def send_message(self, chat_id, text):
        """Gửi tin nhắn"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            response = self.session.post(
                url, 
                json=data, 
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Đã gửi auto-response đến {chat_id}")
                return True
            else:
                logger.error(f"Lỗi khi gửi tin nhắn: {result.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {e}")
            return False
    
    def should_auto_respond(self, user_id: int) -> bool:
        """Kiểm tra có nên tự động phản hồi không"""
        if not self.is_offline:
            return False
        
        # Kiểm tra số lần đã phản hồi cho user này
        count = self.user_response_count.get(str(user_id), 0)
        if count >= self.max_responses_per_user:
            return False
        
        return True
    
    def create_smart_response(self, message: Dict) -> Optional[str]:
        """Tạo phản hồi thông minh dựa trên nội dung tin nhắn"""
        content = message.get("content", "").lower()
        sender = message.get("sender", "Unknown")
        user_id = message.get("user_id")
        
        # Tính thời gian offline
        offline_duration = datetime.now() - self.offline_start_time
        offline_hours = int(offline_duration.total_seconds() / 3600)
        offline_minutes = int((offline_duration.total_seconds() % 3600) / 60)
        
        # Phân loại tin nhắn và chọn template phù hợp
        if any(word in content for word in ["urgent", "khẩn cấp", "gấp", "emergency"]):
            template_id = "urgent_response"
        elif any(word in content for word in ["price", "giá", "cost", "bao nhiêu"]):
            template_id = "price_inquiry"
        elif any(word in content for word in ["hello", "hi", "chào", "xin chào"]):
            template_id = "welcome_offline"
        elif any(word in content for word in ["buy", "mua", "order", "đặt hàng"]):
            template_id = "sales_offline"
        elif any(word in content for word in ["help", "support", "hỗ trợ", "giúp"]):
            template_id = "support_offline"
        else:
            template_id = "default_offline"
        
        # Lấy template, fallback về default nếu không tìm thấy
        template = self.templates.get_template(template_id)
        if not template:
            template = self.templates.get_template("default_offline")
        if not template:
            template = {"body": "Cảm ơn bạn đã nhắn tin! Tôi hiện đang offline và sẽ trả lời sớm nhất có thể."}
        
        # Thay thế placeholder
        body = template.get("body", "")
        body = body.replace("{sender_name}", sender)
        body = body.replace("{offline_hours}", str(offline_hours))
        body = body.replace("{offline_minutes}", str(offline_minutes))
        body = body.replace("{current_time}", datetime.now().strftime("%H:%M"))
        body = body.replace("{current_date}", datetime.now().strftime("%d/%m/%Y"))
        
        # Thêm thông tin về thời gian offline nếu > 1 giờ
        if offline_hours > 0:
            body += f"\n\n⏰ Tôi đã offline được {offline_hours} giờ {offline_minutes} phút."
        
        return body
    
    def save_pending_message(self, message: Dict):
        """Lưu tin nhắn để xem lại khi online"""
        self.pending_messages.append({
            **message,
            "received_at": datetime.now().isoformat(),
            "auto_responded": True
        })
        
        # Giới hạn số tin nhắn lưu trữ
        if len(self.pending_messages) > 100:
            self.pending_messages = self.pending_messages[-100:]
        
        self.save_state()
    
    def process_message(self, message: Dict):
        """Xử lý tin nhắn"""
        user_id = message.get("user_id")
        chat_id = message.get("chat_id")
        
        # Lưu tin nhắn để xem lại sau
        self.save_pending_message(message)
        
        # Kiểm tra có nên auto-respond không
        if self.should_auto_respond(user_id):
            response_text = self.create_smart_response(message)
            if response_text and self.send_message(chat_id, response_text):
                # Cập nhật counter
                count = self.user_response_count.get(str(user_id), 0)
                self.user_response_count[str(user_id)] = count + 1
                self.save_state()
                
                logger.info(f"Đã auto-respond cho user {user_id} (lần {count + 1})")
    
    def get_pending_messages_summary(self) -> str:
        """Lấy tóm tắt tin nhắn chờ xử lý"""
        if not self.pending_messages:
            return "Không có tin nhắn nào trong thời gian offline."
        
        summary = f"📨 Có {len(self.pending_messages)} tin nhắn trong thời gian offline:\n\n"
        
        for i, msg in enumerate(self.pending_messages[-10:], 1):  # Chỉ hiển thị 10 tin nhắn gần nhất
            timestamp = datetime.fromisoformat(msg["received_at"]).strftime("%d/%m %H:%M")
            summary += f"{i}. {msg['sender']}: {msg['content'][:50]}{'...' if len(msg['content']) > 50 else ''} ({timestamp})\n"
        
        if len(self.pending_messages) > 10:
            summary += f"\n... và {len(self.pending_messages) - 10} tin nhắn khác."
        
        return summary
    
    def clear_pending_messages(self):
        """Xóa tin nhắn chờ xử lý"""
        self.pending_messages = []
        self.save_state()
        logger.info("Đã xóa tất cả tin nhắn chờ xử lý")
    
    def run(self):
        """Chạy auto responder"""
        logger.info("Bắt đầu chạy Offline Auto Responder...")
        logger.info(f"Trạng thái hiện tại: {'OFFLINE' if self.is_offline else 'ONLINE'}")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while True:
                try:
                    # Kiểm tra trạng thái offline
                    self.check_offline_status()
                    
                    # Lấy tin nhắn mới
                    messages = self.get_updates_simple()
                    
                    # Reset error counter nếu thành công
                    consecutive_errors = 0
                    
                    # Xử lý từng tin nhắn
                    for message in messages:
                        try:
                            self.process_message(message)
                        except Exception as e:
                            logger.error(f"Lỗi khi xử lý tin nhắn: {e}")
                    
                    # Nghỉ một chút
                    time.sleep(3)
                    
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Lỗi trong vòng lặp chính (lần {consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error("Quá nhiều lỗi liên tiếp, dừng bot")
                        break
                    
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            logger.info("Auto Responder đã bị dừng bởi người dùng")
        except Exception as e:
            logger.error(f"Lỗi nghiêm trọng: {e}")
        finally:
            self.save_state()
            logger.info("Auto Responder đã dừng")

def main():
    """Hàm chính"""
    responder = OfflineAutoResponder()
    responder.run()

if __name__ == "__main__":
    main()
