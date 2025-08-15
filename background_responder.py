import json
import time
import logging
import requests
import os
import sys
import threading
from datetime import datetime
import subprocess

# Thiết lập logging
log_file = os.path.join(os.path.dirname(__file__), 'background_responder.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

class BackgroundResponder:
    def __init__(self):
        self.config_file = "background_config.json"
        self.state_file = "background_state.json"
        self.pid_file = "responder.pid"
        self.load_config()
        self.load_state()
        self.responded_messages = set()
        self.running = True
        
    def load_config(self):
        """Tải cấu hình từ file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "telegram_token": "8216435475:AAHGgvKc9sFSiF1ejudtBpQx-B7mP8g3muw",
                "check_interval": 15,
                "auto_offline_message": "🤖 Chào {name}!\n\nCảm ơn bạn đã nhắn tin! Tôi hiện không có mặt và không thể trả lời ngay.\n\n💬 Tin nhắn của bạn đã được ghi nhận, tôi sẽ phản hồi sớm nhất có thể.\n\n🙏 Cảm ơn sự kiên nhẫn của bạn!",
                "enabled": True
            }
            self.save_config()
            
    def save_config(self):
        """Lưu cấu hình"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def load_state(self):
        """Tải trạng thái hiện tại"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {
                "last_update_id": 0,
                "start_time": datetime.now().isoformat(),
                "message_count": 0
            }
            self.save_state()
            
    def save_state(self):
        """Lưu trạng thái"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
            
    def save_pid(self):
        """Lưu Process ID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
    def remove_pid(self):
        """Xóa file PID"""
        try:
            os.remove(self.pid_file)
        except:
            pass
            
    def is_running(self):
        """Kiểm tra xem service có đang chạy không"""
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            # Kiểm tra process có tồn tại không
            os.kill(pid, 0)
            return True
        except:
            return False
            
    def get_telegram_updates(self):
        """Lấy tin nhắn mới từ Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/getUpdates"
            params = {
                "offset": self.state["last_update_id"] + 1,
                "timeout": 10
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data["ok"]:
                    return data["result"]
            return []
        except Exception as e:
            logger.error(f"Lỗi khi lấy tin nhắn: {e}")
            return []
            
    def send_telegram_message(self, chat_id, text):
        """Gửi tin nhắn qua Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Lỗi khi gửi tin nhắn: {e}")
            return False
            
    def process_message(self, update):
        """Xử lý tin nhắn nhận được"""
        try:
            if not self.config.get("enabled", True):
                return
                
            if "message" not in update:
                return
                
            message = update["message"]
            chat_id = message["chat"]["id"]
            message_id = message["message_id"]
            
            # Tránh trả lời trùng lặp
            unique_id = f"{chat_id}_{message_id}"
            if unique_id in self.responded_messages:
                return
                
            # Lấy tên người gửi
            sender_name = message["from"].get("first_name", "bạn")
            if message["from"].get("last_name"):
                sender_name += " " + message["from"]["last_name"]
                
            # Gửi tin nhắn offline tự động
            response_text = self.config["auto_offline_message"].format(name=sender_name)
                
            # Gửi phản hồi
            if self.send_telegram_message(chat_id, response_text):
                self.responded_messages.add(unique_id)
                self.state["message_count"] += 1
                self.save_state()
                logger.info(f"✅ Đã trả lời tự động cho {sender_name} (ID: {chat_id})")
            else:
                logger.error(f"❌ Không thể gửi tin nhắn cho {sender_name}")
                
        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin nhắn: {e}")
            
    def run_daemon(self):
        """Chạy service ngầm"""
        self.save_pid()
        logger.info("🚀 Background Responder đã khởi động")
        logger.info(f"📱 Token: ...{self.config['telegram_token'][-10:]}")
        logger.info(f"⏰ Kiểm tra mỗi {self.config['check_interval']} giây")
        
        try:
            while self.running:
                # Lấy tin nhắn mới
                updates = self.get_telegram_updates()
                
                for update in updates:
                    # Cập nhật last_update_id
                    self.state["last_update_id"] = update["update_id"]
                    self.save_state()
                    
                    # Xử lý tin nhắn
                    self.process_message(update)
                    
                # Dọn dẹp danh sách tin nhắn đã trả lời
                if len(self.responded_messages) > 1000:
                    self.responded_messages = set(list(self.responded_messages)[-500:])
                    
                # Nghỉ trước khi kiểm tra lại
                time.sleep(self.config["check_interval"])
                
        except Exception as e:
            logger.error(f"❌ Lỗi không mong muốn: {e}")
        finally:
            self.remove_pid()
            logger.info("🛑 Background Responder đã dừng")
            
    def stop_daemon(self):
        """Dừng service"""
        self.running = False
        
    def get_status(self):
        """Lấy thông tin trạng thái"""
        if self.is_running():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                return {
                    "running": True,
                    "start_time": state.get("start_time"),
                    "message_count": state.get("message_count", 0),
                    "enabled": self.config.get("enabled", True)
                }
            except:
                return {"running": True, "start_time": "Unknown", "message_count": 0}
        else:
            return {"running": False}

def start_service():
    """Khởi động service"""
    responder = BackgroundResponder()
    if responder.is_running():
        print("❌ Service đã đang chạy!")
        return False
        
    print("🚀 Đang khởi động Background Responder...")
    
    # Chạy trong background
    if os.name == 'nt':  # Windows
        subprocess.Popen([
            sys.executable, __file__, '--daemon'
        ], creationflags=subprocess.CREATE_NO_WINDOW)
    else:  # Linux/Mac
        subprocess.Popen([sys.executable, __file__, '--daemon'])
        
    time.sleep(2)  # Đợi service khởi động
    
    if responder.is_running():
        print("✅ Background Responder đã khởi động thành công!")
        print("💡 Bot sẽ tự động trả lời tin nhắn khi bạn offline")
        return True
    else:
        print("❌ Không thể khởi động service!")
        return False

def stop_service():
    """Dừng service"""
    responder = BackgroundResponder()
    if not responder.is_running():
        print("❌ Service không đang chạy!")
        return False
        
    try:
        with open(responder.pid_file, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 9 if os.name != 'nt' else 1)
        responder.remove_pid()
        print("✅ Đã dừng Background Responder!")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi dừng service: {e}")
        return False

def show_status():
    """Hiển thị trạng thái"""
    responder = BackgroundResponder()
    status = responder.get_status()
    
    print("\n" + "="*50)
    print("📊 TRẠNG THÁI BACKGROUND RESPONDER")
    print("="*50)
    
    if status["running"]:
        print("🟢 Trạng thái: ĐANG CHẠY")
        print(f"⏰ Khởi động: {status.get('start_time', 'Unknown')}")
        print(f"📨 Tin nhắn đã trả lời: {status.get('message_count', 0)}")
        print(f"🔧 Trạng thái: {'BẬT' if status.get('enabled', True) else 'TẮT'}")
    else:
        print("🔴 Trạng thái: KHÔNG CHẠY")
        
    print("="*50)

def toggle_service():
    """Bật/tắt service"""
    responder = BackgroundResponder()
    current_enabled = responder.config.get("enabled", True)
    responder.config["enabled"] = not current_enabled
    responder.save_config()
    
    status = "BẬT" if responder.config["enabled"] else "TẮT"
    print(f"✅ Đã {status} Background Responder")

def main():
    """Menu điều khiển"""
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        # Chạy trong chế độ daemon
        responder = BackgroundResponder()
        responder.run_daemon()
        return
        
    while True:
        print("\n" + "="*50)
        print("🤖 BACKGROUND AUTO RESPONDER")
        print("="*50)
        print("1. 🚀 Khởi động Background Service")
        print("2. 🛑 Dừng Background Service")
        print("3. 📊 Xem trạng thái")
        print("4. 🔧 Bật/Tắt Auto Reply")
        print("5. ⚙️  Chỉnh sửa tin nhắn")
        print("6. 🚪 Thoát")
        print("="*50)
        
        choice = input("👉 Chọn chức năng (1-6): ").strip()
        
        if choice == "1":
            start_service()
            
        elif choice == "2":
            stop_service()
            
        elif choice == "3":
            show_status()
            
        elif choice == "4":
            toggle_service()
            
        elif choice == "5":
            responder = BackgroundResponder()
            print(f"\nTin nhắn offline hiện tại:")
            print(responder.config["auto_offline_message"])
            new_msg = input("\nNhập tin nhắn mới (Enter để bỏ qua): ")
            if new_msg.strip():
                responder.config["auto_offline_message"] = new_msg
                responder.save_config()
                print("✅ Đã cập nhật tin nhắn offline")
                
        elif choice == "6":
            print("👋 Tạm biệt!")
            break
            
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()