# Use Python 3.12 slim based on Debian Bookworm (stable) để tránh lỗi package
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies (FIX libGL error - dùng libgl1 thay vì libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port (Railway sẽ set PORT env variable)
EXPOSE 8000

# Run qua python main.py để handle PORT động (từ code của bạn)
CMD ["python", "main.py"]
