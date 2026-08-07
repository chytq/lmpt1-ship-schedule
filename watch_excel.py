"""
เฝ้าไฟล์ Excel — พอไฟล์ถูกแก้และเซฟ จะ build เว็บใหม่แล้ว push ขึ้น GitHub เอง

รันผ่าน WATCH_AUTO.bat หรือให้ Task Scheduler เปิดให้ตอน login
(ตั้งด้วย SETUP_AUTO_UPDATE.bat)

รันตรง ๆ ก็ได้:
    python watch_excel.py                 -> เช็คทุก 60 วินาที
    python watch_excel.py --interval 300  -> เช็คทุก 5 นาที
    python watch_excel.py --once          -> เช็ครอบเดียวแล้วจบ (ใช้กับ cron/scheduler)
"""
import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import app as flask_app
import update_web

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / ".watch_state.json"
LOG_FILE = BASE_DIR / "watch.log"
LOG_MAX_BYTES = 512 * 1024

# ต้องเห็น mtime เดิมติดกันกี่รอบ ถึงจะถือว่าเซฟเสร็จแล้วจริง
# (กันกรณี Excel/OneDrive ยังเขียนไฟล์ค้างอยู่)
STABLE_CHECKS = 2
STABLE_WAIT = 5


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line, flush=True)
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > LOG_MAX_BYTES:
            tail = LOG_FILE.read_text(encoding="utf-8").splitlines()[-500:]
            LOG_FILE.write_text("\n".join(tail) + "\n", encoding="utf-8")
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def read_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def excel_mtime(path):
    """mtime ของไฟล์ (None ถ้าไฟล์หายหรืออ่านไม่ได้ เช่นกำลังถูกเขียนอยู่)"""
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def wait_until_stable(path):
    """รอจน mtime นิ่ง แปลว่าเซฟเสร็จแล้ว คืน mtime สุดท้าย (None ถ้าไฟล์หาย)"""
    last = excel_mtime(path)
    same = 0
    for _ in range(24):          # กันค้าง: สูงสุด ~2 นาที
        time.sleep(STABLE_WAIT)
        now = excel_mtime(path)
        if now is None:
            return None
        if now == last:
            same += 1
            if same >= STABLE_CHECKS:
                return now
        else:
            same = 0
            last = now
    return last


def check_once(path):
    """คืน True ถ้ามีการอัปเดตเกิดขึ้นจริง"""
    mtime = excel_mtime(path)
    if mtime is None:
        log(f"[!] อ่านไฟล์ไม่ได้: {path}")
        return False

    state = read_state()
    if state.get("mtime") == mtime:
        return False                      # ไม่มีอะไรเปลี่ยน

    log(f"ไฟล์ Excel เปลี่ยน (เซฟเมื่อ {datetime.fromtimestamp(mtime):%H:%M:%S}) — รอให้เซฟเสร็จ ...")
    stable = wait_until_stable(path)
    if stable is None:
        log("[!] ไฟล์หายระหว่างรอ — ข้ามรอบนี้")
        return False

    log("เริ่มอัปเดตเว็บ ...")
    try:
        update_web.main([])
    except Exception as e:
        log(f"[X] อัปเดตไม่สำเร็จ: {e}")
        log("    จะลองใหม่รอบหน้า")
        return False

    write_state({"mtime": stable, "updated_at": datetime.now().isoformat(timespec="seconds")})
    log("อัปเดตเสร็จ")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=60, help="เช็คทุกกี่วินาที (default 60)")
    ap.add_argument("--once", action="store_true", help="เช็ครอบเดียวแล้วจบ")
    args = ap.parse_args()

    path = flask_app.find_excel()
    if path is None:
        log("[X] ไม่พบไฟล์ Excel — ตรวจ path ในตัวแปร DEFAULT_EXCEL ใน app.py")
        return 1
    path = Path(path)

    if args.once:
        check_once(path)
        return 0

    log("=" * 54)
    log("เริ่มเฝ้าไฟล์ Excel")
    log(f"  ไฟล์  : {path}")
    log(f"  เช็คทุก: {args.interval} วินาที")
    log("  ปิดหน้าต่างนี้ = หยุดอัปเดตอัตโนมัติ")
    log("=" * 54)

    while True:
        try:
            check_once(path)
        except KeyboardInterrupt:
            log("หยุดเฝ้าไฟล์แล้ว")
            return 0
        except Exception:
            log("[X] เกิดข้อผิดพลาดที่ไม่คาดคิด:")
            log(traceback.format_exc())
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            log("หยุดเฝ้าไฟล์แล้ว")
            return 0


if __name__ == "__main__":
    sys.exit(main())
