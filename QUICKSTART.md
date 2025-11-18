# 🚀 QUICKSTART - PADDLEOCR API

## 📦 BẠN CÓ GÌ?

Folder `paddleocr-api` chứa:
- ✅ `main.py` - FastAPI server
- ✅ `requirements.txt` - Dependencies
- ✅ `railway.json` - Deploy config
- ✅ `README.md` - Project info
- ✅ `.gitignore` - Git ignore rules
- ✅ `HUONG_DAN_DEPLOY.md` - Hướng dẫn deploy chi tiết
- ✅ `TICH_HOP_APPS_SCRIPT.js` - Code tích hợp Apps Script

---

## ⚡ 5 BƯỚC NHANH

### 1️⃣ TẠO GITHUB REPO (2 phút)

```
1. Vào: https://github.com/new
2. Tên repo: paddleocr-api
3. Chọn Public
4. ✅ Tick "Add README"
5. Click "Create repository"
```

### 2️⃣ UPLOAD CODE (1 phút)

```
1. Click "Add file" → "Upload files"
2. Kéo thả TẤT CẢ file trong folder paddleocr-api
3. Click "Commit changes"
```

### 3️⃣ DEPLOY RAILWAY (5 phút)

```
1. Vào: https://railway.app
2. Login with GitHub
3. Click "New Project"
4. Chọn "Deploy from GitHub repo"
5. Chọn repo "paddleocr-api"
6. Click "Deploy Now"
7. Đợi 5 phút (xem logs)
```

### 4️⃣ LẤY URL (30 giây)

```
1. Vào Settings (⚙️)
2. Networking → "Generate Domain"
3. Copy URL: https://xxxx.railway.app
```

### 5️⃣ TÍCH HỢP APPS SCRIPT (3 phút)

```
1. Mở file TICH_HOP_APPS_SCRIPT.js
2. Copy các đoạn code cần thiết
3. Paste vào Apps Script
4. Sửa CONFIG.PADDLEOCR_API_URL = "URL từ Railway"
5. Chạy menu "🔬 TEST PaddleOCR API"
```

---

## ✅ KIỂM TRA THÀNH CÔNG

### Test 1: Mở trình duyệt

```
Vào: https://your-app.railway.app/health
```

**Kết quả:**
```json
{
  "status": "healthy",
  "ocr_engine": "PaddleOCR",
  "language": "Vietnamese",
  "ready": true
}
```

### Test 2: Apps Script

```
1. Reload spreadsheet
2. Menu "Trich Yeu File" → "🔬 TEST PaddleOCR API"
3. Thấy popup "TEST THÀNH CÔNG ✅"
```

---

## 🎯 SAU KHI SETUP XONG

### Xử lý 1 file:
```
Menu → Test 1 file
```

### Xử lý batch nhỏ:
```
Menu → BAT DAU trich yeu
```

### Xử lý 100K files:
```
Menu → CHE DO TU DONG (100K files)
```

---

## 📊 ƯU TIÊN OCR ENGINES

Hệ thống sẽ tự động thử theo thứ tự:

**1. PaddleOCR** (nếu bật)
   - Độ chính xác: 96-98%
   - Tốc độ: ~3s/file
   - Miễn phí: ✅

**2. Gemini Vision** (nếu còn quota)
   - Độ chính xác: 95-97%
   - Tốc độ: ~15s/file
   - Quota: 1500/key/ngày

**3. Google OCR** (fallback)
   - Độ chính xác: 90-95%
   - Tốc độ: ~45s/file
   - Không giới hạn: ✅

---

## 💰 CHI PHÍ

**Railway Free Tier:**
- 500 giờ/tháng
- Đủ cho 100K files

**Tổng chi phí: $0** ✅

---

## ⚠️ XỬ LÝ LỖI NHANH

| Lỗi | Giải pháp |
|-----|-----------|
| Build failed | Đảm bảo 3 file ở root, không trong subfolder |
| App failed | Đợi thêm 2-3 phút, PaddleOCR cần load |
| 500 Error | Check Railway logs |
| Quota exceeded | Đợi đầu tháng mới hoặc upgrade |

---

## 📞 CẦN TRỢ GIÚP?

1. ❌ **Deploy lỗi?** → Xem `HUONG_DAN_DEPLOY.md`
2. ❌ **Apps Script lỗi?** → Xem `TICH_HOP_APPS_SCRIPT.js`
3. ❌ **Vẫn không được?** → Gửi error message cụ thể

---

## 🎉 CHECKLIST HOÀN THÀNH

- [ ] GitHub repo created
- [ ] Files uploaded
- [ ] Railway deployed
- [ ] URL generated
- [ ] Health check OK
- [ ] Apps Script integrated
- [ ] Test 1 file OK
- [ ] Ready to process 100K files!

**CHÚC MỪNG! BẠN ĐÃ SẴN SÀNG XỬ LÝ 100K FILES! 🚀**
