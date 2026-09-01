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
from datetime import date, datetime
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


def to_static(html, built_years):
    """แปลง HTML จาก Flask ให้ทำงานได้แบบไฟล์ล้วน"""
    # 1) dropdown เปลี่ยนหน้าด้วย JS แทน form submit
    html = html.replace('onchange="this.form.submit()"', 'onchange="_go()"')
    # 2) path รูปภาพ: /static/img/x.png -> static/img/x.png (relative)
    html = html.replace('"/static/', '"static/')
    # 3) เอา auto-reload ทุก 5 นาทีออก (static ไม่มีอะไรให้ reload)
    html = re.sub(r"<script>\s*//[^\n]*\n\s*setTimeout.*?</script>", "", html, flags=re.S)
    # 4) ตัดปีที่ไม่ได้ build ออกจาก dropdown — ไม่งั้นเลือกแล้วเจอ 404
    ok = {str(y) for y in built_years}
    html = re.sub(
        r'\s*<option value="(\d{4})"[^>]*>\s*\d{4}\s*</option>',
        lambda m: m.group(0) if m.group(1) in ok else "",
        html)
    # 5) ใส่ JS นำทาง
    html = html.replace("</body>", NAV_JS + "</body>")
    return html


class SampleDataRefused(RuntimeError):
    """กันไม่ให้เอาข้อมูลตัวอย่างขึ้นเว็บสาธารณะ"""


def assert_real_data():
    """ตรวจก่อนเสมอว่ากำลังใช้ข้อมูลจริง และ "อ่านได้จริง"

    นี่คือด่านสำคัญ: ถ้าไฟล์ Excel หายไปหรืออ่านไม่ได้ชั่วคราว (OneDrive กำลัง
    sync, Excel ล็อกไฟล์อยู่ตอนเซฟ) ต้องหยุด ไม่ใช่สร้างเว็บเปล่าทับของดี

    เช็คแค่ path.exists() ไม่พอ — เคยเกิดจริงมาแล้วว่าไฟล์มีอยู่แต่เปิดไม่ได้
    (Errno 13 Permission denied) แล้วเว็บสาธารณะกลายเป็นปฏิทินเปล่า
    """
    import app as _app
    import core
    path, kind = _app.excel_source()
    if kind == "sample" or _app.USE_SAMPLE:
        raise SampleDataRefused(
            "กำลังอยู่ในโหมดข้อมูลตัวอย่าง (USE_SAMPLE=1) — ไม่สร้างเว็บให้\n"
            "     ข้อมูลสมมติห้ามขึ้นเว็บสาธารณะ ถ้าจะ build จริงให้ปิด USE_SAMPLE ก่อน")
    if path is None:
        raise SampleDataRefused(
            f"หาไฟล์ Excel จริงไม่เจอ: {_app.DEFAULT_EXCEL}\n"
            "     ตรวจว่าไฟล์ยังอยู่และ OneDrive sync เสร็จแล้ว — ยังไม่แตะเว็บของเดิม")
    # ต้องเปิดและ parse ได้จริง ไม่ใช่แค่มีไฟล์
    try:
        years = core.available_years(path, _app.DEFAULT_SHEET)
    except PermissionError as e:
        raise SampleDataRefused(
            f"เปิดไฟล์ Excel ไม่ได้ (ถูกล็อกอยู่): {e}\n"
            "     มักเกิดตอนเปิดไฟล์ค้างใน Excel หรือ OneDrive กำลัง sync\n"
            "     ยังไม่แตะเว็บของเดิม — จะลองใหม่รอบหน้า") from e
    except Exception as e:
        raise SampleDataRefused(
            f"อ่านไฟล์ Excel ไม่สำเร็จ: {type(e).__name__}: {e}\n"
            "     ยังไม่แตะเว็บของเดิม") from e
    if not years:
        raise SampleDataRefused(
            "อ่านไฟล์ได้แต่ไม่พบข้อมูลปีใด ๆ เลย — น่าจะผิดปกติ ยังไม่แตะเว็บของเดิม")
    return path, kind


