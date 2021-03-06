from flask import Flask
from celery_app import crawl, test
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongodb:27017/crawler"
mongo = PyMongo(app)


@app.route('/')
def hello_world():
  return 'Hello, World!'


@app.route('/test')
def test_fun():
  test.delay()
  return "OK"


if __name__ == '__main__':
  app.run(host='0.0.0.0')
