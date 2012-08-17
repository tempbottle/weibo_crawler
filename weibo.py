#!/usr/bin/env python
#coding: utf-8
#file   : weibo.py
#author : ning
#date   : 2012-08-17 21:54:20



import urllib, urllib2
import os, sys
import re, time
import logging
import copy
import random
import httpc
from httpc import *
from httpc import HttplibHTTPC
from httpc import HTTPException

from common import init_logging, retry

try:
    import json
except:
    import simplejson as json

init_logging(httpc.logger)

#myuid: 1872013465

def _build_url(base_url, params):
    for k, v in params.items():
        if isinstance(v, unicode) : 
            params[k] = v.encode('utf-8') 
    return base_url + '?' + urllib.urlencode(params)

http_client = CurlHTTPC()

headers = {
    'Cookie' : 'xxxxxxxxxx'
    ,

}

@retry(Exception, delay=1, tries=1)
def list(page):
    url = 'http://weibo.com/aj/mblog/info/big'
    params = {
        'id':'3473449194485683',
        'max_id':'3480128992296125',
        'page': page,
        '_t':'0',
        '__rnd':'1345213457270',
    }
    url = _build_url(url, params)
    response = http_client.get(url, headers)
    body = response['body']
    body = json.loads(body)
    #print body
    html = body['data']['html'].encode('utf8')
    lst = re.findall('<dd>.*?</dd>', html, re.DOTALL)
    return lst

@retry(Exception, delay=1, tries=1)
def parse_path(dd):
    lst = re.findall('usercard="(.*?)"', dd, re.DOTALL)
    print lst
    print ''


def main():
    for page in range(49):
        for i in list(page):
            parse_path(i)
    
main()


