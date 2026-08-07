"""
เปิด/ปิด ระบบอัปเดตเว็บอัตโนมัติ

    python setup_auto.py on      -> เปิด (เริ่มเฝ้าไฟล์ + ให้เปิดเองตอน login)
    python setup_auto.py off     -> ปิด
    python setup_auto.py status  -> ดูสถานะ

ใช้ Startup folder ไม่ใช่ Task Scheduler เพราะเครื่องบริษัทบล็อกการสร้าง
scheduled task (Access is denied) แต่ Startup folder ใช้ได้ปกติไม่ต้องเป็น admin
"""
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
WATCHER = BASE_DIR / "watch_excel.py"
PYTHONW = Path(sys.executable).with_name("pythonw.exe")
STARTUP = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup"
SHORTCUT = STARTUP / "LNG Vessel Schedule Auto Update.lnk"
INTERVAL = 120


def ps(script):
    return subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def watcher_pids():
    """PID ของ process ที่กำลังรัน watch_excel.py อยู่"""
    r = ps("Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe' or Name='python.exe'\" | "
           "Where-Object { $_.CommandLine -like '*watch_excel.py*' } | "
           "Select-Object -ExpandProperty ProcessId")
    return [int(x) for x in r.stdout.split() if x.strip().isdigit()]


def stop_watcher():
    pids = watcher_pids()
    for pid in pids:
        ps(f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue")
    return len(pids)


def start_watcher():
    subprocess.Popen(
        [str(PYTHONW), str(WATCHER), "--interval", str(INTERVAL)],
        cwd=str(BASE_DIR),
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )


def make_shortcut():
    STARTUP.mkdir(parents=True, exist_ok=True)
    r = ps(f"""
$ws = New-Object -ComObject WScript.Shell
$l = $ws.CreateShortcut('{SHORTCUT}')
$l.TargetPath       = '{PYTHONW}'
$l.Arguments        = '"{WATCHER}" --interval {INTERVAL}'
$l.WorkingDirectory = '{BASE_DIR}'
$l.Description      = 'อัปเดตเว็บตารางเรืออัตโนมัติเมื่อไฟล์ Excel เปลี่ยน'
$l.WindowStyle      = 7
$l.Save()
""")
    return r.returncode == 0 and SHORTCUT.exists()


def cmd_on():
    if not PYTHONW.exists():
        print(f"[X] ไม่พบ pythonw.exe ที่ {PYTHONW}")
        return 1

    stopped = stop_watcher()
    if stopped:
        print(f"  หยุดตัวเฝ้าเดิม {stopped} ตัว")

    print("  ตั้งให้เปิดเองตอน login ...")
    if make_shortcut():
        print("        OK")
    else:
        print("        ไม่สำเร็จ — ยังเปิดเองด้วย WATCH_AUTO.bat ได้")

    print("  เริ่มเฝ้าไฟล์ Excel ...")
    start_watcher()
    print("        OK")

    print()
    print("-" * 54)
    print("  เปิดระบบอัปเดตอัตโนมัติแล้ว")
    print()
    print("  ต่อจากนี้: แก้ไฟล์ Excel แล้วเซฟ")
    print(f"  ภายใน {INTERVAL // 60} นาที เว็บจะอัปเดตเอง ไม่ต้องกดอะไร")
    print()
    print("  ดูว่าทำอะไรไปบ้าง : watch.log")
    print("  ปิดระบบ           : STOP_AUTO_UPDATE.bat")
    print()
    print("  หมายเหตุ: เครื่องนี้ต้องเปิดอยู่และต่อเน็ต")
    print("-" * 54)
    return 0


def cmd_off():
    stopped = stop_watcher()
    print(f"  หยุดตัวเฝ้า {stopped} ตัว")
    if SHORTCUT.exists():
        SHORTCUT.unlink()
        print("  ลบออกจาก startup แล้ว")
    print()
    print("-" * 54)
    print("  ปิดระบบอัปเดตอัตโนมัติแล้ว")
    print("  อัปเดตเองด้วย UPDATE_WEB.bat แทน")
    print("-" * 54)
    return 0


def cmd_status():
    pids = watcher_pids()
    print(f"  ตัวเฝ้ากำลังทำงาน : {'ใช่ (PID ' + ', '.join(map(str, pids)) + ')' if pids else 'ไม่'}")
    print(f"  เปิดเองตอน login  : {'ใช่' if SHORTCUT.exists() else 'ไม่'}")
    log = BASE_DIR / "watch.log"
    if log.exists():
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
        print()
        print("  บันทึกล่าสุด:")
        for line in lines[-8:]:
            print("   ", line)
    return 0


if __name__ == "__main__":
    action = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
    print()
    sys.exit({"on": cmd_on, "off": cmd_off, "status": cmd_status}.get(action, cmd_status)())
