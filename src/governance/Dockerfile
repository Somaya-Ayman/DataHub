FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY governance.py .

# Run as non-root user for security
RUN useradd -m appuser
USER appuser

ENTRYPOINT ["python", "governance.py"]