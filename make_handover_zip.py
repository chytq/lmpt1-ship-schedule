"""
สร้างไฟล์ zip สำหรับส่งให้ dev (ไม่ต้องใช้ GitHub)

    python make_handover_zip.py

จะได้ไฟล์ ShipScheduleWeb_forDev_YYYY-MM-DD.zip ไว้ที่ Desktop
ส่งทาง LINE / อีเมล / USB ได้เลย

สิ่งที่ "ไม่" ใส่ลงไป: ไฟล์ Excel จริง, รหัสผ่าน, log, ไฟล์ที่ build แล้ว,
cache และประวัติ git — ตรวจซ้ำอีกชั้นก่อนเซฟทุกครั้ง
"""
import sys
import zipfile
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent
DESKTOP = BASE_DIR.parent
OUT = DESKTOP / f"ShipScheduleWeb_forDev_{date.today():%Y-%m-%d}.zip"

# โฟลเดอร์ที่ข้ามทั้งอัน
SKIP_DIRS = {".git", "__pycache__", "docs", "uploads", "dist", ".claude", ".vscode"}

# ไฟล์ที่ห้ามติดไปเด็ดขาด
SKIP_FILES = {".admin_password", "watch.log", ".watch_state.json"}
SKIP_SUFFIX = {".pyc", ".pyo", ".log"}

# ข้อมูลจริงห้ามหลุด — sample/*.xlsx ใส่ได้ (ข้อมูลปลอม) นอกนั้นห้ามหมด
SECRET_PATTERNS = [".xlsm", "admin_password", "watch.log", ".env"]
SAMPLE_ALLOWED = "sample/sample_work_plan.xlsx"


def should_include(path: Path) -> bool:
    rel = path.relative_to(BASE_DIR)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if path.name in SKIP_FILES or path.suffix.lower() in SKIP_SUFFIX:
        return False
    # ยอมให้เฉพาะ sample/*.xlsx (ข้อมูลปลอม) — ที่อื่นห้ามมีไฟล์ Excel
    if path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        return rel.parts[:1] == ("sample",) and path.suffix.lower() == ".xlsx"
    return True


def audit(names):
    """ตรวจซ้ำว่าไม่มีอะไรที่ไม่ควรอยู่ในไฟล์ zip"""
    bad = []
    for n in names:
        low = n.lower()
        if low == SAMPLE_ALLOWED:
            continue                       # ข้อมูลปลอม ส่งได้
        if low.endswith((".xlsx", ".xls")):
            bad.append(n)                  # ไฟล์ Excel อื่นห้ามติดไป
            continue
        if any(pat in low for pat in SECRET_PATTERNS):
            bad.append(n)
    return bad


def main():
    # ต้องมีข้อมูลตัวอย่างก่อน dev จะได้แกะแล้วรันได้ทันที
    sample = BASE_DIR / "sample" / "sample_work_plan.xlsx"
    if not sample.exists():
        print("ยังไม่มีข้อมูลตัวอย่าง — สร้างให้ก่อน ...")
        import subprocess
        r = subprocess.run([sys.executable, str(BASE_DIR / "sample" / "make_sample_excel.py")],
                           cwd=BASE_DIR)
        if r.returncode != 0:
            print("สร้างข้อมูลตัวอย่างไม่สำเร็จ")
            return 1
        print()

    files = sorted(p for p in BASE_DIR.rglob("*") if p.is_file() and should_include(p))
    if not files:
        print("ไม่พบไฟล์ที่จะใส่")
        return 1

    names = [str(p.relative_to(BASE_DIR)).replace("\\", "/") for p in files]
    bad = audit(names)
    if bad:
        print("[X] หยุด — พบไฟล์ที่ไม่ควรส่งออกไป:")
        for b in bad:
            print("     ", b)
        return 2

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p, n in zip(files, names):
            z.write(p, f"ShipScheduleWeb/{n}")

    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"สร้างไฟล์แล้ว: {OUT.name}")
    print(f"  ที่อยู่ : {OUT}")
    print(f"  ขนาด  : {size_mb:.2f} MB")
    print(f"  ไฟล์  : {len(files)} ไฟล์")
    print()
    print("ตรวจแล้วว่าไม่มี: ไฟล์ Excel จริง, รหัสผ่าน, log, ประวัติ git")
    print()
    print("ส่งไฟล์นี้ให้ dev ได้เลย — แกะแล้วอ่าน README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
