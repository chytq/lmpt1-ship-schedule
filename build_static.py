"""
สร้างเว็บแบบ static (ไฟล์ HTML ล้วน ไม่ต้องมี server)

รัน:  python build_static.py            -> สร้างปีปัจจุบัน
      python build_static.py 2026       -> ระบุปี
      python build_static.py 2025 2026  -> หลายปี

ผลลัพธ์อยู่ในโฟลเดอร์ docs/ — คือโฟลเดอร์ที่ GitHub Pages ใช้เสิร์ฟเว็บ
พอ build เสร็จแค่ git commit + push เว็บก็อัปเดตเอง
"""
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from app import app

BASE_DIR = Path(__file__).parent
DIST = BASE_DIR / "docs"

# JS ที่ใช้แทนการ submit form (static ไม่มี server ให้ submit)
NAV_JS = """
<script>
function _go(){
  var m = document.querySelector('select[name=month]').value.padStart(2,'0');
  var y = document.querySelector('select[name=year]').value;
  location.href = y + '-' + m + '.html';
}
</script>
"""


def to_static(html):
    """แปลง HTML จาก Flask ให้ทำงานได้แบบไฟล์ล้วน"""
    # 1) dropdown เปลี่ยนหน้าด้วย JS แทน form submit
    html = html.replace('onchange="this.form.submit()"', 'onchange="_go()"')
    # 2) path รูปภาพ: /static/img/x.png -> static/img/x.png (relative)
    html = html.replace('"/static/', '"static/')
    # 3) เอา auto-reload ทุก 5 นาทีออก (static ไม่มีอะไรให้ reload)
    html = re.sub(r"<script>\s*//[^\n]*\n\s*setTimeout.*?</script>", "", html, flags=re.S)
    # 4) ใส่ JS นำทาง
    html = html.replace("</body>", NAV_JS + "</body>")
    return html


def build(years):
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # ก๊อปรูปเรือ/โลโก้ไปด้วย
    shutil.copytree(BASE_DIR / "static", DIST / "static")

    now = datetime.now()
    pages = 0
    with app.test_client() as c:
        for year in years:
            for month in range(1, 13):
                r = c.get(f"/?month={month}&year={year}")
                if r.status_code != 200:
                    print(f"  !! {year}-{month:02d} -> HTTP {r.status_code}")
                    continue
                html = to_static(r.get_data(as_text=True))
                (DIST / f"{year}-{month:02d}.html").write_text(html, encoding="utf-8")
                pages += 1
            print(f"  {year}: สร้าง 12 เดือน")

    # index.html = เดือนปัจจุบัน (ถ้าปีปัจจุบันไม่ได้ build ใช้เดือนแรกของปีแรก)
    if now.year in years:
        landing = f"{now.year}-{now.month:02d}.html"
    else:
        landing = f"{years[0]}-01.html"
    (DIST / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url={landing}">'
        f'<title>LNG Vessel Schedule</title>'
        f'<p>กำลังเปิด… <a href="{landing}">คลิกที่นี่ถ้าไม่เด้งอัตโนมัติ</a></p>',
        encoding="utf-8")

    # GitHub Pages จะข้ามไฟล์/โฟลเดอร์ที่ขึ้นต้นด้วย _ ถ้าไม่มีไฟล์นี้
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    size_mb = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file()) / 1024 / 1024
    print()
    print(f"เสร็จ — {pages} หน้า, รวม {size_mb:.1f} MB")
    print(f"อยู่ที่: {DIST}")
    print()
    print("อัปเดตเว็บ:  git add -A  &&  git commit -m \"update schedule\"  &&  git push")


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]] or [datetime.now().year]
    print(f"สร้างเว็บ static ปี {', '.join(map(str, args))} ...")
    build(args)
