import json
import time
import logging
import requests
from datetime import datetime
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_responder.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
class SimpleAutoResponder:
    def __init__(self):
        self.config_file = "simple_config.json"
        self.state_file = "responder_state.json"
        self.load_config()
        self.load_state()
        self.responded_messages = set()  
    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "telegram_token": "8216435475:AAHGgvKc9sFSiF1ejudtBpQx-B7mP8g3muw",
                "check_interval": 10,  
                "messages": {
                    "offline": "🤖 Chào {name}!\n\nCảm ơn bạn đã nhắn tin! Tôi hiện đang offline và không thể trả lời ngay.\n\n💬 Vui lòng để lại tin nhắn, tôi sẽ phản hồi sớm nhất có thể khi online trở lại.\n\n🙏 Cảm ơn sự kiên nhẫn của bạn!",
                    "online": "👋 Chào {name}!\n\nCảm ơn bạn đã nhắn tin! Tôi đã nhận được tin nhắn của bạn.\n\n⏰ Tôi sẽ trả lời bạn trong vòng 2-3 phút.\n\n😊 Cảm ơn bạn đã chờ đợi!"
                }
            }
            self.save_config()
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    def load_state(self):
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {
                "is_online": False,
                "last_update_id": 0,
                "start_time": datetime.now().isoformat()
            }
            self.save_state()
    def save_state(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    def set_online(self):
        self.state["is_online"] = True
        self.save_state()
        logger.info("✅ Đã chuyển sang trạng thái ONLINE")
    def set_offline(self):
        self.state["is_online"] = False
        self.save_state()
        logger.info("❌ Đã chuyển sang trạng thái OFFLINE")
    def get_status(self):
        status = "ONLINE" if self.state["is_online"] else "OFFLINE"
        return f"🔄 Trạng thái hiện tại: {status}"
    def get_telegram_updates(self):
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
        try:
            if "message" not in update:
                return
            message = update["message"]
            chat_id = message["chat"]["id"]
            message_id = message["message_id"]
            unique_id = f"{chat_id}_{message_id}"
            if unique_id in self.responded_messages:
                return
            sender_name = message["from"].get("first_name", "bạn")
            if message["from"].get("last_name"):
                sender_name += " " + message["from"]["last_name"]
            if self.state["is_online"]:
                response_text = self.config["messages"]["online"].format(name=sender_name)
            else:
                response_text = self.config["messages"]["offline"].format(name=sender_name)
            if self.send_telegram_message(chat_id, response_text):
                self.responded_messages.add(unique_id)
                logger.info(f"✅ Đã trả lời {sender_name} (ID: {chat_id})")
            else:
                logger.error(f"❌ Không thể gửi tin nhắn cho {sender_name}")
        except Exception as e:
            logger.error(f"Lỗi khi xử lý tin nhắn: {e}")
    def run(self):
        logger.info("🚀 Bắt đầu Simple Auto Responder")
        logger.info(f"📱 Token: ...{self.config['telegram_token'][-10:]}")
        logger.info(f"🔄 Trạng thái: {'ONLINE' if self.state['is_online'] else 'OFFLINE'}")
        try:
            while True:
                updates = self.get_telegram_updates()
                for update in updates:
                    self.state["last_update_id"] = update["update_id"]
                    self.save_state()
                    self.process_message(update)
                if len(self.responded_messages) > 1000:
                    self.responded_messages = set(list(self.responded_messages)[-500:])
                time.sleep(self.config["check_interval"])
        except KeyboardInterrupt:
            logger.info("🛑 Đã dừng Auto Responder")
        except Exception as e:
            logger.error(f"❌ Lỗi không mong muốn: {e}")

def main():
    responder = SimpleAutoResponder()
    while True:
        print("\n" + "="*50)
        print("🤖 SIMPLE AUTO RESPONDER")
        print("="*50)
        print("1. 🚀 Khởi động Auto Responder")
        print("2. 🟢 Đặt trạng thái ONLINE")
        print("3. 🔴 Đặt trạng thái OFFLINE")
        print("4. 📊 Xem trạng thái hiện tại")
        print("5. ⚙️  Chỉnh sửa tin nhắn")
        print("6. 🚪 Thoát")
        print("="*50)
        choice = input("👉 Chọn chức năng (1-6): ").strip()
        if choice == "1":
            print("\n🚀 Đang khởi động Auto Responder...")
            print("💡 Nhấn Ctrl+C để dừng")
            responder.run()
        elif choice == "2":
            responder.set_online()
            print("✅ Đã chuyển sang trạng thái ONLINE")
        elif choice == "3":
            responder.set_offline()
            print("❌ Đã chuyển sang trạng thái OFFLINE")
        elif choice == "4":
            print(f"\n{responder.get_status()}")
        elif choice == "5":
            print("\n⚙️ Chỉnh sửa tin nhắn:")
            print("1. Tin nhắn khi OFFLINE")
            print("2. Tin nhắn khi ONLINE")
            msg_choice = input("Chọn (1-2): ").strip()
            if msg_choice == "1":
                print(f"\nTin nhắn OFFLINE hiện tại:")
                print(responder.config["messages"]["offline"])
                new_msg = input("\nNhập tin nhắn mới (Enter để bỏ qua): ")
                if new_msg.strip():
                    responder.config["messages"]["offline"] = new_msg
                    responder.save_config()
                    print("✅ Đã cập nhật tin nhắn OFFLINE")
            elif msg_choice == "2":
                print(f"\nTin nhắn ONLINE hiện tại:")
                print(responder.config["messages"]["online"])
                new_msg = input("\nNhập tin nhắn mới (Enter để bỏ qua): ")
                if new_msg.strip():
                    responder.config["messages"]["online"] = new_msg
                    responder.save_config()
                    print("✅ Đã cập nhật tin nhắn ONLINE")
        elif choice == "6":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()