from fastapi import FastAPI, File, UploadFile
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io
import os

app = FastAPI()

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='vi')

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image and return OCR results"""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        img_array = np.array(image)
        
        # Perform OCR
        result = ocr.ocr(img_array, cls=True)
        
        # Extract text
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                text_lines.append(line[1][0])
        
        return {
            "success": True,
            "text": "\n".join(text_lines),
            "lines": text_lines
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/")
async def root():
    return {"message": "PaddleOCR API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# For Railway.app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
