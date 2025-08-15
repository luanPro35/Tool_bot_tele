import os
import json
import logging

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
        logger.info("Config đã được khởi tạo")

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    self.config = json.load(file)
                logger.info(f"Đã tải cấu hình từ {self.config_file}")
            else:
                self.config = self.create_default_config()
                self.save_config()
                logger.info(f"Đã tạo tệp cấu hình mặc định {self.config_file}")
        except Exception as e:
            logger.error(f"Lỗi khi tải cấu hình: {str(e)}")
            self.config = self.create_default_config()

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, ensure_ascii=False, indent=4)
            logger.info(f"Đã lưu cấu hình vào {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu cấu hình: {str(e)}")
            return False

    def get(self, key, default=None):
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key, value):
        try:
            keys = key.split('.')
            d = self.config
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = value
            self.save_config()
        except Exception as e:
            logger.error(f"Lỗi khi đặt giá trị cấu hình cho key '{key}': {e}")

    def delete(self, key):
        keys = key.split('.')
        config = self.config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                logger.warning(f"Không thể xóa cấu hình không tồn tại: {key}")
                return False
            config = config[k]
        
        if keys[-1] in config:
            del config[keys[-1]]
            logger.info(f"Đã xóa cấu hình: {key}")
            return self.save_config()
        
        logger.warning(f"Không thể xóa cấu hình không tồn tại: {key}")
        return False

    def create_default_config(self):
        return {
            "app": {
                "name": "Auto Responder",
                "version": "1.0.0",
                "log_level": "INFO",
                "check_interval": 300,
                "auto_start": True
            },
            "platforms": {
                "email": {
                    "enabled": True,
                    "check_interval": 300
                },
                "telegram": {
                    "enabled": True,
                    "check_interval": 60,
                    "connect_timeout": 10,
                    "read_timeout": 30
                }
            },
            "credentials": {
                "email": {
                    "username": "your_email@example.com",
                    "password": "your_password",
                    "imap_server": "imap.example.com",
                    "imap_port": 993,
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587
                }
            },
            "excluded_senders": [
                "noreply@example.com",
                "newsletter@example.com"
            ],
            "keyword_template_mapping": {
                "help": "support_ticket",
                "hours": "business_hours",
                "vacation": "out_of_office",
                "hello": "welcome",
                "buy": "sales_inquiry"
            }
        }
