#!/usr/bin/python3
# coding:utf-8
import sys
import os
import argparse
import common.util as util
from core.daemon import Daemon

# because conf is widely used, we should
# use CONF to hold it in memory. and this
# is a constant area.
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

import logging


class Rent(Daemon):
  def __init__(self):
    homeDir = conf.get("system", "homeDir")
    pidFile = conf.get("system", "pidFile")
    super(Rent, self).__init__(pidFile)

  def run(self):
    logging.info("enter Rent run function")
    import time
    while True:
      logging.info("yuanbo print here")
      time.sleep(1)



def prepareSystem():
  # set home dir into conf
  filePath = os.path.abspath(sys.argv[0])
  homeDir = os.path.dirname(filePath)
  conf.set("system", "homeDir", homeDir)
  pidFile = conf.get("system", "pidFile")
  util.createFile(pidFile)


def parseArgs():
  args = ARGS_PARSER.parse_args()
  return args


if __name__ == "__main__":
  # parse args before prepare system
  args = parseArgs()
  prepareSystem()
  rent = Rent()
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
