FROM python:3.9.1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5555

# CMD [ "celery", "flower -A celery_app.celery --broker=amqp://guest:guest@rabbitmq:5672/  --address=0.0.0.0 --port=5555"]