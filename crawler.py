import requests
from bs4 import BeautifulSoup
from collections import deque
from pathlib import Path

# Old version:
# Single threaded crawler


def main():
  # Path("./docs").mkdir(parents=True, exist_ok=True)

  urls = deque()
  urls.append('http://google.com/')

  crawl_count = 0
  while len(urls) >= 0 and crawl_count < 10:
    crawl_count += 1
    curr = urls.popleft()
    print("Crawling: ", curr, crawl_count)
    # make an http req
    r = requests.get(curr)
    base = r.url

    # save it to a folder
    text = r.content
    file_name = "docs/" + r.url.replace("/", "") + ".html"
    with open(file_name, 'wb') as f:
      f.write(r.content)

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
      urls.append(currUrl)
  return


if __name__ == '__main__':
  main()
