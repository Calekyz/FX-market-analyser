FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies (pure Python, no system deps needed)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
