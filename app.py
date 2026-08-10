"""
LNG Vessel Schedule — Web App
รัน:  python app.py   แล้วเปิด  http://localhost:5000
เครื่องอื่นในวงเดียวกันเปิดได้ที่  http://<IP เครื่องนี้>:5000
"""
import io
import os
import secrets
from calendar import month_name, Calendar
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (Flask, render_template, request, redirect,
                   url_for, send_file, flash, session, abort)

import core

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ไฟล์ Excel หลัก — ตอนรันบนเครื่องตัวเองจะอ่าน path นี้ให้อัตโนมัติ
# ตอน deploy ขึ้น server ตั้ง env var DEFAULT_EXCEL หรือปล่อยว่างแล้วอัปโหลดผ่าน /admin
DEFAULT_EXCEL = Path(os.environ.get(
    "DEFAULT_EXCEL",
    r"C:\Users\lng660008\OneDrive - PTT GROUP\Work plan for LO.xlsm"))
DEFAULT_SHEET = os.environ.get("DEFAULT_SHEET", "Sheet1")
ALLOWED_EXT = {".xlsx", ".xlsm", ".xls"}

# รหัสผ่านหน้า admin (สำหรับอัปโหลด Excel)
# ลำดับ: env var ADMIN_PASSWORD -> ไฟล์ .admin_password -> สุ่มใหม่แล้วเก็บไว้
# ไฟล์ .admin_password อยู่ใน .gitignore จึงไม่หลุดขึ้น GitHub
PASSWORD_FILE = BASE_DIR / ".admin_password"


def _load_admin_password():
    env = os.environ.get("ADMIN_PASSWORD")
    if env:
        return env
    if PASSWORD_FILE.exists():
        pw = PASSWORD_FILE.read_text(encoding="utf-8").strip()
        if pw:
            return pw
    pw = secrets.token_urlsafe(9)
    PASSWORD_FILE.write_text(pw, encoding="utf-8")
    return pw


ADMIN_PASSWORD = _load_admin_password()
MAX_UPLOAD_MB = 25

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lng-vessel-schedule")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def admin_required(view):
    """หน้าไหนใส่ decorator นี้ ต้อง login ก่อนถึงเข้าได้"""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def find_excel():
    """ลำดับการหาไฟล์ Excel: อัปโหลดล่าสุด -> ไฟล์หลัก -> ไฟล์ตัวอย่าง
    (ไฟล์ตัวอย่างมีไว้ให้ dev รันได้เลยโดยไม่ต้องมีข้อมูลจริง
     สร้างด้วย: python make_sample_excel.py)"""
    uploads = sorted(UPLOAD_DIR.glob("latest.*"))
    if uploads:
        return uploads[0]
    if DEFAULT_EXCEL.exists():
        return DEFAULT_EXCEL
    sample = BASE_DIR / "sample_work_plan.xlsx"
    if sample.exists():
        return sample
    return None


_years_cache: dict = {}


def year_choices(excel, sheet):
    """ปีที่มีข้อมูลจริงในไฟล์ + ปีปัจจุบันเสมอ
    (cache ไว้ตาม mtime ของไฟล์ จะได้ไม่ต้องเปิด workbook ใหม่ทุก request)"""
    now_year = datetime.now().year
    if excel is None:
        return [now_year]
    key = (str(excel), excel.stat().st_mtime, sheet)
    if key not in _years_cache:
        try:
            years = core.available_years(excel, sheet)
        except Exception:
            years = []
        _years_cache.clear()
        _years_cache[key] = sorted(set(years) | {now_year})
    return _years_cache[key]


def get_period():
    now = datetime.now()
    try: month = int(request.args.get("month", now.month))
    except ValueError: month = now.month
    try: year = int(request.args.get("year", now.year))
    except ValueError: year = now.year
    month = min(max(month, 1), 12)
    sheet = (request.args.get("sheet") or DEFAULT_SHEET).strip() or DEFAULT_SHEET
    return month, year, sheet


