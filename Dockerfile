FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY app.py ./
COPY templates ./templates
COPY static ./static

# Create directory for database (can be mounted as volume)
RUN mkdir -p /data

ENV FLASK_ENV=production
ENV DATABASE_PATH=/data/bills.db

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
