# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---- Final stage ----
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed packages from the builder stage, not the build tools
COPY --from=builder /root/.local /root/.local
COPY app.py .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app.py"]
