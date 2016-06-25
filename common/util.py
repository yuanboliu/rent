#! /bin/python
# coding:utf-8

import os
import logging
import configparser
import logging.config


def setupLogging(logConfFile="conf/logging.ini", logLevel=logging.INFO):
  # create logs dir
  if not os.path.exists("logs"):
    os.mkdir("logs")
  if os.path.exists(logConfFile):
    logging.config.fileConfig(logConfFile)
  else:
    logging.basicConfig(level=logLevel)


# singleton for configuration
def resetConf(configFile="conf/rent.ini"):
  configure = configparser.ConfigParser()
  if os.path.exists(configFile):
    configure.read(configFile, "utf8")
  return configure


# this parameter should not be directly modified outside
CONF = resetConf()