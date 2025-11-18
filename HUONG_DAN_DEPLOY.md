# HƯỚNG DẪN DEPLOY PADDLEOCR API LÊN RAILWAY

## 🎯 MỤC TIÊU
Deploy PaddleOCR API lên Railway.app để Apps Script có thể gọi qua internet

## ✅ CHUẨN BỊ
- 3 file: main.py, requirements.txt, railway.json (đã có sẵn)
- Tài khoản GitHub (miễn phí)
- Tài khoản Railway (miễn phí - 500 giờ/tháng)

---

## 📋 CÁCH 1: DEPLOY QUA GITHUB (KHUYẾN NGHỊ - ĐỠN GIẢN NHẤT)

### Bước 1: Tạo GitHub Repository

1. **Vào GitHub:** https://github.com/new
2. **Điền thông tin:**
   - Repository name: `paddleocr-api`
   - Description: `PaddleOCR API for Vietnamese documents`
   - Chọn: **Public** hoặc **Private** (cả 2 đều OK)
   - ✅ Tick: "Add a README file"
3. **Click:** Create repository

### Bước 2: Upload 3 Files

**CÁCH ĐƠN GIẢN (Qua Web UI):**

1. Trong repo vừa tạo, click **Add file** → **Upload files**
2. Kéo thả hoặc chọn 3 file:
   - `main.py`
   - `requirements.txt`
   - `railway.json`
3. Kéo xuống dưới, click **Commit changes**

✅ Xong phần GitHub!

### Bước 3: Deploy trên Railway

1. **Vào Railway:** https://railway.app
2. **Login/Sign up:**
   - Click "Login"
   - Chọn "Login with GitHub"
   - Authorize Railway
3. **Tạo Project mới:**
   - Click **"New Project"**
   - Chọn **"Deploy from GitHub repo"**
   - Chọn repo `paddleocr-api` vừa tạo
   - Click **"Deploy Now"**

### Bước 4: Đợi Deploy (5-10 phút)

Railway sẽ tự động:
- ✅ Đọc requirements.txt
- ✅ Cài đặt Python packages
- ✅ Build PaddleOCR
- ✅ Start server

**Xem Log:**
- Click vào deployment
- Tab **"Deployments"**
- Click vào deployment mới nhất
- Xem logs để biết tiến độ

**Dấu hiệu thành công:**
```
🚀 Server đã khởi động!
🌍 PORT: 8000
```

### Bước 5: Lấy Public URL

1. Click vào **Settings** (biểu tượng ⚙️)
2. Kéo xuống **"Networking"**
3. Click **"Generate Domain"**
4. Copy URL (VD: `paddleocr-api-production.up.railway.app`)

✅ **XONG! API đã LIVE!**

---

## 🧪 TEST API

### Test 1: Health Check

Mở trình duyệt, vào:
```
https://your-app.railway.app/health
```

Kết quả mong đợi:
```json
{
  "status": "healthy",
  "ocr_engine": "PaddleOCR",
  "language": "Vietnamese",
  "ready": true
}
```

### Test 2: API Info

Vào:
```
https://your-app.railway.app/
```

Sẽ thấy thông tin đầy đủ về API.

---

## 📋 CÁCH 2: DEPLOY QUA RAILWAY CLI (KHÔNG CẦN GITHUB)

### Bước 1: Cài Railway CLI

**Windows:**
```bash
# Dùng PowerShell
iwr https://railway.app/install.ps1 | iex
```

**Mac/Linux:**
```bash
# Dùng Terminal
curl -fsSL https://railway.app/install.sh | sh
```

### Bước 2: Login

```bash
railway login
```

Trình duyệt sẽ mở, đăng nhập Railway.

### Bước 3: Deploy

```bash
# Vào folder chứa 3 files
cd path/to/paddleocr-api

# Khởi tạo project
railway init

# Deploy
railway up
```

### Bước 4: Lấy URL

```bash
railway domain
```

---

## 🔧 SAU KHI DEPLOY

### Kiểm tra Logs

**Qua Web:**
- Vào Railway Dashboard
- Click project
- Tab "Deployments"
- Xem logs real-time

**Qua CLI:**
```bash
railway logs
```

### Cập nhật Code

**Cách 1 (GitHub):**
1. Edit file trên GitHub
2. Commit changes
3. Railway tự động deploy lại

**Cách 2 (CLI):**
```bash
# Sau khi sửa code
railway up
```

---

## ⚠️ XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: "Build failed"

**Nguyên nhân:** Railway không tìm thấy requirements.txt

**Giải pháp:**
- Đảm bảo 3 files ở root folder
- Không để trong subfolder

### Lỗi 2: "Application failed to respond"

**Nguyên nhân:** Server chưa start xong

**Giải pháp:**
- Đợi thêm 2-3 phút (PaddleOCR cần thời gian load)
- Check logs xem có lỗi không

### Lỗi 3: "Out of memory"

**Nguyên nhân:** Railway free tier giới hạn RAM

**Giải pháp:**
- Giảm `rec_batch_num` trong main.py (từ 6 xuống 4)
- Hoặc upgrade Railway plan ($5/month)

### Lỗi 4: "Service Unavailable"

**Nguyên nhân:** Vượt 500 giờ/tháng

**Giải pháp:**
- Check usage: Railway Dashboard → Usage
- Đợi đến đầu tháng mới
- Hoặc upgrade plan

---

## 💰 RAILWAY PRICING

**Free Tier:**
- ✅ 500 giờ/tháng (~16 giờ/ngày)
- ✅ $5 credit/tháng
- ✅ 512MB RAM
- ✅ Public repository

**Starter Plan: $5/month**
- ✅ Unlimited giờ
- ✅ $5 credit
- ✅ 8GB RAM
- ✅ Private repo support

**Ước tính cho 100K files:**
- Mỗi file: ~2-3 giây
- Tổng: ~100 giờ
- → **Hoàn toàn FREE!**

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Check logs trên Railway
2. Xem phần "Xử lý lỗi" ở trên
3. Hỏi lại tôi với error message cụ thể

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] Tạo GitHub repo
- [ ] Upload 3 files
- [ ] Deploy Railway
- [ ] Lấy được URL
- [ ] Test health check thành công
- [ ] Copy URL để tích hợp Apps Script

**URL của bạn:**
```
https://_____________________.railway.app
```

Sau khi có URL này, chúng ta sẽ tích hợp vào Apps Script!
