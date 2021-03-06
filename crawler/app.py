from flask import Flask, request
from flask import render_template
from celery_app import crawl, test
# from flask_pymongo import PyMongo


app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://mongodb:27017/crawler"
# mongo = PyMongo(app)


@app.route('/')
def hello_world():
  return render_template('crawlpage.html')


@app.route('/crawlurl', methods=['POST'])
def test_fun():
  if request and request.form["url"] != "":
    url = request.form["url"]
    crawl.delay(url)
  return "OK"


if __name__ == '__main__':
  app.run(host='0.0.0.0')
