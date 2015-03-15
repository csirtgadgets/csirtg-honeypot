#!/usr/bin/env python

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

if os.name == 'posix' and os.getuid() == 0:
    print 'ERROR: You must not run kippo as root!'
    sys.exit(1)

# you MUST change these...
interface = '0.0.0.0'
USER = ''
FEED = ''
TOKEN = ''

lastTS = ''
contexts = {}

cfg = config('rdp.yml')


def log_it(peer):
    whiteface_log(peer)


def whiteface_log(peer):
    today = str(datetime.now().date())
    for c in contexts:
        if c != today:
            del contexts[c]

    if not contexts.get(today):
        contexts[today] = {}

    if not contexts[today].get(peer.host):
        contexts[today][peer.host] = []

        log.msg('logging to whiteface...')
        ret = observable.Observable(user=cfg['user'], feed=cfg['feed'], token=cfg['token'], thing=peer.host,
                                            portlist=3389, protocol='tcp', tags='scanner,rdp').new()

        log.msg('logged to whiteface %s ' % ret['observable']['location'])


class TerminalServices(Protocol):
    def dataReceived(self, data):
        global lastTS
        global gi
        global contexts
        tpkt_data = data[:4]
        x224_data = data[4:]
        v, junk, total_len = struct.unpack('!BBH', tpkt_data)
        log.msg("TPKT (v.%d and length %d) on port %d from: %s (%d/TCP):" % (
        v, total_len, self.transport.getHost().port, self.transport.getPeer().host, self.transport.getPeer().port))
        if (len(data) == total_len):
            l, c = struct.unpack('BB', x224_data[:2])
            if c == 0xe0:
                x224 = struct.unpack('!HHBH', x224_data[2:9])
                log.msg("\tX224 Connection Request. Responding...")
                self.transport.write(struct.pack('!BBHBBHHB', v, 0, 11, 6, 0xd0, x224[1], 0x1234, x224[2]))
                logger.info("\tLogin: %s" % x224_data[6:])
                if (lastTS != self.transport.getPeer().host):
                    lastTS = self.transport.getPeer().host
                    thread.start_new_thread(log_it, (self.transport.getPeer(),))
            else:
                log.msg("\tX224 Unrecognized code:")
                self.transport.loseConnection()
                if (lastTS != self.transport.getPeer().host):
                    lastTS = self.transport.getPeer().host
                    thread.start_new_thread(log_it, (self.transport.getPeer(),))
        else:
            log.msg("Data inconsistent... dropping connection.")
            self.transport.loseConnection()
            if (lastTS != self.transport.getPeer().host):
                lastTS = self.transport.getPeer().host
                thread.start_new_thread(log_it, (self.transport.getPeer(),))

fTS = Factory()
fTS.protocol = TerminalServices

application = service.Application('wf-rdp')
service = internet.TCPServer(int(3389), fTS, interface=interface)
service.setServiceParent(application)