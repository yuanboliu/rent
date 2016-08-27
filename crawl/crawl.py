#!/usr/bin/python3
#coding:utf-8
import asyncio
import cgi
import aiohttp
import time
import logging
import urllib.parse
import re
from collections import namedtuple
import common.util

try:
  # Python 3.4.
  from asyncio import JoinableQueue as Queue
except ImportError:
  # Python 3.5.
  from asyncio import Queue

# a new tuple to record the process of crawl
FetchStatistic = namedtuple('FetchStatistic',
                            ['url',
                             'nextUrl',
                             'status',
                             'exception',
                             'size',
                             'contentType',
                             'encoding',
                             'numUrls',
                             'numNewUrls'])

class Crawler:
  """Crawl a set of URLs.
    This manages two sets of URLs: 'urls' and 'done'.  'urls' is a set of
    URLs seen, and 'done' is a list of FetchStatistics.
  """
  def __init__(self, roots,
               exclude=None,  # What to crawl.
               maxRedirect=10, maxTries=4,  # Per-url limits.
               maxTasks=10, *, loop=None):
    self.loop = loop or asyncio.get_event_loop()
    self.exclude = exclude
    self.maxRedirect = maxRedirect
    self.maxTries = maxTries
    self.maxTasks = maxTasks
    self.roots = roots
    self.queue = Queue(loop=self.loop)
    self.seenUrls = set()
    self.session = aiohttp.ClientSession(loop=self.loop)
    # this property seems useless
    self.rootDomains = set()
    self.seenUrls = set()

    # this part of code is complicated, need to be modified
    for root in self.roots:
      # this the pattern of urlParse
      # scheme://netloc/path;parameters?query#fragment
      urlDict = urllib.parse.urlparse(root)
      host, port = urllib.parse.splitport(urlDict.netloc)
      if not host:
        continue
      self.rootDomains.add(host.lower())
      self.addUrl(root)

    # record time here
    self.t0 = time.time()
    self.t1 = None


  def addUrl(self, url, maxRedirect=None):
    if maxRedirect is None:
      maxRedirect = self.maxRedirect
    logging.info("add a url to the queue if not seen before")
    self.seenUrls.add(url)
    self.queue.put_nowait((url, maxRedirect))


  def hostOkay(self, host):
    """Check if a host should be crawled.

    A literal match (after lowercasing) is always good.  For hosts
    that don't look like IP addresses, some approximate matches
    are okay depending on the strict flag.
    """
    host = host.lower()
    if host in self.rootDomains:
      return True
    # if this is a ip address, ignore it
    if re.match(r'\A[\d\.]*\Z', host):
      return False
    return True


  def urlAllowed(self, url):
    # use regex pattern to exclude some urls
    if self.exclude and re.search(self.exclude, url):
      return False
    parts = urllib.parse.urlparse(url)
    if parts.scheme not in ('http', 'https'):
      logging.debug('skipping non-http scheme in %r', url)
      return False
    host, port = urllib.parse.splitport(parts.netloc)
    if not self.hostOkay(host):
      logging.debug('skipping non-root host in %r', url)
      return False
    return True

  def close(self):
    """Close resources."""
    self.session.close()

  """
  get links from web page content
  """
  @asyncio.coroutine
  def parseLinks(self, response):
    links = set()

    if response.status == 200:
      contentType = response.headers.get('content-type')
      if contentType:
        contentType, pDict = cgi.parse_header(contentType)
      if contentType in ('text/html', 'application/xml'):
        text = yield from response.text()
        urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''',
                              text))
        if urls:
          logging.info('got %r distinct urls from %r',
                       len(urls), response.url)
        for url in urls:
          # format relative urls
          normalized = urllib.parse.urljoin(response.url, url)
          # split fragment from url
          # http://c#b b is a fragment
          deFragmented, frag = urllib.parse.urldefrag(normalized)
          if self.urlAllowed(deFragmented):
            links.add(deFragmented)
    return links


  @asyncio.coroutine
  def fetch(self, url, maxRedirect):
    """Fetch one URL."""
    tries = 0
    while tries < self.maxTries:
      try:
        response = yield from self.session.get(
          url, allow_redirects=False)
        if tries > 1:
          logging.info('try %r for %r success', tries, url)
        break
      except aiohttp.ClientError as clientError:
        logging.info("try %r for %r raised %r",tries, url, clientError)
      tries += 1
    # this else is relative to while, means
    # if tries >= self.maxTries, execute else segment
    else:
      logging.error('%r failed after %r tries', url, self.maxTries)
      return

    try:
      if common.util.isRedirect(response):
        location = response.headers['location']
        # location is the base url and get relative path from url
        # then we compose a new url as a next url
        nextUrl = urllib.parse.urljoin(url, location)
        if nextUrl in self.seenUrls:
          return
        if maxRedirect > 0:
          logging.info('redirect to %r from %r', nextUrl, url)
          # redirect recursion here
          self.addUrl(nextUrl, maxRedirect - 1)
        else:
          logging.error('redirect limit reached for %r from %r',
                        nextUrl, url)
      # if url is not a redirect url
      else:
        links = yield from self.parseLinks(response)
        for link in links.difference(self.seenUrls):
          self.queue.put_nowait((link, self.maxRedirect))
        # update links and add those links to seen links
        # if links in queue or has been visited, then
        # add it to seen links
        self.seenUrls.update(links)
    finally:
      yield from response.release()

  @asyncio.coroutine
  def work(self):
    try:
      while True:
        url, maxRedirect = yield from self.queue.get()
        assert url in self.seenUrls
        # in python2 we use `for` to yield, we now simply yield from
        yield from self.fetch(url, maxRedirect)
        # when one url fetch is done, send message to queue
        self.queue.task_done()
    except asyncio.CancelledError:
      pass

  @asyncio.coroutine
  def crawl(self):
    """Run the crawler until all finished."""
    workers = [asyncio.Task(self.work(), loop=self.loop)
               for _ in range(self.maxTasks)]
    self.t0 = time.time()
    # wait until queue is empty
    yield from self.queue.join()
    self.t1 = time.time()
    for w in workers:
      w.cancel()

def main():
  pass

if __name__ == '__main__':
    main()