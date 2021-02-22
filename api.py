from flask import Flask
from tasks.crawler import crawl

app = Flask(__name__)


@app.route('/')
def hello_world():
  return 'Hello, World!'


# flask
# pymongo
# celery


# celery
# pymongo
