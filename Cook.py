# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading
import queue
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Cook(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        self.queueIn = queue.Queue()
        self.queueOut = queue.Queue()
        self.logger = logging.getLogger("Cook {}".format(self.own_id))

    def receiveRequest(self,args): #if method == FOOD_REQ
        pass

    def requestGrill(self,args): #if args hambg
        pass

    def requestFry(self,args): #if args fries
        pass

    def requestDrink(self,args): #if args drinks
        pass

    def foodDone(self,args): #avisa o empregado que esta pronto
        pass

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
                elif o['method'] == 'FOOD_REQ':
                    self.receiveRequest(o['args'])
