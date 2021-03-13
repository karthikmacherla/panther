# from kombu.serialization import register
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
import time


mongo_client = pymongo.MongoClient("mongodb://mongodb:27017")
mongo_db = mongo_client["crawler"]
doc_store = mongo_db["documents"]
robot_store = mongo_db["robots"]
robot_store.create_index("domain", unique=True)
doc_store.create_index("url", unique=True)


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
    print("Fetching doc for: ", url)
    fetch_doc.delay(url, str(robot["_id"]))
  elif delay_crawl(robot):
    print("Delaying crawl for: ", url)
    pop_from_queue.delay(url)
  else:
    print("Not crawling: ", url)


def get_robot(domain):
  """
    Get's robots.txt for a url if it exists, parses content, and saves to db
    - params = domain name
  """
  res = robot_store.find_one({"domain": domain})
  if res is not None:
    return res

  robot_url = "http://" + domain + "/robots.txt"
  r = requests.get(robot_url)
  status = r.status_code
  rob_text = r.content

  allowed_links = {}
  disallowed_links = {}
  crawl_delays = {}
  user_agents = []

  curr_user_agents = []
  lastaccessedtime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
  if status == 200:
    for line in rob_text.splitlines():
      line = str(line, 'utf-8')
      if line.startswith("#"):
        continue
      elif line.strip() == "":
        curr_user_agents = []
      elif line.startswith("User-agent:"):
        curr_agent = line.split(": ")[1]
        curr_user_agents.append(curr_agent)
        user_agents.append(curr_agent)
      elif line.startswith("Disallow:"):
        for agent in curr_user_agents:
          disallowed_links[agent] = disallowed_links.get(agent, [])
          disallowed_links[agent].append(line.split(": ")[1])
      elif line.startswith("Allow:"):
        for agent in curr_user_agents:
          allowed_links[agent] = allowed_links.get(agent, [])
          allowed_links[agent].append(line.split(": ")[1])
      elif line.startswith("Crawl-delay:"):
        for agent in curr_user_agents:
          crawl_delays[agent] = line.split(": ")[1]
  robot = {
      "allowed_links": allowed_links,
      "disallowed_links": disallowed_links,
      "crawl_delays": crawl_delays,
      "last_accessed_time": lastaccessedtime,
      "domain": domain
  }
  _id = robot_store.insert(robot)
  robot["_id"] = _id
  # create invariant that None == just fetched
  del robot["last_accessed_time"]
  return robot


def robot_allows_crawl(robot, url):
  """
    checks if url is disallowed or allowed to be crawled from robot constraints
  """
  domain = urlparse(url).netloc
  urlpath = url.split(domain)[1]

  for allowed in robot["allowed_links"].get("*", []):
    if urlpath.startswith(allowed):
      return True

  for disallowed in robot["disallowed_links"].get("*", []):
    if urlpath.startswith(disallowed):
      return False

  # ignoring crawl-delay for now vs. supposed to use last-accessed-time.
  return True


def delay_crawl(robot):
  """
    Checks if robot requires crawler to delay itself to stay compliant
  """
  delay = robot["crawl_delay"].get("*")
  last_time = robot.get("last_accessed_time")
  if delay is not None and last_time is not None:
    curr = dt.datetime.now()
    then = dt.datetime.strptime(last_time, "%a, %d %b %Y %H:%M:%S GMT")
    return (curr - dt.timedelta(seconds=delay)) < then
  return False


@celery.task
def fetch_doc(url, rob_id):
  """
    Fetches the document from the url or from the db.
    Checks if the url has been modified and if not, fetches from db.

    Also updates the robots.txt for domain if url was accessed so future links wait
  """
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

  r = requests.get(url, headers=headers)
  status = r.status_code
  # we're in the clear/it's been modified
  new_html_page = status == 200 or (status < 400 and status != 304) and (
      "text/html" in r.headers["content-type"])
  if new_html_page:
    get_req = requests.get(url)
    if get_req.status_code != 200:
      return
    text = str(get_req.content)
    should_save = True

  # update the robots.txt's last accessed
  new_last_accessed = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
  robot_store.update({"_id": rob_id}, {
                     "$set": {"last_accessed_time": new_last_accessed}})
  # consider implementing content-hashing
  parse.delay(url, text)

  if should_save:
    save_doc(url, text)


@celery.task
def parse(base, text):
  """
    Extracts all links and adds them to frontier queue
  """
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


@celery.task
def save_doc(url, text):
  """
    Saves document to MongoDB doc collection
    - Objects of the form: 
      { doc: text, url: url, last_accessed: gmt-http-string }
  """
  curr_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
  doc_store.update_one({"url": url}, {
      "$set": {"doc": text, "last_accessed": curr_time}
  }, upsert=True)
