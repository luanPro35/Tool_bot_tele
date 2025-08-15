#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script kiểm tra kết nối Telegram Bot
"""

import requests
import json

def test_telegram_bot():
    """Kiểm tra kết nối và thông tin bot Telegram"""
    
    # Đọc token từ config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        token = config['credentials']['telegram']['token']
    except Exception as e:
        print(f"Lỗi khi đọc token từ config: {e}")
        return False
    
    if not token:
        print("Không tìm thấy token trong config")
        return False
    
    print(f"Đang kiểm tra bot với token: {token[:10]}...")
    
    # Test getMe API
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('ok'):
            bot_info = data.get('result', {})
            print("✅ Kết nối thành công!")
            print(f"Bot name: {bot_info.get('first_name', 'N/A')}")
            print(f"Username: @{bot_info.get('username', 'N/A')}")
            print(f"Bot ID: {bot_info.get('id', 'N/A')}")
            print(f"Can join groups: {bot_info.get('can_join_groups', 'N/A')}")
            print(f"Can read all group messages: {bot_info.get('can_read_all_group_messages', 'N/A')}")
            return True
        else:
            print(f"❌ API trả về lỗi: {data.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
        return False

def test_get_updates():
    """Kiểm tra việc lấy tin nhắn"""
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        token = config['credentials']['telegram']['token']
    except Exception as e:
        print(f"Lỗi khi đọc token từ config: {e}")
        return False
    
    print("\nĐang kiểm tra getUpdates...")
    
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        params = {
            "limit": 5,
            "timeout": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('ok'):
            updates = data.get('result', [])
            print(f"✅ Lấy updates thành công! Có {len(updates)} tin nhắn")
            
            if updates:
                print("Tin nhắn gần đây:")
                for i, update in enumerate(updates[-3:], 1):  # Hiển thị 3 tin nhắn cuối
                    if 'message' in update:
                        msg = update['message']
                        sender = msg.get('from', {}).get('first_name', 'Unknown')
                        text = msg.get('text', 'No text')[:50]
                        print(f"  {i}. Từ {sender}: {text}...")
            else:
                print("Không có tin nhắn nào")
            return True
        else:
            print(f"❌ API trả về lỗi: {data.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối khi lấy updates: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
        return False

if __name__ == "__main__":
    print("=== KIỂM TRA TELEGRAM BOT ===")
    
    # Test kết nối cơ bản
    if test_telegram_bot():
        # Test lấy tin nhắn
        test_get_updates()
    
    print("\n=== KẾT THÚC KIỂM TRA ===")
