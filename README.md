# LNG Vessel Schedule — Web

เว็บไซต์แสดงตารางเรือ LNG (แปลงมาจาก `Ship_Schedule.py` เวอร์ชัน tkinter)

## วิธีรัน

### แบบใช้งานจริง (แนะนำ) — ให้เพื่อนร่วมงานเข้าได้

1. **ครั้งแรกครั้งเดียว**: คลิกขวา `SETUP_ADMIN.bat` → **Run as administrator**
   (เปิด firewall port 5000 + ตั้งให้เว็บเปิดเองทุกครั้งที่ login)
2. ดับเบิลคลิก `START_SERVER.bat` (หรือรอ auto-start ตอน login)
3. ส่งลิงก์นี้ให้เพื่อน: **http://ITNB690297:5000**

> ใช้ **ชื่อเครื่อง** (`ITNB690297`) ไม่ใช่ IP — เพราะ IP เป็น DHCP เปลี่ยนทุกครั้งที่ต่อเน็ตใหม่
>
> เครื่องนี้ต้อง **เปิดอยู่ + ต่อเน็ตบริษัท** เพื่อนถึงจะเข้าได้ (ปิดเครื่อง/sleep = เว็บดับ)

### แบบพัฒนา/ทดสอบ

```
pip install -r requirements.txt
python app.py
```

แล้วเปิด **http://localhost:5000**

## การใช้งาน

- เว็บจะอ่านไฟล์ `Work plan for LO.xlsm` (path ตั้งไว้ใน `app.py` ตัวแปร `DEFAULT_EXCEL`) ให้อัตโนมัติ
- หรืออัปโหลดไฟล์ Excel อื่นได้จากหน้าเว็บ (ไฟล์จะถูกเก็บไว้ใน `uploads/`)
- เลือกเดือน / ปี / ชื่อ sheet ได้จากแถบด้านบน
- ปุ่ม **ดาวน์โหลด PNG** สร้างรูปปฏิทินแบบเดียวกับโปรแกรมเดิมทุกอย่าง
- **แถบสรุปรายเดือน** — จำนวนเรือทั้งเดือน, LT/Spot, และจำนวนเรือแยกตาม Shipper
- **ตารางรายละเอียดเรือ** ใต้ปฏิทิน — วันที่, Berth, Shipper, ประเภท (LT/Spot),
  Unloading Quantity, Density, LM (เรือที่ยังไม่เข้าเทียบท่าจะแสดง "–")
- หน้าเว็บรีเฟรชตัวเองทุก 5 นาที — แก้ไฟล์ Excel แล้วตารางบนเว็บอัปเดตตามเอง

## หน้าผู้ดูแล (อัปเดตไฟล์ Excel)

เข้าที่ `/admin` เช่น `http://ITNB690297:5000/admin`
รหัสผ่านเริ่มต้น: `lng2026` (เปลี่ยนได้ผ่าน env var `ADMIN_PASSWORD`)

ใช้อัปโหลดไฟล์ Excel ใหม่โดยไม่ต้องเข้าถึงตัวเครื่อง server
หน้าเว็บสาธารณะไม่มีปุ่มอัปโหลด/ดาวน์โหลดให้กดเลย

## เอาขึ้นอินเทอร์เน็ตให้บุคคลภายนอกดู

ดู **[DEPLOY.md](DEPLOY.md)** — ใช้ GitHub Pages (ฟรีถาวร ไม่ต้องดูแล)

สั้น ๆ คือ: `python build_static.py 2026` จะสร้างเว็บแบบไฟล์ HTML ล้วนลงโฟลเดอร์
`docs/` แล้ว push ขึ้น GitHub — ได้ลิงก์ `https://<บัญชี>.github.io/<repo>/`

เวลาตารางเปลี่ยน แค่ดับเบิลคลิก **`UPDATE_WEB.bat`** จบ (build + commit + push ให้เอง)

### อัปเดตอัตโนมัติ (ไม่ต้องกดอะไรเลย)

ดับเบิลคลิก **`SETUP_AUTO_UPDATE.bat`** ครั้งเดียว จากนั้นแค่แก้ไฟล์ Excel แล้วเซฟ
ภายใน ~2 นาทีเว็บจะอัปเดตเอง

- ตัวเฝ้าไฟล์ทำงานเงียบ ๆ เบื้องหลัง (ไม่มีหน้าต่างโผล่) และเปิดเองทุกครั้งที่ login
- ดูว่าทำอะไรไปบ้าง: เปิดไฟล์ `watch.log`
- เช็คสถานะ: `python setup_auto.py status`
- ปิดระบบ: `STOP_AUTO_UPDATE.bat`

ใช้ Startup folder ไม่ใช่ Task Scheduler เพราะเครื่องบริษัทบล็อกการสร้าง scheduled task

## ถ้าอยากให้เข้าได้ตลอด 24 ชม. (ไม่ผูกกับเครื่องนี้)

เครื่องนี้เป็นโน้ตบุ๊ก — ปิด/หลับ/ถอดจากเน็ตบริษัทเมื่อไหร่ เว็บก็ดับ
ถ้าจะให้ใช้งานจริงจังต้องขอ IT ตั้ง server ให้:

