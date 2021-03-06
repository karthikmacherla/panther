from flask import Flask
from celery_app import crawl, test

app = Flask(__name__)


@app.route('/')
def hello_world():
  return 'Hello, World!'


@app.route('/test')
def test_fun():
  test.delay()
  return "OK"


if __name__ == '__main__':
  app.run(host='0.0.0.0')
