#!/usr/bin/python3
# coding:utf-8
import sys
import os
import argparse
import asyncio
import common.util as util
from core.daemon import Daemon
from crawl.crawl import Crawler
import crawl.report

# because conf is widely used, we should
# use CONF to hold it in memory. and this
# is a constant and initial area.
conf = util.resetConf("conf/rent.ini")
util.setupLogging("conf/logging.ini")
util.CONF = conf
PROGRAM_NAME = "rent system"
SYS_VERSION = conf.get("system", "version")
ARGS_PARSER = argparse.ArgumentParser(description=PROGRAM_NAME)
ARGS_PARSER.add_argument(
    '-d', action='store', required=False, dest="daemon",
    choices=["start", "stop", "status", "restart"],
    help='operate the background process')
ARGS_PARSER.add_argument('-v', "--version",
                         action="version",
                         version="%s %s" % (PROGRAM_NAME, SYS_VERSION),
                         help="show the system's version number")
ARGS_PARSER.add_argument('-c', "--crawl",
                         action="store_const",
                         const=True,
                         help="whether or not start crawlers, if this \
                              option is used, means to start them")

import logging


# function area, get dictionaries or collections frm conf file
def getSiteDict():
  # split site and get all root
  siteList = conf.get("site", "all", "").split(",")
  siteDict = {}
  for site in siteList:
    siteDict[site] = {}
    tmpList = conf.get(site, "root", "").split(",")
    # collection can erase redundant root of site
    siteDict[site].rootList = { util.fix_url(root) for root in tmpList }
    siteDict[site].userName = conf.get(site, "userName", "")
    siteDict[site].password = conf.get(site, "password", "")
    siteDict[site].needLogin = conf.getboolean(site, "needLogin", False)
  return siteDict


class Rent(Daemon):

  def __init__(self, args = None):
    pidFile = conf.get("system", "pidFile")
    super(Rent, self).__init__(pidFile)
    self.args = args


  def startSiteCrawler(self):
    # if command line does not contain --crawl
    if not self.args.crawl:
      return
    # get site dictionary
    siteDict = getSiteDict()
    loop = asyncio.get_event_loop()
    # use multi threads to start crawl
    for site in siteDict:
      crawler = Crawler(site.rootList,
                        maxRedirect=conf.getint("system", "maxRedirect", 10),
                        maxTries=conf.getint("system", "maxTries", 4),
                        maxTasks=conf.getint("system", "maxTasks", 10))
      try:
        loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl
      except KeyboardInterrupt:
        sys.stderr.flush()
        logging.error("Interrupted")
      finally:
        crawl.report.report(crawler)
        crawler.close()
        # next two lines are required for actual aiohttp resource cleanup
        loop.stop()
        loop.run_forever()
        loop.close()


  def run(self):
    logging.info("enter Rent run function")

    # start running site crawler
    self.startSiteCrawler()



def prepareSystem():
  # set home dir into conf
  filePath = os.path.abspath(sys.argv[0])
  homeDir = os.path.dirname(filePath)
  conf.set("system", "homeDir", homeDir)
  pidFile = conf.get("system", "pidFile")
  reportFile = conf.get("system", "reportFile")
  util.createFile(reportFile)
  util.createFile(pidFile)


def parseArgs():
  args = ARGS_PARSER.parse_args()
  return args


if __name__ == "__main__":
  # parse args before prepare system
  args = parseArgs()
  prepareSystem()
  rent = Rent(args)
  logging.info("started background process and log into file")

  # if need to operate process
  if args.daemon == "start":
    rent.start()
  elif args.daemon == "stop":
    rent.stop()
  elif args.daemon == "restart":
    rent.restart()
  elif args.daemon == "status":
    rent.status()
