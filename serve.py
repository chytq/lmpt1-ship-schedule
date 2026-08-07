"""
Production server สำหรับ LNG Vessel Schedule
ใช้ waitress แทน Flask dev server — รองรับหลายคนเข้าพร้อมกันได้จริง

รัน:  python serve.py
หยุด: Ctrl+C
"""
import socket
from waitress import serve as waitress_serve

from app import app, ADMIN_PASSWORD

PORT = 5000
THREADS = 8


def lan_ip():
    """หา IP ของเครื่องในวง LAN (ไม่ต้องต่อเน็ตจริง)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    host = socket.gethostname()
    print("=" * 60)
    print("  LNG Vessel Schedule — Production Server")
    print("=" * 60)
    print(f"  เครื่องนี้     : http://localhost:{PORT}")
    print(f"  ส่งให้เพื่อน   : http://{host}:{PORT}     <-- ใช้ลิงก์นี้")
    print(f"  (สำรอง)       : http://{lan_ip()}:{PORT}")
    print(f"  หน้าผู้ดูแล    : http://{host}:{PORT}/admin")
    print(f"  รหัสผ่าน admin : {ADMIN_PASSWORD}")
    print("=" * 60)
    print("  * ลิงก์ชื่อเครื่องดีกว่า เพราะ IP เปลี่ยนได้ทุกครั้งที่ต่อเน็ตใหม่")
    print("  * ปิดหน้าต่างนี้ = เว็บดับ เพื่อนเข้าไม่ได้")
    print("  กด Ctrl+C เพื่อหยุด server")
    print()
    waitress_serve(app, host="0.0.0.0", port=PORT, threads=THREADS)