@app.route("/")
def index():
    month, year, sheet = get_period()
    excel = find_excel()
    ytd_vessels, skipped_all, error = [], [], None
    if excel is None:
        error = ("ยังไม่มีไฟล์ตารางเรือ — ผู้ดูแลระบบกรุณาอัปโหลดที่หน้า /admin")
    else:
        try:
            # อ่านรอบเดียวตั้งแต่ Jan ถึงเดือนที่เลือก แล้วแยกใช้ทั้งรายเดือนและสะสม
            ytd_vessels, skipped_all = core.load_vessels(excel, sheet, year, range(1, month + 1))
        except Exception as e:
            error = str(e)

    vessels = [v for v in ytd_vessels if v["month"] == month]
    skipped = [name for m, name in skipped_all if m == month]

    def summarize(vs):
        shippers, lt, spot = {}, 0, 0
        for v in vs:
            shippers[v["shipper"]] = shippers.get(v["shipper"], 0) + 1
            nom = v["nom"].strip().lower()
            if nom == "lt":     lt += 1
            elif nom == "spot": spot += 1
        # เรียง shipper ตามจำนวนมาก→น้อย
        shippers = dict(sorted(shippers.items(), key=lambda kv: -kv[1]))
        return shippers, lt, spot

    vbd = {}
    for v in ytd_vessels:
        v["logo"] = core.resolve_logo_key(v["shipper"])
    for v in vessels:
        vbd.setdefault(v["day"], []).append(v)

    shipper_counts, lt_count, spot_count = summarize(vessels)
    ytd_shippers, ytd_lt, ytd_spot = summarize(ytd_vessels)
    all_shippers = set(shipper_counts) | set(ytd_shippers)
    shipper_logos = {s: core.resolve_logo_key(s) for s in all_shippers}
    weeks = Calendar(firstweekday=6).monthdayscalendar(year, month)

    file_mtime = None
    if excel is not None:
        file_mtime = datetime.fromtimestamp(excel.stat().st_mtime).strftime("%d/%m/%Y %H:%M")

    return render_template(
        "index.html",
        month=month, year=year, sheet=sheet,
        month_label=month_name[month].upper(),
        month_names=[month_name[i] for i in range(1, 13)],
        years=year_choices(excel, sheet),
        weeks=weeks, vbd=vbd,
        vessels=vessels, skipped=skipped, error=error,
        shipper_counts=shipper_counts, shipper_logos=shipper_logos,
        lt_count=lt_count, spot_count=spot_count,
        ytd_total=len(ytd_vessels), ytd_shippers=ytd_shippers,
        ytd_lt=ytd_lt, ytd_spot=ytd_spot,
        ytd_label=("%s – %s %d" % (month_name[1][:3].upper(),
                                   month_name[month][:3].upper(), year)),
        excel_name=excel.name if excel else None,
        file_mtime=file_mtime,
        today=datetime.now(),
    )


# ─── ADMIN: อัปเดตไฟล์ Excel ────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(request.args.get("next") or url_for("admin"))
        flash("รหัสผ่านไม่ถูกต้อง")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin():
    excel = find_excel()
    info = None
    if excel is not None:
        st = excel.stat()
        info = {
            "name": excel.name,
            "size_kb": round(st.st_size / 1024),
            "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%d/%m/%Y %H:%M"),
            "is_upload": excel.parent == UPLOAD_DIR,
        }
    return render_template("admin.html", info=info, today=datetime.now())


@app.route("/upload", methods=["POST"])
@admin_required
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        flash("ยังไม่ได้เลือกไฟล์")
        return redirect(url_for("admin"))
    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        flash(f"ไฟล์ต้องเป็น Excel ({', '.join(sorted(ALLOWED_EXT))})")
        return redirect(url_for("admin"))
    # เขียนไฟล์ใหม่ก่อน ค่อยลบของเก่า เพื่อไม่ให้เว็บว่างเปล่าถ้าอัปโหลดพัง
    tmp = UPLOAD_DIR / f"_incoming{ext}"
    f.save(tmp)
    try:
        core.load_vessels(tmp, DEFAULT_SHEET, datetime.now().year, [1])
    except Exception as e:
        tmp.unlink(missing_ok=True)
        flash(f"ไฟล์นี้อ่านไม่ได้ ({e}) — ยังใช้ไฟล์เดิมอยู่")
        return redirect(url_for("admin"))
    for old in UPLOAD_DIR.glob("latest.*"):
        old.unlink()
    tmp.rename(UPLOAD_DIR / f"latest{ext}")
    flash(f"อัปเดตไฟล์ {f.filename} เรียบร้อย — เว็บแสดงข้อมูลใหม่แล้ว")
    return redirect(url_for("admin"))


@app.route("/reset-upload", methods=["POST"])
@admin_required
def reset_upload():
    for old in UPLOAD_DIR.glob("latest.*"):
        old.unlink()
    flash("ลบไฟล์ที่อัปโหลดแล้ว กลับไปใช้ไฟล์หลัก")
    return redirect(url_for("admin"))


@app.route("/png")
def download_png():
    month, year, sheet = get_period()
    excel = find_excel()
    if excel is None:
        return "ยังไม่มีไฟล์ Excel", 404
    vessels, _ = core.load_vessels(excel, sheet, year, [month])
    upd = datetime.now().strftime("%d/%m/%y")
    img = core.build_calendar(vessels, month, year, upd)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=True,
                     download_name=f"{month_name[month]}_{year}.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
