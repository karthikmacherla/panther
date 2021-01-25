# Project Outline!


## Goals:
- Distributed web crawler in python, similar to the spec sheet given in 555
- mercator style 
- decent workflow and way to build on top of code
- focus on modularity!!!
- try not to cheat / use too many online sources in the spirit of this assignment


## Timesheets:
6:35pm - 7:00pm : looked at hw2 from 555
7:45pm - 9:00pm : wrote a single threaded script that literally just makes a request + saves file. tried to figured out why pipenv shell wasn't working
9:00pm - 9:30 : single threaded crawler (doesn't save url frontier)
7:30pm - 8:01pm : read intro to celery ~ celery is a distributed task queue + uses DBs to relay messages + store results of tasks
3:30 - 4:10pm : crawler that crawls a doc, and continuously finds neighbors and adds to redis queue.

## The way it works:
we have 4 key tasks:
- url frontier which literally just pops things from the persistent queue
- crawler which makes the request and fetches the page, sends over url + doc
- you must eventually call result.get() or result.forget() on every async task apparently 
bc it uses memory resources

## Loose Ends/Next Steps
- `pipenv` bs
- figure out how to add to mongodb
- bad workflow. find a way to be able to start everything all at once
- use a celery config file