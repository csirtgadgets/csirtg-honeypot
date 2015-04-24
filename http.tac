#!/usr/bin/env python

# http://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html

import struct
import thread
import sys
from twisted.internet.protocol import Protocol, Factory
from twisted.application import internet, service
from twisted.python import log
from whiteface import observable
from datetime import datetime
import os
from config import config
from pprint import pprint

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s] - %(message)s'

import logging
logger = logging.getLogger()
handle = logging.StreamHandler()
handle.setLevel(logging.DEBUG)
fmt = logging.Formatter(LOG_FORMAT)
handle.setFormatter(fmt)
logger.addHandler(handle)
logger.setLevel('INFO')

#if os.name == 'posix' and os.getuid() == 0:
#    print 'ERROR: You must not run me as root!'
#    sys.exit(1)

# you MUST change these...
interface = '0.0.0.0'
USER = ''
FEED = ''
TOKEN = ''
PORTLIST = '80'
PROTO = 'tcp'
TAGS = 'scanner,http'

contexts = {}

if not os.path.exists('http.yml'):
    logger.error('missing http.yml config file')
    sys.exit()

cfg = config('http.yml')


def log_it(peer):
    whiteface_log(peer)


def whiteface_log(peer):
    today = str(datetime.now().date())

    pprint(peer)
    pprint(contexts)
    print peer.host

    for c in contexts:
        if c != today:
            del contexts[c]

    pprint(contexts)

    if not contexts.get(today):
        contexts[today] = {}

    if not contexts[today].get(peer.host):
        contexts[today][peer.host] = 1

        log.msg('logging to whiteface...')
        ret = observable.Observable(user=cfg['user'], feed=cfg['feed'], token=cfg['token'], thing=peer.host,
                                            portlist=80, protocol='tcp', tags='scanner,http').new()

        log.msg('logged to whiteface %s ' % ret['observable']['location'])


class Fake(Protocol):
    global contexts
    def connectionMade(self):
        thread.start_new_thread(log_it, (self.transport.getPeer(),))



fTS = Factory()
fTS.protocol = Fake

application = service.Application('wf-http')
service = internet.TCPServer(int(80), fTS, interface=interface)
service.setServiceParent(application)
