#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module quản lý các mẫu phản hồi tin nhắn
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


class ResponseTemplates:
    """Lớp quản lý các mẫu phản hồi tin nhắn"""

    def __init__(self, templates_file="templates.json"):
        """Khởi tạo với tệp mẫu phản hồi"""
        self.templates_file = templates_file
        self.templates = {}
        self.load_templates()
        logger.info("ResponseTemplates đã được khởi tạo")

    def load_templates(self):
        """Tải các mẫu phản hồi từ tệp JSON"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as file:
                    self.templates = json.load(file)
                logger.info(f"Đã tải {len(self.templates)} mẫu phản hồi từ {self.templates_file}")
            else:
                # Tạo mẫu mặc định nếu tệp không tồn tại
                self.templates = self.create_default_templates()
                self.save_templates()
                logger.info(f"Đã tạo tệp mẫu phản hồi mặc định {self.templates_file}")
        except Exception as e:
            logger.error(f"Lỗi khi tải mẫu phản hồi: {str(e)}")
            # Tạo mẫu mặc định nếu có lỗi
            self.templates = self.create_default_templates()

    def save_templates(self):
        """Lưu các mẫu phản hồi vào tệp JSON"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as file:
                json.dump(self.templates, file, ensure_ascii=False, indent=4)
            logger.info(f"Đã lưu {len(self.templates)} mẫu phản hồi vào {self.templates_file}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu mẫu phản hồi: {str(e)}")
            return False

    def get_template(self, template_id):
        """Lấy mẫu phản hồi theo ID"""
        template = self.templates.get(template_id)
        if not template:
            logger.warning(f"Không tìm thấy mẫu phản hồi với ID: {template_id}")
            # Trả về mẫu mặc định nếu không tìm thấy
            return self.templates.get("default", {
                "subject": "Phản hồi tự động",
                "body": "Cảm ơn bạn đã liên hệ. Đây là tin nhắn tự động. Chúng tôi sẽ phản hồi sớm nhất có thể."
            })
        return template

    def add_template(self, template_id, template_content):
        """Thêm hoặc cập nhật mẫu phản hồi"""
        self.templates[template_id] = template_content
        logger.info(f"Đã thêm/cập nhật mẫu phản hồi với ID: {template_id}")
        return self.save_templates()

    def delete_template(self, template_id):
        """Xóa mẫu phản hồi theo ID"""
        if template_id in self.templates:
            del self.templates[template_id]
            logger.info(f"Đã xóa mẫu phản hồi với ID: {template_id}")
            return self.save_templates()
        logger.warning(f"Không thể xóa mẫu phản hồi không tồn tại với ID: {template_id}")
        return False

    def list_templates(self):
        """Liệt kê tất cả các mẫu phản hồi"""
        return self.templates

    def create_default_templates(self):
        """Tạo các mẫu phản hồi mặc định"""
        return {
            "default": {
                "subject": "Phản hồi tự động",
                "body": "Cảm ơn bạn đã liên hệ. Đây là tin nhắn tự động. Chúng tôi sẽ phản hồi sớm nhất có thể."
            },
            "welcome": {
                "subject": "Chào mừng bạn",
                "body": "Cảm ơn bạn đã liên hệ với chúng tôi. Chúng tôi đã nhận được tin nhắn của bạn và sẽ phản hồi trong thời gian sớm nhất."
            },
            "out_of_office": {
                "subject": "Thông báo vắng mặt",
                "body": "Cảm ơn bạn đã liên hệ. Hiện tại tôi đang vắng mặt và sẽ trở lại vào ngày DD/MM/YYYY. Tôi sẽ phản hồi tin nhắn của bạn sau khi trở lại."
            },
            "business_hours": {
                "subject": "Giờ làm việc",
                "body": "Cảm ơn bạn đã liên hệ. Giờ làm việc của chúng tôi là từ 9:00 đến 17:00, Thứ Hai đến Thứ Sáu. Chúng tôi sẽ phản hồi tin nhắn của bạn trong giờ làm việc tiếp theo."
            }
        }