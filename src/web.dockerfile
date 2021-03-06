FROM python:3.9.1
WORKDIR /app
COPY requirements/web-requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# EXPOSE 5000
CMD [ "python", "./app.py" ]