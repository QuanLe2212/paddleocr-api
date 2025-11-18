/**
 * TÍCH HỢP PADDLEOCR VÀO APPS SCRIPT
 * 
 * Sau khi deploy Railway xong, làm theo các bước sau:
 * 
 * BƯỚC 1: Copy URL từ Railway (VD: https://paddleocr-api-production.up.railway.app)
 * BƯỚC 2: Thêm/sửa code trong script hiện tại như bên dưới
 */

/* ===== BƯỚC 1: THÊM VÀO PHẦN CONFIG ===== */

var CONFIG = {
  // ... code CONFIG hiện tại ...
  
  // THÊM DÒNG NÀY:
  PADDLEOCR_API_URL: 'https://your-app.railway.app',  // ← Thay bằng URL thật từ Railway
  USE_PADDLEOCR: true,  // ← true = dùng PaddleOCR, false = dùng Gemini/Google
  PADDLEOCR_TIMEOUT: 30000,  // 30 giây timeout
  
  // Ưu tiên OCR engines (thử từ trái sang phải)
  OCR_PRIORITY: ['paddleocr', 'gemini', 'google']
};

/* ===== BƯỚC 2: THÊM HÀM MỚI - PADDLEOCR ===== */

/**
 * OCR PDF bằng PaddleOCR API
 */
function extractPdfWithPaddleOCR(file) {
  var startTime = new Date().getTime();
  
  try {
    Logger.log('  Đang gọi PaddleOCR API...');
    
    // Convert PDF sang base64
    var pdfBlob = file.getBlob();
    var base64Pdf = Utilities.base64Encode(pdfBlob.getBytes());
    
    // Gọi API
    var url = CONFIG.PADDLEOCR_API_URL + '/ocr-base64';
    
    var response = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ 
        pdf_base64: base64Pdf 
      }),
      muteHttpExceptions: true,
      timeout: CONFIG.PADDLEOCR_TIMEOUT
    });
    
    var responseCode = response.getResponseCode();
    
    // Kiểm tra HTTP status
    if (responseCode !== 200) {
      throw new Error('PaddleOCR API trả về HTTP ' + responseCode);
    }
    
    // Parse response
    var data = JSON.parse(response.getContentText());
    
    // Kiểm tra success
    if (!data.success || !data.text) {
      throw new Error('PaddleOCR response invalid: ' + JSON.stringify(data));
    }
    
    var elapsed = new Date().getTime() - startTime;
    
    Logger.log('  ✅ PaddleOCR OK: ' + data.text.length + ' chars (' + (elapsed/1000).toFixed(1) + 's)');
    Logger.log('  Pages: ' + data.pages_processed + '/' + data.total_pages);
    
    return data.text;
    
  } catch (e) {
    var elapsed = new Date().getTime() - startTime;
    Logger.log('  ❌ PaddleOCR lỗi (' + (elapsed/1000).toFixed(1) + 's): ' + e.message);
    throw e;
  }
}

/* ===== BƯỚC 3: SỬA HÀM extractFileContent ===== */

/**
 * TÌM HÀM extractFileContent TRONG SCRIPT CŨ
 * SỬA PHẦN XỬ LÝ PDF NHƯ SAU:
 */

