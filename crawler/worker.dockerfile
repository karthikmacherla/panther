FROM python:3.9.1
WORKDIR /app
COPY requirements/worker-requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .