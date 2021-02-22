from kombu.serialization import register
from celery import Celery
from bs4 import BeautifulSoup
from collections import deque
from pathlib import Path
import celeryconfig
import requests
import json

app = Celery('tasks')
app.config_from_object('celeryconfig')


register('mongodb', lambda obj: obj, lambda obj: obj,
         content_type='application/mongo-json', content_encoding='utf-8')

# GOAL:
# press start -> starts redis, mongodb, celery workers, adds a url to the space
# celery worker pops off url, crawls it, adds to mongodb, and adds neighbors to queue


@app.task
def crawl(url):
  r = requests.get(url)
  base = r.url

  text = r.content
  print(base, text[0: min(len(text), 20)])
  print()

  # parse doc here
  soup = BeautifulSoup(text, 'html.parser')

  # add friends to arraylist
  for link in soup.find_all('a'):
    # get full url
    currUrl = link.get('href')
    if currUrl is None:
      continue
    if not (currUrl[0:7] == "http://" or currUrl[0:8] == "https://"):  # if url is relative
      currUrl = base + currUrl
    crawl.delay(currUrl)

  return {"url": base, "doc": str(text)}
