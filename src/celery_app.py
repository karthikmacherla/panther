from kombu.serialization import register
from celery import Celery
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
from pathlib import Path
import datetime as dt
import celeryconfig
import requests
import json
import pymongo

mongo_client = pymongo.MongoClient("mongodb://mongodb:27017")
mongo_db = mongo_client["crawler"]
doc_store = mongo_db["documents"]
robot_store = mongo_db["robots"]


celery = Celery('tasks')
celery.config_from_object('celeryconfig')


@celery.task
def test():
  return 5


@celery.task
def pop_from_queue(url):
  check_robots.delay(url)


@celery.task
def check_robots(url):
  # extract site domain
  domain = urlparse(url).netloc

  # try getting robots.txt from database
  robot = get_robot(domain)
  if robot_allows_crawl(robot, url):
    fetch_doc.delay(url)


def get_robot(domain):
  res = robot_store.find_one({"domain": domain})
  if res is not None:
    return res

  robot_url = domain + "/robots.txt"
  r = requests.get(robot_url)
  status = r.status_code
  rob_text = r.content

  allowed_links = {}
  disallowed_links = {}
  crawl_delays = {}
  user_agents = []

  curr_user_agents = []
  lastaccessedtime = dt.datetime.now()
  if status == 200:
    for line in rob_text.splitlines():
      if line.startswith("#"):
        continue
      elif line.strip() == "":
        curr_user_agents = []
      elif line.startswith("User-agent:"):
        curr_agent = line.split(":")[1]
        curr_user_agents.append(curr_agent)
        user_agents.append(curr_agent)
      elif line.startswith("Disallow:"):
        for agent in curr_user_agents:
          disallowed_links[agent] = line.split(":")[1]
      elif line.startswith("Allow:"):
        for agent in curr_user_agents:
          allowed_links[agent] = line.split(":")[1]
      elif line.startswith("Crawl-delay:"):
        for agent in curr_user_agents:
          crawl_delays[agent] = line.split(":")[1]
  robot = {
      "allowed_links": allowed_links,
      "disallowed_links": disallowed_links,
      "crawl_delays": crawl_delays,
      "last_accessed_time": lastaccessedtime,
      "domain": domain
  }
  robot_store.insert(robot)
  # create invariant that None == just fetched
  del robot["last_access_time"]
  return robot


def robot_allows_crawl(robot, url):
  urlpath = urlparse(url).path
  for disallowed in robot["disallowed_links"]:
    if urlpath.startswith(disallowed):
      return False
  # ignoring crawl-delay for now vs. supposed to use last-accessed-time.
  return True


@celery.task
def fetch_doc(url):
  # check if you've seen this url before: how? query docdb for url
  query = doc_store.find({"url": url}).limit(1)
  last_accessed = None
  text = None
  should_save = False
  if query.count() == 1:
    doc = query.next()
    last_accessed = doc["last_accessed"]
    text = doc["doc"]

  # make a head req
  headers = {}
  if last_accessed is not None:
    headers["If-Modified-Since"] = last_accessed

  r = requests.head(url, headers=headers)

  # we're in the clear/it's been modified
  if r.status_code == 200:
    get_req = requests.get(url)
    if get_req.status_code != 200:
      return
    text = str(get_req.content)
    should_save = True

  # update the robots.txt
  parse.delay(url, text, should_save)


@celery.task
def parse(base, text):
  # potentially do content hash here?
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
    pop_from_queue.delay(currUrl)
  save_doc.delay(base, text)


@celery.task
def save_doc(url, text):
  doc_store.insert_one({"url": url, "doc": text})
