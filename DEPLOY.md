# วิธีเอาเว็บขึ้นอินเทอร์เน็ต (ให้บุคคลภายนอกเข้าดูได้)

แนะนำ **PythonAnywhere** เพราะฟรี ไม่ต้องใช้ git ไม่ต้องใช้บัตรเครดิต
และไฟล์ที่อัปโหลดไม่หายเวลา server restart (ต่างจาก Render/Railway ที่ไฟล์หาย)

---

## ขั้นตอน (ครั้งแรกครั้งเดียว ~20 นาที)

### 1. เตรียมไฟล์

บีบอัดโฟลเดอร์ `ShipScheduleWeb` เป็น zip
(ไม่ต้องใส่โฟลเดอร์ `uploads` กับ `__pycache__` และ **ไม่ต้องใส่ไฟล์ Excel**)

### 2. สมัคร PythonAnywhere

ไปที่ https://www.pythonanywhere.com → **Pricing & signup** → **Create a Beginner account** (ฟรี)

จะได้ URL ประจำตัวเป็น `https://<username>.pythonanywhere.com`

### 3. อัปโหลดโค้ด

- แท็บ **Files** → ปุ่ม **Upload a file** → เลือกไฟล์ zip
- แท็บ **Consoles** → **Bash** แล้วพิมพ์:

```bash
unzip ShipScheduleWeb.zip
cd ShipScheduleWeb
pip3 install --user -r requirements.txt
```

### 4. สร้าง Web App

- แท็บ **Web** → **Add a new web app**
- เลือก **Manual configuration** (ห้ามเลือก Flask template)
- เลือก Python เวอร์ชันล่าสุดที่มี

จากนั้นในหน้า Web ตั้งค่า:

| ช่อง | ใส่ค่า |
|---|---|
| Source code | `/home/<username>/ShipScheduleWeb` |
| Working directory | `/home/<username>/ShipScheduleWeb` |
| WSGI configuration file | กดเข้าไปแก้ (ดูขั้นที่ 5) |

**Static files** — กด Add ทีละแถว:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/ShipScheduleWeb/static/` |

### 5. แก้ไฟล์ WSGI

กดลิงก์ **WSGI configuration file** ลบของเดิมทิ้งทั้งหมด แล้วใส่:

```python
import sys, os

path = '/home/<username>/ShipScheduleWeb'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DEFAULT_EXCEL']  = '/nonexistent'
os.environ['ADMIN_PASSWORD'] = 'ตั้งรหัสผ่านของคุณตรงนี้'
os.environ['SECRET_KEY']     = 'ใส่ข้อความสุ่มยาวๆ อะไรก็ได้'

from app import app as application
```

> เปลี่ยน `<username>` เป็นชื่อบัญชีจริง และ **ตั้งรหัสผ่านใหม่** อย่าใช้ค่า default

### 6. เปิดใช้งาน

กดปุ่มเขียว **Reload** ที่หน้า Web แล้วเปิด `https://<username>.pythonanywhere.com`

ครั้งแรกจะขึ้นว่ายังไม่มีไฟล์ตารางเรือ — ไปที่
`https://<username>.pythonanywhere.com/admin` ใส่รหัสผ่าน แล้วอัปโหลดไฟล์ Excel

---

## การใช้งานประจำวัน

**คนทั่วไป** → เปิด `https://<username>.pythonanywhere.com` ดูอย่างเดียว ไม่มีปุ่มอะไรให้กดพลาด

**คุณ (ผู้ดูแล)** → พอแก้ไฟล์ Excel เสร็จ:
1. เข้า `https://<username>.pythonanywhere.com/admin`
2. เลือกไฟล์ `Work plan for LO.xlsm` → กดอัปโหลด
3. เว็บอัปเดตทันที

ระบบจะลองอ่านไฟล์ก่อนเสมอ ถ้าไฟล์เสียหรือผิดรูปแบบจะไม่ทับของเดิม

---

## ข้อควรรู้

- **บัญชีฟรีต้องกดต่ออายุทุก 3 เดือน** — PythonAnywhere จะส่งอีเมลเตือน
  เข้าไปกดปุ่ม "Run until 3 months from today" ที่แท็บ Web (ถ้าลืมกด เว็บจะหยุด)
- ถ้าอยากได้โดเมนของตัวเอง เช่น `lngschedule.com` ต้องอัปเกรดเป็นแพ็กเกจเสียเงิน ($5/เดือน)
- อยากเปลี่ยนรหัสผ่าน admin — แก้ `ADMIN_PASSWORD` ในไฟล์ WSGI แล้วกด Reload

---

## ทางเลือกอื่น

| บริการ | ข้อดี | ข้อเสีย |
|---|---|---|
| **PythonAnywhere** | ฟรี ไฟล์ไม่หาย ไม่ต้องใช้ git | ต้องต่ออายุทุก 3 เดือน |
| Render (free) | deploy ผ่าน git อัตโนมัติ | ไฟล์ที่อัปโหลด**หาย**ทุกครั้งที่ restart + หลับหลังไม่มีคนเข้า 15 นาที |
| Server บริษัท | เสถียรที่สุด อ่าน Excel จาก shared drive ได้เลย | ต้องขอ IT |

ถ้าเลือก Render ต้องเอาไฟล์ Excel ใส่ใน git repo แทนการอัปโหลด
(มี `Procfile` เตรียมไว้ให้แล้ว)