function extractFileContent(driveLink, fileIndex) {
  var fileId = extractFileId(driveLink);
  if (!fileId) return { status: 'Loi', note: 'Link khong hop le' };
  
  try {
    var file = DriveApp.getFileById(fileId);
    var mime = file.getMimeType();
    var name = file.getName();
    var size = formatFileSize(file.getSize());
    
    if (CONFIG.PDF_ONLY && mime !== 'application/pdf') {
      return { name: name, mimeType: mime, size: size, status: 'Bo qua', note: 'Khong phai PDF' };
    }
    
    if (file.getSize() > CONFIG.MAX_FILE_SIZE) {
      return { name: name, size: size, status: 'Bo qua', note: 'File qua lon' };
    }
    
    var content = '';
    var ocrEngine = '';
    
    if (mime === 'application/pdf') {
      
      // ========== PHẦN MỚI: THỬ THEO THỨ TỰ ƯU TIÊN ==========
      
      var engines = CONFIG.OCR_PRIORITY || ['gemini', 'google'];
      var lastError = '';
      
      for (var i = 0; i < engines.length; i++) {
        var engine = engines[i];
        
        try {
          Logger.log('  Thử engine: ' + engine);
          
          // 1. PaddleOCR (ưu tiên cao nhất nếu bật)
          if (engine === 'paddleocr' && CONFIG.USE_PADDLEOCR) {
            content = extractPdfWithPaddleOCR(file);
            ocrEngine = 'paddleocr';
            break;  // Thành công -> dừng
          }
          
          // 2. Gemini Vision (nếu còn quota)
          else if (engine === 'gemini' && canUseGemini() && !getAllKeysExhausted()) {
            content = extractPdfWithGeminiVision(file);
            ocrEngine = 'gemini';
            break;
          }
          
          // 3. Google OCR (fallback cuối cùng)
          else if (engine === 'google') {
            content = extractPdfWithGoogleOCR(file);
            ocrEngine = 'google';
            break;
          }
          
        } catch (e) {
          lastError = e.message;
          Logger.log('  → ' + engine + ' thất bại: ' + e.message);
          
          // Nếu còn engine khác, thử tiếp
          if (i < engines.length - 1) {
            Logger.log('  → Chuyển sang engine tiếp theo...');
            continue;
          } else {
            // Hết engine rồi -> throw error
            throw new Error('Tất cả OCR engines đều thất bại. Last: ' + lastError);
          }
        }
      }
      
      // ========== HẾT PHẦN MỚI ==========
    }
    
    content = content.substring(0, CONFIG.MAX_CHARS_PER_FILE);
    
    return { 
      name: name, 
      mimeType: mime, 
      size: size, 
      content: content, 
      summary: content.substring(0, 500), 
      status: 'Thanh cong',
      ocrEngine: ocrEngine
    };
    
  } catch (e) {
    return { status: 'Loi', note: e.message };
  }
}

/* ===== BƯỚC 4: THÊM HÀM TEST ===== */

/**
 * Test PaddleOCR API
 * Chạy hàm này để kiểm tra kết nối
 */
function testPaddleOCRAPI() {
  try {
    Logger.log('==========================================');
    Logger.log('TEST PADDLEOCR API');
    Logger.log('==========================================');
    
    // Test 1: Health check
    Logger.log('\n1. Health Check...');
    var healthUrl = CONFIG.PADDLEOCR_API_URL + '/health';
    var healthResponse = UrlFetchApp.fetch(healthUrl);
    var healthData = JSON.parse(healthResponse.getContentText());
    
    Logger.log('✅ Health: ' + JSON.stringify(healthData));
    
    // Test 2: Test với file thật
    Logger.log('\n2. Test với file PDF...');
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = getSourceSheet(ss);
    var data = sheet.getDataRange().getValues();
    var linkCol = findLinkColumn(data[0]);
    
    // Tìm file PDF đầu tiên
    for (var i = 1; i < data.length; i++) {
      var link = data[i][linkCol];
      if (link && isValidDriveLink(link)) {
        Logger.log('Đang test file: ' + link);
        
        var fileId = extractFileId(link);
        var file = DriveApp.getFileById(fileId);
        
        Logger.log('File: ' + file.getName());
        Logger.log('Size: ' + formatFileSize(file.getSize()));
        
        // Gọi PaddleOCR
        var ocrText = extractPdfWithPaddleOCR(file);
        
        Logger.log('✅ OCR thành công!');
        Logger.log('Text length: ' + ocrText.length + ' chars');
        Logger.log('Preview: ' + ocrText.substring(0, 200) + '...');
        
        // Test trích yếu
        var trichYeu = detectTrichYeu(ocrText);
        Logger.log('\nTrích yếu:');
        Logger.log('- Ký hiệu: ' + (trichYeu.kyHieu || 'N/A'));
        Logger.log('- Trích yếu: ' + (trichYeu.trichYeu || 'N/A'));
        Logger.log('- Ngày: ' + (trichYeu.ngayThang || 'N/A'));
        
        Logger.log('\n==========================================');
        Logger.log('TEST HOÀN THÀNH - PaddleOCR HOẠT ĐỘNG TỐT!');
        Logger.log('==========================================');
        
        // Hiển thị kết quả
        var ui = SpreadsheetApp.getUi();
        ui.alert(
          'TEST THÀNH CÔNG! ✅',
          'PaddleOCR API hoạt động tốt!\n\n' +
          'File: ' + file.getName() + '\n' +
          'Text: ' + ocrText.length + ' ký tự\n\n' +
          'Trích yếu:\n' +
          '• Ký hiệu: ' + (trichYeu.kyHieu || 'N/A') + '\n' +
          '• Trích yếu: ' + (trichYeu.trichYeu || 'N/A') + '\n' +
          '• Ngày: ' + (trichYeu.ngayThang || 'N/A'),
          ui.ButtonSet.OK
        );
        
        return;
      }
    }
    
    throw new Error('Không tìm thấy file PDF để test');
    
  } catch (e) {
    Logger.log('❌ TEST THẤT BẠI: ' + e.message);
    
    var ui = SpreadsheetApp.getUi();
    ui.alert(
      'TEST THẤT BẠI ❌',
      'Lỗi: ' + e.message + '\n\n' +
      'Kiểm tra:\n' +
      '1. URL PaddleOCR có đúng không?\n' +
      '2. Railway app có đang chạy không?\n' +
      '3. Xem Logs để biết chi tiết',
      ui.ButtonSet.OK
    );
  }
}

