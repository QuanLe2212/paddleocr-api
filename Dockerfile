# Use Python 3.12 slim based on Debian Bookworm (stable)
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies (FIX libGL error)
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

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Run the application via python main.py (handles PORT dynamically)
CMD ["python", "main.py"]