1. ขอ VM / server ในบริษัท (Windows หรือ Linux ก็ได้)
2. ก๊อปโฟลเดอร์นี้ไปวาง แล้วรัน `python serve.py`
3. ย้ายไฟล์ Excel ไปไว้บน **shared drive** ที่ server อ่านได้
   แล้วแก้ path ในตัวแปร `DEFAULT_EXCEL` ใน `app.py`
4. ขอ DNS name จาก IT เช่น `http://lng-schedule.pttgrp.corp`

**หมายเหตุเรื่องข้อมูล**: ตารางนี้มีข้อมูลภายใน (shipper, ปริมาณ, ชื่อ Loading Master)
ถ้าจะเอาขึ้น cloud/อินเทอร์เน็ตสาธารณะ ต้องใส่ระบบ login ก่อน
และควรคุยกับ IT Security ของบริษัทก่อนเสมอ

## สำหรับ Developer (เริ่มพัฒนาต่อ)

ไม่ต้องขอไฟล์อะไรเพิ่ม — โค้ดทั้งหมดอยู่ใน repo นี้ และมีตัวสร้างข้อมูลตัวอย่างให้

```bash
git clone https://github.com/chytq/lmpt1-ship-schedule.git
cd lmpt1-ship-schedule
pip install -r requirements.txt
python make_sample_excel.py     # สร้างข้อมูลสมมติ ~150 ลำ 2 ปี
python app.py                   # เปิด http://localhost:5000
```

**ไฟล์ Excel จริงไม่ได้อยู่ใน repo** (กันไว้ใน `.gitignore`) ถ้าจะทดสอบกับข้อมูลจริง
ให้ขอไฟล์ `Work plan for LO.xlsm` แล้วชี้ path ด้วย environment variable:

```bash
set DEFAULT_EXCEL=C:\path\to\Work plan for LO.xlsm
python app.py
```

ถ้าไม่ตั้ง `DEFAULT_EXCEL` ระบบจะไล่หาไฟล์ตามลำดับ:
`uploads/latest.*` → path ใน `DEFAULT_EXCEL` → `sample_work_plan.xlsx`

### ตัวแปรที่ตั้งผ่าน environment ได้

| ตัวแปร | ค่าเริ่มต้น | ใช้ทำอะไร |
|---|---|---|
| `DEFAULT_EXCEL` | path บนเครื่องเจ้าของ | ตำแหน่งไฟล์ Excel |
| `DEFAULT_SHEET` | `Sheet1` | ชื่อ sheet ที่อ่าน |
| `ADMIN_PASSWORD` | สุ่มเก็บใน `.admin_password` | รหัสผ่านหน้า `/admin` |
| `SECRET_KEY` | ค่าคงที่ | Flask session key |

### สถาปัตยกรรม

```
Excel (.xlsm)
   └─ core.py          อ่าน + parse ข้อมูล และวาดรูป PNG ด้วย Pillow
        └─ app.py      Flask: หน้าเว็บ / หน้า admin / endpoint ดาวน์โหลด PNG
             ├─ serve.py         รันแบบ production (waitress)
             └─ build_static.py  render หน้าเว็บเป็น HTML ล้วนลง docs/
                  └─ update_web.py   build + git commit + push
                       └─ watch_excel.py  เฝ้าไฟล์แล้วเรียก update_web เอง
```

จุดที่ควรรู้:
- `core.py` ไม่ผูกกับ Flask เลย เรียกใช้แยกได้ (`load_vessels`, `build_calendar`)
- คอลัมน์ที่อ่านจาก Excel ประกาศไว้ที่ `COL` ใน `core.py`
- ไฟล์ `.bat` เป็น **ASCII ล้วนโดยตั้งใจ** — ถ้าใส่ภาษาไทย cmd.exe จะ parse คำสั่งเพี้ยน
  ข้อความภาษาไทยทั้งหมดจึงอยู่ในฝั่ง Python

## โครงสร้าง

- `build_static.py` — สร้างเว็บ static ลง `docs/` สำหรับ GitHub Pages
- `update_web.py` — build + commit + push (logic อยู่ใน Python เพราะ cmd.exe
  อ่านไฟล์ .bat ที่มีภาษาไทยแล้วคำสั่งเพี้ยน ไฟล์ .bat จึงเป็น ASCII ล้วนทุกไฟล์)
- `UPDATE_WEB.bat` — ดับเบิลคลิกเพื่ออัปเดตเว็บบน GitHub Pages
- `watch_excel.py` — เฝ้าไฟล์ Excel แล้วอัปเดตเว็บให้เองเมื่อไฟล์เปลี่ยน
- `setup_auto.py` / `SETUP_AUTO_UPDATE.bat` / `STOP_AUTO_UPDATE.bat` — เปิด/ปิดระบบอัตโนมัติ
- `serve.py` — production server (waitress) สำหรับรันบนเครื่อง/server
- `START_SERVER.bat` — ดับเบิลคลิกเพื่อเปิดเว็บบนเครื่องนี้
- `SETUP_ADMIN.bat` — ตั้งค่า firewall + auto-start (รันครั้งเดียว, ต้อง admin)
- `app.py` — Flask web server
- `core.py` — logic อ่าน Excel + วาด PNG (ยกมาจากโปรแกรมเดิม)
- `templates/index.html` — หน้าเว็บปฏิทิน
- `static/img/` — รูปเรือและโลโก้ shipper (ดึงออกมาจาก base64 ในไฟล์เดิม)
