# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Node(threading.Thread):
    def __init__(self, own_id, address, root_id, root_address, timeout=3):
        threading.Thread.__init__(self)
        self.own_id = own_id
        self.address = address
        self.successor_id = None
        self.successor_address = None
        self.root_id = root_id
        self.root_address = root_address  
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.logger = logging.getLogger("Node {}".format(self.own_id))
        self.node_table = dict()

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
        if self.own_id != self.root_id:
            # send message to root to enter the ring
            msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : self.own_id, 'address' : self.address, 'placed' : False }};
            self.send(self.root_address, msg)

    def neighbor_ack(self, args):
        self.logger.debug('Acknowledging neigbour %s', args)
        neighbor_id = args['id']
        neighbor_address = args['address']
        placed = args['placed']
        # if advertised id is to be my next id, register it and notify successor
        # by sending NODE_JOIN message to my previous successor
        if self.successor_id is None: # Node is alone
            msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : self.own_id, 'address' : self.address, 'placed' : True }};
            self.send(neighbor_address, msg)
            self.successor_id = neighbor_id
            self.successor_address = neighbor_address
            self.logger.debug('Successor: %s', self.successor_id)
        elif (neighbor_id > self.own_id and neighbor_id < self.successor_id) or (self.successor_id < self.own_id and (neighbor_id < self.successor_id or neighbor_id > self.own_id)):
            msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : self.successor_id, 'address' : self.successor_address, 'placed' : True }};
            self.send(neighbor_address, msg)
            self.successor_id = neighbor_id
            self.successor_address = neighbor_address
            self.logger.debug('Successor: %s', self.successor_id)
        else:
            if not placed:
                msg = { 'method' : "NODE_JOIN", 'args' : { 'id' : neighbor_id, 'address' : neighbor_address, 'placed' : False }};
                self.send(self.successor_address, msg)

    def print_ring(self):
        self.logger.debug('%s > %s', self.own_id, self.successor_id)
        if self.successor_id == self.root_id:
            return 0
        msg = { 'method' : 'PRINT_RING' }
        self.send(self.successor_address, msg)

    def print_table(self):
        self.logger.debug('%s', self.node_table)
        if self.successor_id == self.root_id:
            return 0
        msg = { 'method' : 'PRINT_TABLE' }
        self.send(self.successor_address, msg)


    def propagate_table(self, args):
        self.node_table = args['table'] # update my table with the one recieved
        rounds = args['rounds']
        myname = self.__class__.__name__
        if self.own_id == self.root_id: # if we are at root, we've made a lap
            rounds+=1
            if rounds > 2: # stop propagating
                return
        if myname in self.node_table: # table is already built and just need to propagate it
            msg = { 'method' : 'NODE_DISCOVERY', 'args' : { 'table' : self.node_table , 'rounds' : rounds } }
            self.send(self.successor_address, msg)
        else: # need to update the table with my id and propagate it
            self.node_table[myname] = self.own_id
            msg = { 'method' : 'NODE_DISCOVERY', 'args' : { 'table' : self.node_table , 'rounds' : rounds } }
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
                elif o['method'] == 'PRINT_RING':
                    self.print_ring()
                elif o['method'] == 'PRINT_TABLE':
                    self.print_table()
                elif o['method'] == 'NODE_DISCOVERY':
                    self.propagate_table(o['args'])
