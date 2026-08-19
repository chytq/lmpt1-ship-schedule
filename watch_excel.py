"""
อัปเดตเว็บตามเวลาที่กำหนด (ค่าปกติ: 06:00, 09:00, 12:00, 15:00, 18:00)

รันผ่าน WATCH_AUTO.bat หรือให้ Windows เปิดให้เองตอน login
(ตั้งด้วย SETUP_AUTO_UPDATE.bat)

    python watch_excel.py                       -> ตามตารางเวลาปกติ
    python watch_excel.py --at 6,9,12,15,18     -> กำหนดชั่วโมงเอง
    python watch_excel.py --on-change           -> โหมดเดิม: เซฟปุ๊บอัปเดตปั๊บ
    python watch_excel.py --once                -> เช็ครอบเดียวแล้วจบ

ถ้าถึงเวลาแล้วแต่ไฟล์ Excel ไม่ได้แก้อะไรเลย จะไม่ commit ซ้ำ
ถ้าเครื่องปิดคร่อมรอบไหนไป พอเปิดมาจะตามเก็บรอบล่าสุดที่พลาดให้ 1 ครั้ง
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

DEFAULT_HOURS = [6, 9, 12, 15, 18]

# ต้องเห็น mtime เดิมติดกันกี่รอบ ถึงจะถือว่าเซฟเสร็จแล้วจริง
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


def write_state(**kw):
    state = read_state()
    state.update(kw)
    try:
        STATE_FILE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def excel_mtime(path):
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def wait_until_stable(path):
    """รอจน mtime นิ่ง แปลว่าเซฟเสร็จแล้ว"""
    last = excel_mtime(path)
    same = 0
    for _ in range(24):
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


def run_update(path, reason):
    """สั่ง build + push คืน True ถ้าสำเร็จ"""
    log(f"{reason} — รอให้ไฟล์นิ่งก่อน ...")
    if wait_until_stable(path) is None:
        log("[!] ไฟล์หายระหว่างรอ — ข้ามรอบนี้")
        return False
    log("เริ่มอัปเดตเว็บ ...")
    try:
        update_web.main([])
    except Exception as e:
        log(f"[X] อัปเดตไม่สำเร็จ: {e}")
        log("    จะลองใหม่รอบหน้า")
        return False
    log("อัปเดตเสร็จ")
    return True


# ─── โหมดตามตารางเวลา ────────────────────────────────────────────────────────
def due_slot(now, hours):
    """รอบล่าสุดของวันนี้ที่ถึงเวลาแล้ว (None ถ้ายังไม่ถึงรอบแรกของวัน)"""
    past = [h for h in hours if now.hour >= h]
    if not past:
        return None
    return now.replace(hour=max(past), minute=0, second=0, microsecond=0)


def check_schedule(path, hours):
    now = datetime.now()
    slot = due_slot(now, hours)
    if slot is None:
        return False                       # ยังไม่ถึงรอบแรกของวัน
    key = slot.strftime("%Y-%m-%dT%H")
    if read_state().get("last_slot") == key:
        return False                       # รอบนี้ทำไปแล้ว

    if excel_mtime(path) is None:
        log(f"[!] ถึงรอบ {slot:%H:%M} แต่อ่านไฟล์ Excel ไม่ได้ — จะลองใหม่")
        return False

    late = " (ตามเก็บรอบที่พลาดไป)" if now.hour != slot.hour else ""
    if run_update(path, f"ถึงรอบ {slot:%H:%M}{late}"):
        write_state(last_slot=key,
                    updated_at=datetime.now().isoformat(timespec="seconds"))
        return True
    return False


# ─── โหมดเดิม: เซฟปุ๊บอัปเดตปั๊บ ──────────────────────────────────────────────
def check_on_change(path):
    mtime = excel_mtime(path)
    if mtime is None:
        log(f"[!] อ่านไฟล์ไม่ได้: {path}")
        return False
    if read_state().get("mtime") == mtime:
        return False
    stamp = datetime.fromtimestamp(mtime).strftime("%H:%M:%S")
    if run_update(path, f"ไฟล์ Excel เปลี่ยน (เซฟเมื่อ {stamp})"):
        write_state(mtime=excel_mtime(path),
                    updated_at=datetime.now().isoformat(timespec="seconds"))
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", default=",".join(map(str, DEFAULT_HOURS)),
                    help="ชั่วโมงที่ให้อัปเดต คั่นด้วยจุลภาค เช่น 6,9,12,15,18")
    ap.add_argument("--on-change", action="store_true",
                    help="โหมดเดิม: อัปเดตทันทีที่ไฟล์เปลี่ยน")
    ap.add_argument("--interval", type=int, default=60,
                    help="เช็คทุกกี่วินาที (default 60)")
    ap.add_argument("--once", action="store_true", help="เช็ครอบเดียวแล้วจบ")
    args = ap.parse_args()

    try:
        hours = sorted({int(x) for x in args.at.split(",") if x.strip() != ""})
    except ValueError:
        log(f"[X] รูปแบบ --at ไม่ถูกต้อง: {args.at!r}")
        return 1
    if not args.on_change and not all(0 <= h <= 23 for h in hours):
        log(f"[X] ชั่วโมงต้องอยู่ระหว่าง 0-23: {hours}")
        return 1

    path = flask_app.find_excel()
    if path is None:
        log("[X] ไม่พบไฟล์ Excel — ตรวจ path ในตัวแปร DEFAULT_EXCEL ใน app.py")
        return 1
    path = Path(path)

    check = (lambda: check_on_change(path)) if args.on_change \
        else (lambda: check_schedule(path, hours))

    if args.once:
        check()
        return 0

    log("=" * 58)
    log("เริ่มระบบอัปเดตเว็บอัตโนมัติ")
    log(f"  ไฟล์  : {path}")
    if args.on_change:
        log("  โหมด  : อัปเดตทันทีที่ไฟล์ Excel เปลี่ยน")
    else:
        log("  โหมด  : ตามเวลา " + ", ".join(f"{h:02d}:00" for h in hours))
        nxt = [h for h in hours if h > datetime.now().hour]
        log(f"  รอบถัดไป: {nxt[0]:02d}:00 วันนี้" if nxt
            else f"  รอบถัดไป: {hours[0]:02d}:00 พรุ่งนี้")
    log("=" * 58)

    while True:
        try:
            check()
        except KeyboardInterrupt:
            log("หยุดทำงานแล้ว")
            return 0
        except Exception:
            log("[X] เกิดข้อผิดพลาดที่ไม่คาดคิด:")
            log(traceback.format_exc())
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            log("หยุดทำงานแล้ว")
            return 0


if __name__ == "__main__":
    sys.exit(main())
