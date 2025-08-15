import os
import json
import time
import logging
import threading
import subprocess
from datetime import datetime
from message_handler import MessageHandler
from response_templates import ResponseTemplates
from config import Config

file_handler = logging.FileHandler("auto_responder.log", encoding="utf-8")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        stream_handler
    ]
)

logger = logging.getLogger(__name__)


class AutoResponder:
    def __init__(self, config_file="config.json"):
        self.config = Config(config_file)
        self.templates = ResponseTemplates()
        self.message_handler = MessageHandler(self.config, self.templates)
        self.last_check_time = datetime.now()
        logger.info("AutoResponder đã được khởi tạo")

    def start_web_server(self):
        try:
            logger.info("Bắt đầu máy chủ web...")
            subprocess.Popen(["python", "web_server.py"])
        except Exception as e:
            logger.error(f"Lỗi khi bắt đầu máy chủ web: {e}")

    def start(self):
        web_server_thread = threading.Thread(target=self.start_web_server)
        web_server_thread.daemon = True
        web_server_thread.start()
        logger.info("Bắt đầu dịch vụ tự động trả lời tin nhắn")
        try:
            while True:
                new_messages = self.message_handler.check_new_messages()
                
                if new_messages:
                    logger.info(f"Đã nhận được {len(new_messages)} tin nhắn mới")
                    for message in new_messages:
                        self.process_message(message)
                
                self.last_check_time = datetime.now()
                
                telegram_enabled = self.config.get("platforms.telegram.enabled", False)
                if telegram_enabled:
                    check_interval = self.config.get("platforms.telegram.check_interval", 30)
                else:
                    check_interval = self.config.get("app.check_interval", 300)
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("Dịch vụ đã bị dừng bởi người dùng")
        except Exception as e:
            logger.error(f"Lỗi không mong muốn: {str(e)}")
        finally:
            logger.info("Dịch vụ tự động trả lời tin nhắn đã dừng")

    def process_message(self, message):
        try:
            if self.is_new_message(message):
                response = self.message_handler.create_response(message)
                
                if response:
                    self.message_handler.send_response(message, response)
                    logger.info(f"Đã gửi phản hồi tự động cho tin nhắn từ {message.get('sender', 'Unknown')}")
        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")

    def is_new_message(self, message):
        message_time = datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat()))
        return message_time > self.last_check_time


def main():
    auto_responder = AutoResponder()
    auto_responder.start()


if __name__ == "__main__":
    main()
