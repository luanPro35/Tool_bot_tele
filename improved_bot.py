#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bot Telegram cải tiến với xử lý lỗi kết nối tốt hơn
"""

import json
import time
import logging
import requests
import urllib3
from datetime import datetime
from response_templates import ResponseTemplates
from config import Config

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("improved_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImprovedTelegramBot:
    """Bot Telegram cải tiến với xử lý lỗi tốt hơn"""
    
    def __init__(self):
        self.config = Config()
        self.templates = ResponseTemplates()
        self.token = self.config.get("credentials.telegram.token")
        self.last_update_id = self.config.get("telegram.last_update_id", 0)
        self.session = requests.Session()
        
        # Cấu hình session
        self.session.headers.update({
            'User-Agent': 'TelegramBot/2.0',
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
        
        logger.info("ImprovedTelegramBot đã được khởi tạo")
    
    def get_bot_info(self):
        """Lấy thông tin bot"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok'):
                return data.get('result')
            return None
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin bot: {e}")
            return None
    
    def get_updates_simple(self):
        """Lấy updates với phương pháp đơn giản hơn"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "limit": 10,
                "timeout": 0  # Không dùng long polling
            }
            
            logger.debug(f"Đang lấy updates từ offset {self.last_update_id + 1}")
            
            response = self.session.get(
                url, 
                params=params, 
                timeout=15,
                verify=False  # Tạm thời bỏ qua SSL verification
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('ok'):
                logger.error(f"Telegram API error: {data.get('description')}")
                return []
            
            updates = data.get('result', [])
            messages = []
            
            for update in updates:
                # Cập nhật last_update_id
                self.last_update_id = update['update_id']
                self.config.set("telegram.last_update_id", self.last_update_id)
                
                if 'message' in update and 'text' in update['message']:
                    message = update['message']
                    messages.append({
                        "platform": "telegram",
                        "chat_id": message["chat"]["id"],
                        "sender": message["from"].get("username", message["from"].get("first_name", "Unknown")),
                        "content": message.get("text", ""),
                        "timestamp": datetime.fromtimestamp(message["date"]).isoformat(),
                        "message_id": message["message_id"]
                    })
            
            if messages:
                logger.info(f"Nhận được {len(messages)} tin nhắn mới")
            
            return messages
            
        except requests.exceptions.Timeout:
            logger.warning("Timeout khi lấy updates - sẽ thử lại")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Lỗi kết nối: {e} - sẽ thử lại")
            return []
        except Exception as e:
            logger.error(f"Lỗi không mong muốn: {e}")
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
                logger.info(f"Đã gửi tin nhắn thành công đến {chat_id}")
                return True
            else:
                logger.error(f"Lỗi khi gửi tin nhắn: {result.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {e}")
            return False
    
    def create_response(self, message):
        """Tạo phản hồi cho tin nhắn"""
        content = message.get("content", "").lower()
        sender = message.get("sender", "Unknown")
        
        # Kiểm tra từ khóa
        keyword_mapping = self.config.get("keyword_template_mapping", {})
        
        for keyword, template_id in keyword_mapping.items():
            if keyword.lower() in content:
                template = self.templates.get_template(template_id)
                if template:
                    body = template.get("body", "")
                    # Thay thế placeholder
                    body = body.replace("{sender_name}", sender)
                    body = body.replace("{current_time}", datetime.now().strftime("%H:%M:%S"))
                    body = body.replace("{current_date}", datetime.now().strftime("%d/%m/%Y"))
                    return body
        
        # Phản hồi mặc định
        default_template = self.templates.get_template("default")
        if default_template:
            body = default_template.get("body", "Xin chào! Cảm ơn bạn đã liên hệ.")
            body = body.replace("{sender_name}", sender)
            return body
        
        return "Xin chào! Cảm ơn bạn đã liên hệ."
    
    def run(self):
        """Chạy bot"""
        logger.info("Bắt đầu chạy bot...")
        
        # Kiểm tra kết nối
        bot_info = self.get_bot_info()
        if bot_info:
            logger.info(f"Bot đã kết nối: @{bot_info.get('username')}")
        else:
            logger.error("Không thể kết nối đến bot")
            return
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        try:
            while True:
                try:
                    # Lấy tin nhắn mới
                    messages = self.get_updates_simple()
                    
                    # Reset error counter nếu thành công
                    consecutive_errors = 0
                    
                    # Xử lý từng tin nhắn
                    for message in messages:
                        try:
                            response_text = self.create_response(message)
                            if response_text:
                                self.send_message(message['chat_id'], response_text)
                        except Exception as e:
                            logger.error(f"Lỗi khi xử lý tin nhắn: {e}")
                    
                    # Nghỉ một chút trước khi kiểm tra lại
                    time.sleep(2)
                    
                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"Lỗi trong vòng lặp chính (lần {consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error("Quá nhiều lỗi liên tiếp, dừng bot")
                        break
                    
                    # Nghỉ lâu hơn khi có lỗi
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            logger.info("Bot đã bị dừng bởi người dùng")
        except Exception as e:
            logger.error(f"Lỗi nghiêm trọng: {e}")
        finally:
            logger.info("Bot đã dừng")

def main():
    """Hàm chính"""
    bot = ImprovedTelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