def pick_landing(years):
    """เดือนที่จะให้เปิดเป็นหน้าแรก

    ใช้ "เดือนของเรือลำถัดไปที่ยังไม่ถึงวัน" ไม่ใช่เดือนปัจจุบันตรง ๆ
    พอเรือลำสุดท้ายของเดือนผ่านไปแล้ว หน้าแรกจะข้ามไปเดือนถัดไปให้เอง
    ถ้าไม่เหลือเรือข้างหน้าแล้ว ค่อยกลับไปใช้เดือนปัจจุบัน
    """
    import app as _app
    import core
    now = datetime.now()
    today = now.date()
    excel = _app.find_excel()

    if excel is not None:
        for y in [y for y in sorted(years) if y >= now.year]:
            try:
                vessels, _ = core.load_vessels(excel, _app.DEFAULT_SHEET, y, range(1, 13))
            except Exception:
                break                      # อ่านไม่ได้ ใช้วิธีสำรองด้านล่าง
            for v in vessels:              # เรียงตาม (เดือน, วัน) มาแล้ว
                try:
                    d = date(y, v["month"], v["day"])
                except ValueError:
                    continue
                if d >= today:
                    return y, v["month"]

    # ไม่มีเรือข้างหน้าเลย -> เดือนปัจจุบัน (หรือปีล่าสุดที่ build ไว้)
    if now.year in years:
        return now.year, now.month
    newest = max(years)
    return newest, (now.month if newest >= now.year else 12)


def build(years):
    assert_real_data()
    now = datetime.now()

    # ── render ทุกหน้าเก็บในหน่วยความจำก่อน ยังไม่แตะไฟล์เดิมเลย ──
    # ถ้ามีหน้าไหนพัง จะ raise ออกไปโดยที่เว็บของเดิมยังอยู่ครบ
    # (เคยพลาดมาแล้ว: ลบไฟล์เก่าก่อน render พอ render พังเลยเหลือโฟลเดอร์ว่าง)
    rendered = {}
    with app.test_client() as c:
        for year in years:
            for month in range(1, 13):
                r = c.get(f"/?month={month}&year={year}")
                if r.status_code != 200:
                    raise SampleDataRefused(
                        f"หน้า {year}-{month:02d} ตอบ HTTP {r.status_code} — ยกเลิกทั้งชุด")
                html = r.get_data(as_text=True)
                if '<div class="error">' in html:
                    raise SampleDataRefused(
                        f"หน้า {year}-{month:02d} มี error อยู่ในหน้า — ยกเลิกทั้งชุด\n"
                        "     ไม่ปล่อยหน้าที่มี error ขึ้นเว็บสาธารณะ")
                rendered[f"{year}-{month:02d}.html"] = to_static(html, years)
            print(f"  {year}: สร้าง 12 เดือน")

    # ── ถึงตรงนี้แปลว่าทุกหน้าดีหมดแล้ว ค่อยเขียนทับของเดิม ──
    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("*.html"):
        old.unlink()
    shutil.copytree(BASE_DIR / "static", DIST / "static", dirs_exist_ok=True)

    pages = 0
    for name, html in rendered.items():
        (DIST / name).write_text(html, encoding="utf-8")
        pages += 1

    ly, lm = pick_landing(years)
    landing = f"{ly}-{lm:02d}.html"
    print(f"  หน้าแรกชี้ไปที่: {landing}")
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


def default_years():
    """ไม่ระบุปีมา -> ทุกปีที่มีข้อมูลใน Excel + ปีปัจจุบันเสมอ

    - รวมปีเก่าไว้ด้วย ไม่งั้นหน้าเว็บของปีที่ผ่านมาจะหายไปตอน push
    - บวกปีปัจจุบันเข้าไปเสมอ เผื่อกรณีขึ้นปีใหม่แล้วยังไม่ได้ลงข้อมูลปีนั้น
      จะได้มีหน้าปฏิทินเปล่าของปีปัจจุบันให้เปิดดู ไม่ใช่ค้างอยู่ที่ปีเก่า
    """
    import app as _app
    import core
    now_year = datetime.now().year
    excel = _app.find_excel()
    if excel is None:
        return [now_year]
    try:
        years = core.available_years(excel, _app.DEFAULT_SHEET)
    except Exception:
        years = []
    return sorted(set(years) | {now_year})


if __name__ == "__main__":
    try:
        path, _ = assert_real_data()
    except SampleDataRefused as e:
        print()
        print(f"  [X] {e}")
        sys.exit(2)
    print(f"ข้อมูลจาก: {path}")
    args = [int(a) for a in sys.argv[1:]] or default_years()
    print(f"สร้างเว็บ static ปี {', '.join(map(str, args))} ...")
    build(args)
