"""
WSGI entry point — ใช้ตอน deploy บน PythonAnywhere / mod_wsgi

บน PythonAnywhere ให้แก้ไฟล์ WSGI configuration เป็น:

    import sys
    path = '/home/<username>/ShipScheduleWeb'
    if path not in sys.path:
        sys.path.insert(0, path)

    from wsgi import application
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# บน server ไม่มีไฟล์ Excel บนเครื่อง — ให้อัปโหลดผ่านหน้า /admin แทน
os.environ.setdefault("DEFAULT_EXCEL", "/nonexistent")

from app import app as application  # noqa: E402

if __name__ == "__main__":
    application.run()
