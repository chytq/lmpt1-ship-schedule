# วิธีเอาเว็บขึ้น GitHub Pages

ได้ลิงก์แบบ `https://<ชื่อบัญชี>.github.io/<ชื่อ-repo>/`
เหมือนที่ https://lmpt2marine-dev.github.io/application-vessel-schedule-dashboard/

**ฟรีถาวร ไม่มีวันหมดอายุ ไม่ต้องต่ออายุ ไม่มีวันหลับ** เพราะเป็นไฟล์ HTML ล้วน
ไม่ต้องมี server รัน — เครื่องคุณปิดเว็บก็ยังอยู่

โฟลเดอร์นี้ตั้ง git ไว้ให้แล้ว และ commit แรกเสร็จเรียบร้อย เหลือแค่ต่อกับ GitHub

---

## ตั้งค่าครั้งแรก (~10 นาที)

### 1. สร้าง repo บน GitHub

เข้า https://github.com/new

| ช่อง | ใส่ |
|---|---|
| Repository name | `vessel-schedule-dashboard` (หรือชื่ออื่นที่ชอบ) |
| Public / Private | **Public** (บัญชีฟรีต้อง public ถึงจะใช้ Pages ได้) |
| Add README / .gitignore / license | **ไม่ต้องติ๊กอะไรเลย** |

กด **Create repository**

### 2. เชื่อม repo แล้ว push

เปิด Git Bash หรือ PowerShell ในโฟลเดอร์นี้ แล้วรัน (เปลี่ยน `<ชื่อบัญชี>` กับ `<ชื่อ-repo>`):

```bash
git remote add origin https://github.com/<ชื่อบัญชี>/<ชื่อ-repo>.git
git push -u origin main
```

ครั้งแรกจะเด้ง browser ให้ login GitHub — กด Authorize ให้เรียบร้อย

### 3. เปิด GitHub Pages

ในหน้า repo บน GitHub:

**Settings** → เมนูซ้าย **Pages** → ตั้งค่า:

| ช่อง | เลือก |
|---|---|
| Source | Deploy from a branch |
| Branch | `main` |
| Folder | **`/docs`** ← สำคัญ |

กด **Save** แล้วรอ 1-2 นาที

### 4. เสร็จ

เปิด `https://<ชื่อบัญชี>.github.io/<ชื่อ-repo>/` ได้เลย
ส่งลิงก์นี้ให้ใครก็ได้ ทั้งในและนอกบริษัท

---

## การใช้งานประจำ — อัปเดตตารางเรือ

หลังแก้ไฟล์ Excel เสร็จ **ดับเบิลคลิก `UPDATE_WEB.bat`** จบ

สคริปต์จะสร้างหน้าเว็บใหม่ commit แล้ว push ให้อัตโนมัติ
เว็บอัปเดตภายใน 1-2 นาที

อยากสร้างหลายปี:

```
UPDATE_WEB.bat 2025 2026 2027
```

ถ้าอยากทำเองทีละขั้น:

```bash
python build_static.py 2026
git add -A
git commit -m "update schedule"
git push
```

---

## เรื่องที่ต้องรู้

**repo เป็น public** — ใครก็เห็นทั้งโค้ดและข้อมูลตารางเรือ
(ไฟล์ Excel ต้นฉบับ **ไม่ได้** ขึ้นไปด้วย มีแต่หน้าเว็บที่ render แล้ว)
ถ้าอยากให้ repo เป็น private แต่ยังใช้ Pages ได้ ต้องใช้บัญชีแบบเสียเงิน
(GitHub Pro $4/เดือน หรือใช้บัญชี Organization ของบริษัท)

**ข้อมูลบนเว็บนิ่ง** — ไม่ได้อ่าน Excel สดแบบตอนรันบนเครื่อง
ต้องกด `UPDATE_WEB.bat` ทุกครั้งที่ตารางเปลี่ยน ถึงจะอัปเดต

**สร้างล่วงหน้าทุกเดือน** — ปุ่มเลือกเดือน/ปีบนเว็บใช้ได้ปกติ
เพราะ build ไว้ครบทั้ง 12 เดือนของแต่ละปีที่ระบุ

---

## ทางเลือกอื่นที่ไม่ใช่ GitHub Pages

| วิธี | ค่าใช้จ่าย | ข้อมูลอัปเดตเอง | ข้อสังเกต |
|---|---|---|---|
| **GitHub Pages** (แนะนำ) | ฟรี | ไม่ (กดปุ่มอัปเดต) | ไม่มีวันหลับ ไม่ต้องดูแล |
| Netlify Drop | ฟรี | ไม่ | ลากโฟลเดอร์ `docs` ไปวางที่ app.netlify.com/drop ได้ลิงก์ทันที ไม่ต้องสมัคร |
| Cloudflare Pages | ฟรี | ไม่ | เหมือน GitHub Pages ต่อกับ repo เดียวกันได้ เร็วกว่าในไทย |
| PythonAnywhere | ฟรี | ใช่ (อัปโหลดผ่าน /admin) | ต้องกดต่ออายุทุก 3 เดือน |
| Server บริษัท | ขอ IT | ใช่ (อ่าน shared drive สด) | เสถียรสุด อ่าน Excel ตรงจาก network drive ได้ |
| Render free | ฟรี | ไม่แน่นอน | ไฟล์อัปโหลดหายตอน restart + หลับหลังไม่มีคนเข้า 15 นาที |

ถ้าอยากได้แบบ **อ่าน Excel สดโดยไม่ต้องกดอัปเดต** ต้องใช้ตัวที่รัน Python ได้
(PythonAnywhere หรือ server บริษัท) — ดูหัวข้อ "หน้าผู้ดูแล" ใน README.md
