from flask import Flask, request
from flask import render_template
from celery_app import crawl, test

app = Flask(__name__)


@app.route('/')
def home_page():
  return render_template('crawlpage.html')


@app.route('/crawlurl', methods=['POST'])
def crawl_url():
  if request and request.form["url"] != "":
    url = request.form["url"]
    crawl.delay(url)
  return "OK"


if __name__ == '__main__':
  app.run(host='0.0.0.0')
