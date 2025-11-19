from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io
import os
import uvicorn
import cv2
import base64
import tempfile

app = FastAPI()

# Initialize PaddleOCR
ocr = None

def get_ocr():
    """Lazy load OCR model"""
    global ocr
    if ocr is None:
        print("🚀 Initializing PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='vi')
        print("✅ PaddleOCR initialized successfully")
    return ocr

def process_image_array(img_array):
    """Process numpy array with OCR"""
    try:
        print(f"📐 Array shape: {img_array.shape}, dtype: {img_array.dtype}")
        
        # Convert RGB to BGR if needed
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Get OCR engine
        ocr_engine = get_ocr()
        
        # Perform OCR
        print("🔍 Performing OCR...")
        result = ocr_engine.ocr(img_array, cls=True)
        print(f"✅ OCR completed")
        
        # Extract text
        text_lines = []
        full_text = ""
        
        if result and result[0]:
            print(f"📝 Found {len(result[0])} text lines")
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1])
                    text_lines.append(text)
            
            full_text = "\n".join(text_lines)
            print(f"✅ Extracted {len(full_text)} characters")
        else:
            print("⚠️ No text found in image")
        
        return {
            "success": True,
            "text": full_text,
            "lines": text_lines,
            "line_count": len(text_lines)
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ OCR Error: {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

# Model for base64 request
class Base64ImageRequest(BaseModel):
    image: str  # base64 encoded image

@app.post("/ocr/base64")
async def process_ocr_base64(request: Base64ImageRequest):
    """Process base64 encoded image with extensive debugging"""
    print("="*60)
    print("📥 BASE64 REQUEST RECEIVED")
    print("="*60)
    
    base64_str = request.image
    print(f"📊 Base64 length: {len(base64_str)}")
    print(f"🔍 First 50 chars: {base64_str[:50]}")
    print(f"🔍 Last 50 chars: {base64_str[-50:]}")
    
    # Check for data URL prefix
    if base64_str.startswith('data:'):
        print("⚠️ Found data URL prefix, stripping...")
        if ',' in base64_str:
            base64_str = base64_str.split(',', 1)[1]
            print(f"✅ Stripped to length: {len(base64_str)}")
    
    try:
        # Decode base64
        print("🔓 Decoding base64...")
        try:
            image_data = base64.b64decode(base64_str)
            print(f"✅ Decoded size: {len(image_data)} bytes")
            print(f"🔍 First 10 bytes: {image_data[:10]}")
        except Exception as e:
            print(f"❌ Base64 decode error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid base64: {str(e)}")
        
        # Save to temp file for debugging
        temp_file = None
        try:
            print("💾 Saving to temp file for debugging...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(image_data)
                temp_file = tmp.name
            print(f"✅ Saved to: {temp_file}")
            
            # Try to open with PIL from file
            print("🖼️ Opening image from temp file...")
            image = Image.open(temp_file)
            print(f"✅ Image opened: format={image.format}, size={image.size}, mode={image.mode}")
            
        except Exception as e:
            print(f"❌ File-based open failed: {str(e)}")
            
            # Try direct BytesIO
            print("🔄 Trying direct BytesIO...")
            try:
                image = Image.open(io.BytesIO(image_data))
                print(f"✅ BytesIO open succeeded: format={image.format}, size={image.size}, mode={image.mode}")
            except Exception as e2:
                print(f"❌ BytesIO also failed: {str(e2)}")
                raise HTTPException(status_code=422, detail=f"Invalid image data: {str(e2)}")
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            print(f"🔄 Converting from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        print(f"✅ Numpy array created: shape={img_array.shape}, dtype={img_array.dtype}")
        
        return process_image_array(img_array)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error: {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process uploaded image file"""
    print("="*60)
    print("📥 MULTIPART REQUEST RECEIVED")
    print("="*60)
    print(f"📄 Filename: {file.filename}")
    print(f"📝 Content-Type: {file.content_type}")
    
    try:
        # Read file contents
        contents = await file.read()
        print(f"📊 File size: {len(contents)} bytes")
        print(f"🔍 First 10 bytes: {contents[:10]}")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file received")
        
        # Try to open with PIL
        try:
            image = Image.open(io.BytesIO(contents))
            print(f"✅ Image opened: format={image.format}, size={image.size}, mode={image.mode}")
        except Exception as e:
            print(f"❌ PIL open failed: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Invalid image: {str(e)}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            print(f"🔄 Converting from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        print(f"✅ Numpy array created: shape={img_array.shape}, dtype={img_array.dtype}")
        
        return process_image_array(img_array)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error: {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }

@app.get("/")
async def root():
    return {
        "message": "PaddleOCR API v1.3 - Vietnamese OCR (Debug Mode)",
        "status": "running",
        "endpoints": {
            "/ocr": "POST - Upload image file (multipart/form-data)",
            "/ocr/base64": "POST - Send base64 encoded image",
            "/health": "GET - Health check",
            "/test": "GET - Test endpoint"
        },
        "note": "Check Railway logs for detailed debugging info"
    }

@app.get("/health")
async def health():
    try:
        ocr_engine = get_ocr()
        return {
            "status": "healthy",
            "ocr_loaded": ocr_engine is not None,
            "python_version": os.sys.version
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/test")
async def test():
    return {
        "status": "ok",
        "message": "Server is running properly",
        "ocr_status": "loaded" if ocr is not None else "not_loaded",
        "pil_version": Image.__version__ if hasattr(Image, '__version__') else "unknown"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("="*60)
    print(f"🚀 Starting PaddleOCR API Server on port {port}")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=port)
