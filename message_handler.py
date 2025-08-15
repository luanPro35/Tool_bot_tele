import re
import json
import logging
import requests
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(self, config, templates):
        self.config = config
        self.templates = templates
        self.platform_handlers = {
            "email": self.handle_email,
            "telegram": self.handle_telegram,
        }
        logger.info("MessageHandler đã được khởi tạo")

    def check_new_messages(self):
        new_messages = []
        for platform, platform_config in self.config.get("platforms", {}).items():
            if platform_config.get("enabled", False) and platform in self.platform_handlers:
                try:
                    platform_messages = self.platform_handlers[platform]()
                    if platform_messages:
                        new_messages.extend(platform_messages)
                except Exception as e:
                    logger.error(f"Lỗi khi kiểm tra tin nhắn từ {platform}: {str(e)}")
        return new_messages

    def create_response(self, message):
        content = message.get("content", "")
        platform = message.get("platform", "")
        sender = message.get("sender", "")
        if sender in self.config.get("excluded_senders", []):
            logger.info(f"Bỏ qua tin nhắn từ người gửi trong danh sách loại trừ: {sender}")
            return None
        for keyword, template_id in self.config.get("keyword_template_mapping", {}).items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE):
                logger.info(f"Đã tìm thấy từ khóa '{keyword}' trong tin nhắn")
                template = self.templates.get_template(template_id)
                return self._format_template(template, sender)
        default_template = self.templates.get_template("default")
        return self._format_template(default_template, sender)

    def _format_template(self, template, sender):
        if not template:
            return None
        subject = template.get("subject", "")
        body = template.get("body", "")
        replacements = {
            "{sender_name}": sender,
            "{current_time}": datetime.now().strftime("%H:%M:%S"),
            "{current_date}": datetime.now().strftime("%d/%m/%Y")
        }
        for placeholder, value in replacements.items():
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)
        return {
            "subject": subject,
            "body": body
        }

    def send_response(self, original_message, response):
        if not response:
            return False
        platform = original_message.get("platform", "")
        if platform in self.platform_handlers:
            try:
                send_method = getattr(self, f"send_{platform}", None)
                if send_method and callable(send_method):
                    send_method(original_message, response)
                    return True
                else:
                    logger.error(f"Không tìm thấy phương thức gửi cho nền tảng {platform}")
            except Exception as e:
                logger.error(f"Lỗi khi gửi phản hồi qua {platform}: {str(e)}")
        else:
            logger.error(f"Không hỗ trợ gửi phản hồi qua nền tảng {platform}")
        return False

    def handle_email(self):
        logger.info("Kiểm tra email mới")
        return []

    def handle_telegram(self):
        token = self.config.get("credentials.telegram.token")
        last_update_id = self.config.get("telegram.last_update_id", 0)
        if not token:
            logger.error("Không tìm thấy token của bot Telegram trong tệp cấu hình")
            return []
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        params = {
            "offset": last_update_id + 1,
            "timeout": 30,  
            "limit": 100
        }
        session = requests.Session()
        session.headers.update({'User-Agent': 'TelegramBot/1.0'})
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                logger.debug(f"Đang kiểm tra tin nhắn Telegram (lần thử {attempt + 1}/{max_retries})")
                response = session.get(
                    url, 
                    params=params,
                    timeout=(10, 35),  
                    stream=False
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("ok", False):
                    logger.error(f"Telegram API trả về lỗi: {data.get('description', 'Unknown error')}")
                    return []
                updates = data.get("result", [])
                messages = []
                for update in updates:
                    if "message" in update:
                        message = update["message"]
                        if "text" in message:
                            messages.append({
                                "platform": "telegram",
                                "chat_id": message["chat"]["id"],
                                "sender": message["from"].get("username", message["from"].get("first_name", "Unknown")),
                                "content": message.get("text", ""),
                                "timestamp": datetime.fromtimestamp(message["date"]).isoformat(),
                                "message_id": message["message_id"]
                            })
                    self.config.set("telegram.last_update_id", update["update_id"])
                if messages:
                    logger.info(f"Đã nhận được {len(messages)} tin nhắn Telegram mới")
                return messages
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout khi kết nối Telegram (lần thử {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Đã hết số lần thử kết nối Telegram")
                    return []
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Lỗi kết nối Telegram (lần thử {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Không thể kết nối đến Telegram API")
                    return []
            except requests.exceptions.RequestException as e:
                logger.error(f"Lỗi khi lấy tin nhắn Telegram: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return []
            except Exception as e:
                logger.error(f"Lỗi không mong muốn khi xử lý Telegram: {e}")
                return []
        return []

    def send_email(self, original_message, response):
        recipient = original_message.get("sender", "")
        subject = response.get("subject", "Phản hồi tự động")
        body = response.get("body", "")
        logger.info(f"Gửi email phản hồi đến {recipient} với tiêu đề '{subject}'")

    def send_telegram(self, original_message, response):
        token = self.config.get("credentials.telegram.token")
        if not token:
            logger.error("Không tìm thấy token của bot Telegram trong tệp cấu hình")
            return False
        chat_id = original_message.get("chat_id")
        body = response.get("body")
        if not chat_id or not body:
            logger.error("Thiếu chat_id hoặc nội dung để gửi tin nhắn Telegram")
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": body,
            "parse_mode": "HTML"  
        }
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                logger.debug(f"Đang gửi tin nhắn Telegram (lần thử {attempt + 1}/{max_retries})")
                response_obj = requests.post(
                    url, 
                    json=payload, 
                    timeout=(5, 10),  
                    headers={'User-Agent': 'TelegramBot/1.0'}
                )
                response_obj.raise_for_status()
                data = response_obj.json()
                if data.get("ok", False):
                    logger.info(f"Đã gửi tin nhắn Telegram thành công đến {chat_id}")
                    return True
                else:
                    logger.error(f"Telegram API trả về lỗi khi gửi tin nhắn: {data.get('description', 'Unknown error')}")
                    return False
            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout khi gửi tin nhắn Telegram (lần thử {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Đã hết số lần thử gửi tin nhắn Telegram")
                    return False
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Lỗi kết nối khi gửi tin nhắn Telegram (lần thử {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Không thể kết nối đến Telegram API để gửi tin nhắn")
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Lỗi khi gửi tin nhắn Telegram: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return False
            except Exception as e:
                logger.error(f"Lỗi không mong muốn khi gửi tin nhắn Telegram: {e}")
                return False
        return False
