FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for WeasyPrint + PostgreSQL binary
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    libgobject-2.0-0 \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu-core \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8080"]