/* ===== BƯỚC 5: THÊM VÀO MENU ===== */

/**
 * TÌM HÀM setupMenu() TRONG SCRIPT CŨ
 * THÊM MENU ITEM MỚI:
 */

function setupMenu() {
  var ui = SpreadsheetApp.getUi();
  if (!ui) return;

  ui.createMenu('Trich Yeu File')
    .addItem('BAT DAU trich yeu', 'startExtraction')
    .addItem('TIEP TUC tu lan truoc', 'continueExtraction')
    .addSeparator()
    .addItem('CHE DO TU DONG (100K files)', 'startAutoMode')
    .addItem('DUNG tu dong', 'stopAutoMode')
    .addItem('Xem Dashboard tien do', 'openProgressDashboard')
    .addSeparator()
    
    // ========== THÊM DÒNG NÀY ==========
    .addItem('🔬 TEST PaddleOCR API', 'testPaddleOCRAPI')
    // ====================================
    
    .addItem('Setup reset tu dong (chay 1 lan)', 'setupDailyReset')
    .addItem('Kiem tra quota & batch', 'checkAllKeysQuota')
    .addItem('Xem Smart Batch stats', 'showSmartBatchStats')
    .addSeparator()
    .addItem('Test 1 file', 'testFirstFile')
    .addSeparator()
    .addItem('Reset tien do', 'resetProgressMenu')
    .addToUi();
}

/* ===== BƯỚC 6: CẬP NHẬT SMART_BATCH (TÙY CHỌN) ===== */

/**
 * Nếu muốn tracking PaddleOCR stats, thêm vào SMART_BATCH:
 */

var SMART_BATCH = {
  gemini: {
    batchSize: 15,
    avgTime: 15000,
    name: 'Gemini Vision'
  },
  google: {
    batchSize: 2,
    avgTime: 45000,
    name: 'Google OCR'
  },
  
  // ========== THÊM DÒNG NÀY ==========
  paddleocr: {
    batchSize: 20,      // PaddleOCR nhanh hơn
    avgTime: 3000,      // ~3s/file
    name: 'PaddleOCR'
  },
  // ====================================
  
  currentEngine: 'gemini',
  filesProcessed: 0
};

/* ===== HOÀN THÀNH! ===== */

/**
 * TÓM TẮT CÁC THAY ĐỔI:
 * 
 * 1. ✅ Thêm CONFIG.PADDLEOCR_API_URL
 * 2. ✅ Thêm hàm extractPdfWithPaddleOCR()
 * 3. ✅ Sửa hàm extractFileContent() - thêm fallback logic
 * 4. ✅ Thêm hàm testPaddleOCRAPI()
 * 5. ✅ Thêm menu item "TEST PaddleOCR API"
 * 6. ✅ (Tùy chọn) Thêm paddleocr vào SMART_BATCH
 * 
 * SAU KHI SỬA XONG:
 * - Reload spreadsheet
 * - Chạy menu "🔬 TEST PaddleOCR API"
 * - Nếu thành công -> bắt đầu xử lý batch!
 */
