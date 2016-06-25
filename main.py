#! /bin/python
# coding:utf-8
import sys
import os
import common.util


def run():
  pass


def start():
  pass


def stop():
  pass


if __name__ == "__main__":
  baseAbsPath = os.path.abspath(sys.argv[0])
  basePath = os.path.dirname(baseAbsPath)
  conf = common.util.CONF
  conf.set("system", "basePath", basePath)
