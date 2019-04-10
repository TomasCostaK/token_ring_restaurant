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
        threading.Thread.__init__(self)
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
        msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : self.id, 'address' : self.address, 'placed' : False }};
        self.send(self.root_address, msg)

    def neighbor_ack(self, args):
        self.logger.debug('Acknowledging neigbour %s', args)
        neighbor_id = args['id']
        neighbor_address = args['address']
        placed = args['placed']
        # if advertised id is to be my next id, register it and notify successor
        # by sending NODE_JOIN message to my previous successor
        if self.successor_id is None:
            msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : self.id, 'address' : self.address, 'placed' : True }};
            self.send(neighbor_address, msg)
            self.successor_id = neighbor_id
            self.successor_address = neighbor_address
            self.logger.debug('Successor: %s', self.successor_id)
        elif neighbor_id < self.successor_id or self.successor_id == self.root_id:
            msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : self.successor_id, 'address' : self.successor_address, 'placed' : True }};
            self.send(neighbor_address, msg)
            self.successor_id = neighbor_id
            self.successor_address = neighbor_address
            self.logger.debug('Successor: %s', self.successor_id)
        else:
            if not placed:
                msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : neighbor_id, 'address' : neighbor_address, 'placed' : False }};
                self.send(self.successor_address, msg)

    def run(self):
        self.socket.bind(self.address)

        self.neighbor_advertise()

        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.info('O: %s', o)
                if o['method'] == 'NODE_JOIN':
                    self.neighbor_ack(o['args'])
