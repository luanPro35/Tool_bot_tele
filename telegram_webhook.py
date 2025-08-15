#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot với Webhook thay vì polling
"""

import json
import logging
import requests
from flask import Flask, request, jsonify
from message_handler import MessageHandler
from response_templates import ResponseTemplates
from config import Config

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Khởi tạo các thành phần
config = Config()
templates = ResponseTemplates()
message_handler = MessageHandler(config, templates)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Xử lý webhook từ Telegram"""
    try:
        update = request.get_json()
        
        if not update:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        logger.info(f"Nhận được update: {update}")
        
        # Xử lý tin nhắn
        if 'message' in update:
            message_data = update['message']
            
            # Chỉ xử lý tin nhắn text
            if 'text' in message_data:
                # Tạo message object theo format của bot
                message = {
                    "platform": "telegram",
                    "chat_id": message_data["chat"]["id"],
                    "sender": message_data["from"].get("username", message_data["from"].get("first_name", "Unknown")),
                    "content": message_data.get("text", ""),
                    "timestamp": str(message_data["date"]),
                    "message_id": message_data["message_id"]
                }
                
                # Tạo phản hồi
                response = message_handler.create_response(message)
                
                if response:
                    # Gửi phản hồi
                    success = message_handler.send_response(message, response)
                    if success:
                        logger.info(f"Đã gửi phản hồi cho tin nhắn từ {message['sender']}")
                    else:
                        logger.error("Không thể gửi phản hồi")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Lỗi khi xử lý webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'bot': 'running'}), 200

def set_webhook():
    """Thiết lập webhook cho bot"""
    token = config.get("credentials.telegram.token")
    if not token:
        logger.error("Không tìm thấy token Telegram")
        return False
    
    # URL webhook - bạn cần thay đổi thành URL công khai của bạn
    webhook_url = "https://your-domain.com/webhook"  # Thay đổi URL này
    
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    data = {
        "url": webhook_url
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            logger.info(f"Webhook đã được thiết lập thành công: {webhook_url}")
            return True
        else:
            logger.error(f"Lỗi khi thiết lập webhook: {result.get('description')}")
            return False
            
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập webhook: {e}")
        return False

def delete_webhook():
    """Xóa webhook (chuyển về polling)"""
    token = config.get("credentials.telegram.token")
    if not token:
        logger.error("Không tìm thấy token Telegram")
        return False
    
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    
    try:
        response = requests.post(url)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            logger.info("Webhook đã được xóa thành công")
            return True
        else:
            logger.error(f"Lỗi khi xóa webhook: {result.get('description')}")
            return False
            
    except Exception as e:
        logger.error(f"Lỗi khi xóa webhook: {e}")
        return False

if __name__ == '__main__':
    logger.info("Bắt đầu Telegram Bot với Webhook")
    
    # Xóa webhook cũ trước (nếu có)
    delete_webhook()
    
    # Chạy Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
