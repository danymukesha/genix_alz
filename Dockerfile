# genix_alz/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "src/cli.py", "--input", "data/sample_patient.json", "--output", "/output/report.pdf"]
