from celery_app import crawl, test

# initial crawl space
crawl.delay("https://www.google.com/")
