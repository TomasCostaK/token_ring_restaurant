# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Node(threading.Thread):
    def __init__(self, id, address, root_id, root_address, timeout=3):
        self.id = id
        self.address = address
        self.successor_id = None
        self.successor_address = None
        self.root_id = root_id
        self.root_address = root_address  
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.logger = logging.getLogger("Node {}".format(self.id))

    def send(self, address, o):
        p = pickle.dumps(o)
        self.socket.sendto(p, address)

    def recv(self):
        try:
            p, addr = self.socket.recvfrom(1024)
        except socket.timeout:
            return None, None
        else:
            if len(p) == 0:
                return None, addr
            else:
                return p, addr

    def neighbor_advertise(self):
        self.logger.debug('Advertising to neighbors')
        # send message to root to enter the ring
        msg = { method : "NODE_JOIN", args : { id : self.id, address : self.address }};
        self.send(self.root_address, msg)

    def neighbor_ack(self, args):
        self.logger.debug('Acknowledging neigbour %s', args)
        neighbor_id = args['id']
        neighbor_address = args['address']
        # if advertised id is to be my next id, register it and notify successor
        # by sending NODE_JOIN message to my previous successor
        if neighbor_id < self.successor_id or self.successor_id is None or self.successor_id == self.root_id:
            msg = { method : "NODE_JOIN", args : { id : self.successor_id, address : self.successor_addr }};
            self.send(neighbor_address, msg)
            self.successor_id = neighbor_id
            self.successor_addr = neighbor_address
        else:
            msg = { method : "NODE_JOIN", args : { id : neighbor_id, address : neighbor_address }};
            self.send(self.successor_addr, msg)

    def run(self):
        self.socket.bind(self.addr)

        self.neighbor_advertise()

        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.info('O: %s', o)
                if o['method'] == 'NODE_JOIN':
                    self.neighbor_ack(o['args'])
                elif o['method'] == 'NOTIFY':
                    self.notify(o['args'])
                elif o['method'] == 'PUT':
                    if 'src_address' in o['args']:
                        self.put(o['args']['key'], o['args']['value'], addr, o['args']['src_address'])
                    else:
                        self.put(o['args']['key'], o['args']['value'], addr)
                elif o['method'] == 'GET':
                    if 'src_address' in o['args']:
                        self.get(o['args']['key'], addr, o['args']['src_address'])
                    else:
                        self.get(o['args']['key'], addr)
                elif o['method'] == 'PREDECESSOR':
                    self.send(addr, {'method': 'STABILIZE', 'args': self.predecessor_id})
                elif o['method'] == 'STABILIZE':
                    self.stabilize(o['args'], addr)
            else:
                # Ask for predecessor to start the stabilize process
                self.send(self.successor_addr, {'method': 'PREDECESSOR'})





