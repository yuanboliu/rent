#! /bin/python
# coding:utf-8
import sys
import os
import common.util as util
from core.daemon import Daemon

conf = util.CONF

class Rent(Daemon):

  def __init__(self):
    homeDir = conf.get("system", "homeDir")
    pidFile = conf.get("system", "pidFile")
    super(Rent, self).__init__(pidFile)

  def run(self):
    print "running here"

def prepareSystem():
  # set home dir into conf
  filePath = os.path.abspath(sys.argv[0])
  homeDir = os.path.dirname(filePath)
  conf.set("system", "homeDir", homeDir)
  pidFile = conf.get("system", "pidFile")
  util.createFile(pidFile)
  util.setupLogging("conf/test.ini")


if __name__ == "__main__":
  prepareSystem()
  import logging
  logging.info("test for yuanbo")
  rent = Rent()
  rent.start()
