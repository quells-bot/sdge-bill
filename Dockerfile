# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# Stage 2: Production image
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY backend/app.py ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create directory for database (can be mounted as volume)
RUN mkdir -p /data

ENV FLASK_ENV=production
ENV DATABASE_PATH=/data/bills.db

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
