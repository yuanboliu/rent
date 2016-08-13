#!/usr/bin/python3
#coding:utf-8
import asyncio
import aiohttp

try:
  # Python 3.4.
  from asyncio import JoinableQueue as Queue
except ImportError:
  # Python 3.5.
  from asyncio import Queue

class Crawler:
  """Crawl a set of URLs.
    This manages two sets of URLs: 'urls' and 'done'.  'urls' is a set of
    URLs seen, and 'done' is a list of FetchStatistics.
  """
  def __init__(self, roots,
               exclude=None, strict=True,  # What to crawl.
               max_redirect=10, max_tries=4,  # Per-url limits.
               max_tasks=10, *, loop=None):
    self.loop = loop or asyncio.get_event_loop()
    self.exclude = exclude
    self.strict = strict
    self.max_redirect = max_redirect
    self.max_tries = max_tries
    self.max_tasks = max_tasks
    self.roots = roots
    self.queue = Queue(loop=self.loop)
    self.seenUrls = set()
    self.done = []
    self.session = aiohttp.ClientSession(loop=self.loop)

def main():
  pass

if __name__ == '__main__':
    main()