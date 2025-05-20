FROM python:3.11

WORKDIR /app

RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ENVIRONMENT=production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
