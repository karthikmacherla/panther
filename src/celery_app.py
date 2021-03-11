from kombu.serialization import register
from celery import Celery
from bs4 import BeautifulSoup
from collections import deque
from pathlib import Path
import celeryconfig
import requests
import json


celery = Celery('tasks')
celery.config_from_object('celeryconfig')

register('mongodb', lambda obj: obj, lambda obj: obj,
         content_type='application/mongo-json', content_encoding='utf-8')


@celery.task
def test():
  return 5


@celery.task
def crawl(url):
  r = requests.get(url)
  base = r.url

  text = r.content
  print(base, text[0: min(len(text), 20)])
  print()
  parse.delay(base, str(text))


@celery.task
def parse(base, text):
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

  return {"url": base, "doc": text}
