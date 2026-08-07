"""
อัปเดตเว็บบน GitHub Pages — build หน้าเว็บใหม่ แล้ว commit + push ให้อัตโนมัติ

ปกติเรียกผ่าน UPDATE_WEB.bat (ดับเบิลคลิก) แต่รันตรง ๆ ก็ได้:
    python update_web.py            -> ทุกปีที่มีข้อมูลใน Excel
    python update_web.py 2026 2027  -> ระบุปีเอง
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=BASE_DIR,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip())
    return r


def main(year_args):
    print()
    print("=" * 56)
    print("  อัปเดตเว็บตารางเรือ")
    print("=" * 56)

    # ── 1. build ────────────────────────────────────────────────
    print()
    print("[1/3] สร้างหน้าเว็บใหม่จากไฟล์ Excel ...")
    r = subprocess.run([sys.executable, "build_static.py", *year_args],
                       cwd=BASE_DIR)
    if r.returncode != 0:
        raise RuntimeError("สร้างหน้าเว็บไม่สำเร็จ — อ่านข้อความด้านบน")

    # ── 2. commit ───────────────────────────────────────────────
    print()
    print("[2/3] บันทึกการเปลี่ยนแปลง ...")
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        print("      ไม่มีอะไรเปลี่ยน — เว็บตรงกับ Excel อยู่แล้ว")
        return
    changed = git("diff", "--cached", "--name-only").stdout.strip().splitlines()
    print(f"      มี {len(changed)} ไฟล์เปลี่ยน")
    git("commit", "-m", f"update schedule {datetime.now():%Y-%m-%d %H:%M}")

    # ── 3. push ─────────────────────────────────────────────────
    print()
    print("[3/3] ส่งขึ้น GitHub ...")
    if not git("remote", check=False).stdout.strip():
        print("      ยังไม่ได้ตั้ง remote — ข้ามการ push")
        print("      ตั้งด้วย: git remote add origin <URL ของ repo>")
        return
    git("push")

    url = git("remote", "get-url", "origin", check=False).stdout.strip()
    site = ""
    if "github.com" in url:
        part = url.split("github.com")[-1].lstrip(":/").removesuffix(".git")
        if "/" in part:
            user, repo = part.split("/", 1)
            site = f"https://{user}.github.io/{repo}/"

    print()
    print("-" * 56)
    print("  เสร็จแล้ว! เว็บจะอัปเดตภายใน 1-2 นาที")
    if site:
        print(f"  {site}")
    print("-" * 56)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        print()
        print("*" * 56)
        print(f"  ไม่สำเร็จ: {e}")
        print("*" * 56)
        sys.exit(1)
