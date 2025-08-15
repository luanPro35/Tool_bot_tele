import json
import os
import sys
import time
import threading
from datetime import datetime
from offline_auto_responder import OfflineAutoResponder

class BotController:
    def __init__(self):
        self.responder = None
        self.responder_thread = None
        self.is_running = False
        
    def start_auto_responder(self):
        if self.is_running:
            print("❌ Auto responder đã đang chạy!")
            return
        
        try:
            self.responder = OfflineAutoResponder()
            self.responder_thread = threading.Thread(target=self.responder.run, daemon=True)
            self.responder_thread.start()
            self.is_running = True
            print("✅ Auto responder đã được khởi động!")
            print("🤖 Bot sẽ tự động trả lời khi bạn offline")
        except Exception as e:
            print(f"❌ Lỗi khi khởi động auto responder: {e}")
    
    def stop_auto_responder(self):
        if not self.is_running:
            print("❌ Auto responder chưa chạy!")
            return
        
        self.is_running = False
        if self.responder:
            self.responder.save_state()
        print("✅ Auto responder đã được dừng!")
    
    def set_online(self):
        if self.responder:
            self.responder.set_online()
            print("✅ Đã chuyển sang trạng thái ONLINE")
            print("💬 Bot sẽ không tự động trả lời nữa")
        else:
            print("❌ Auto responder chưa được khởi động!")
    
    def set_offline(self):
        if self.responder:
            self.responder.set_offline()
            print("✅ Đã chuyển sang trạng thái OFFLINE")
            print("🤖 Bot sẽ tự động trả lời tin nhắn")
        else:
            print("❌ Auto responder chưa được khởi động!")
    
    def get_status(self):
        if not self.is_running:
            print("❌ Auto responder chưa chạy")
            return
        
        if self.responder:
            status = "OFFLINE" if self.responder.is_offline else "ONLINE"
            offline_time = ""
            if self.responder.is_offline:
                duration = datetime.now() - self.responder.offline_start_time
                hours = int(duration.total_seconds() / 3600)
                minutes = int((duration.total_seconds() % 3600) / 60)
                offline_time = f" (đã offline {hours}h {minutes}m)"
            
            print(f"📊 Trạng thái: {status}{offline_time}")
            print(f"📨 Tin nhắn chờ xử lý: {len(self.responder.pending_messages)}")
            print(f"👥 Số user đã phản hồi: {len(self.responder.user_response_count)}")
        else:
            print("❌ Không thể lấy trạng thái!")
    
    def show_pending_messages(self):
        if not self.responder:
            print("❌ Auto responder chưa được khởi động!")
            return
        
        summary = self.responder.get_pending_messages_summary()
        print("\n" + "="*50)
        print("📨 TIN NHẮN CHỜ XỬ LÝ")
        print("="*50)
        print(summary)
        print("="*50)
    
    def clear_pending_messages(self):
        if not self.responder:
            print("❌ Auto responder chưa được khởi động!")
            return
        
        confirm = input("❓ Bạn có chắc muốn xóa tất cả tin nhắn chờ xử lý? (y/N): ")
        if confirm.lower() == 'y':
            self.responder.clear_pending_messages()
            print("✅ Đã xóa tất cả tin nhắn chờ xử lý!")
        else:
            print("❌ Đã hủy!")
    
    def show_menu(self):
        print("\n" + "="*50)
        print("🤖 BOT AUTO RESPONDER CONTROLLER")
        print("="*50)
        print("1. Khởi động Auto Responder")
        print("2. Dừng Auto Responder")
        print("3. Đặt trạng thái ONLINE")
        print("4. Đặt trạng thái OFFLINE")
        print("5. Xem trạng thái hiện tại")
        print("6. Xem tin nhắn chờ xử lý")
        print("7. Xóa tin nhắn chờ xử lý")
        print("8. Thoát")
        print("="*50)
    
    def run_interactive(self):
        print("🚀 Chào mừng đến với Bot Controller!")
        
        while True:
            self.show_menu()
            choice = input("👉 Chọn chức năng (1-8): ").strip()
            
            if choice == '1':
                self.start_auto_responder()
            elif choice == '2':
                self.stop_auto_responder()
            elif choice == '3':
                self.set_online()
            elif choice == '4':
                self.set_offline()
            elif choice == '5':
                self.get_status()
            elif choice == '6':
                self.show_pending_messages()
            elif choice == '7':
                self.clear_pending_messages()
            elif choice == '8':
                print("👋 Tạm biệt!")
                if self.is_running:
                    self.stop_auto_responder()
                break
            else:
                print("❌ Lựa chọn không hợp lệ!")
            
            input("\n⏸️  Nhấn Enter để tiếp tục...")

def main():
    controller = BotController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            controller.start_auto_responder()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                controller.stop_auto_responder()
        elif command == 'online':
            controller.start_auto_responder()
            time.sleep(1)
            controller.set_online()
            print("✅ Bot đã được đặt ở trạng thái ONLINE")
        elif command == 'offline':
            controller.start_auto_responder()
            time.sleep(1)
            controller.set_offline()
            print("✅ Bot đã được đặt ở trạng thái OFFLINE")
        elif command == 'status':
            controller.start_auto_responder()
            time.sleep(1)
            controller.get_status()
        else:
            print("❌ Lệnh không hợp lệ!")
            print("📖 Cách sử dụng:")
            print("  python bot_controller.py start")
            print("  python bot_controller.py online")
            print("  python bot_controller.py offline")
            print("  python bot_controller.py status")
            print("  python bot_controller.py")
    else:
        controller.run_interactive()

if __name__ == "__main__":
    main()
