#!/usr/bin/env python
#coding:utf8
import urllib
import urllib2
import httplib
import cookielib
import os
import re
import sys
import time
import logging 
import hmac
import base64
import hashlib
import commands
import mimetypes

from cStringIO import StringIO
#from abc import abstractmethod
from urlparse import urlparse
from datetime import datetime


class FileSystemException(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'FileSystemException: ' + str(self.msg)

class NotImplementException(Exception):
    def __init__(self, msg=''):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return 'NotImplementException: ' + str(self.msg)

###########################################################
# retry
###########################################################

def retry(ExceptionToCheck, tries=4, delay=2, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        excpetions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print >>sys.stderr, msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry  # true decorator
    return deco_retry



###########################################################
# color system
###########################################################
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.ENDC = ''

def to_red(s):       return  bcolors.RED+ str(s) + bcolors.ENDC
def to_yellow(s):    return  bcolors.YELLOW+ str(s) + bcolors.ENDC
def to_green(s):     return  bcolors.GREEN + str(s) + bcolors.ENDC
def to_blue(s):      return  bcolors.BLUE+ str(s) + bcolors.ENDC


###########################################################
# misc
###########################################################
def shorten(s, l=80):
    if len(s)<=l:
        return s
    return s[:l-3] + '...'

#commands dose not work on windows..
def system(cmd):
    logging.info(cmd)
    r = commands.getoutput(cmd)
    logging.debug(r)
    return r
	
def system(cmd):
    logging.info(cmd)
    from subprocess import Popen, PIPE
    p = Popen(cmd, shell=True, bufsize = 102400, stdout=PIPE)
    p.wait()
    r = p.stdout.read()
    logging.debug(r)
    return r

def md5_for_file(f, block_size=2**20):
    f = open(f, 'rb')
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()

def parse_size(input):
    K = 1024
    M = K * K
    G = M * K
    T = G * K
    sizestr = re.search(r'(\d*)', input).group(1)
    size = int(sizestr)
    if input.find("k") > 0 or input.find("K") > 0 :
        size=size*K
    if input.find("m") > 0 or input.find("M") > 0 :
        size=size*M
    if input.find("g") > 0 or input.find("G") > 0 :
        size=size*G
    if input.find("t") > 0 or input.find("T") > 0 :
        size=size*T
    return size

def format_size(input):
    input = int(input)
    K = 1024.
    M = K * K
    G = M * K
    T = G * K
    if input >= T: return '%.2fT' % (input /  T)
    if input >= G: return '%.2fG' % (input /  G)
    if input >= M: return '%.2fM' % (input /  M)
    if input >= K: return '%.2fK' % (input /  K)
    return '%d' % input


def format_time(timestamp):
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    t = datetime.fromtimestamp(float(timestamp))
    return t.strftime(ISOTIMEFORMAT)

'''
set_level 设为
'''
def init_logging(logger, set_level = logging.INFO, 
        console = True,
        log_file_path = None):

    logger.setLevel(logging.DEBUG)
    logger.propagate = False # it's parent will not print log (especially when client use a 'root' logger)
    for h in logger.handlers:
        logger.removeHandler(h)
    if console:
        fh = logging.StreamHandler()
        fh.setLevel(set_level)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if log_file_path:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(set_level)
        formatter = logging.Formatter("%(asctime)-15s %(levelname)s  %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)


