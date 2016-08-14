#! /bin/python
# coding:utf-8

import os
import shutil
import logging
import configparser
import logging.config

def createDirectory(dirName):
  if not os.path.exists(dirName):
    os.makedirs(dirName)

def createFile(fileName):
  if not os.path.exists(fileName):
    filePath = os.path.dirname(fileName)
    createDirectory(filePath)
    open(fileName, "w+").close()


def setupLogging(logConfFile="conf/logging.ini", logLevel=logging.INFO):
  # create logs dir
  createDirectory("logs")
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

def fix_url(url):
  """Prefix a schema-less URL with http://."""
  if '://' not in url:
    url = 'http://' + url
  return url

def isRedirect(response):
  return response.status in (300, 301, 302, 303, 307)

# this parameters is used to transport
# info between classes and functions.
CONF = None
