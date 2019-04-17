# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading
import utils
import queue
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Cook(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn = queue.Queue()
        global queueOut = queue.Queue()
        w = Worker()
        w.start()
        self.logger = logging.getLogger("Cook {}".format(self.own_id))

    def run(self):
        self.socket.bind(self.address)

        self.neighbor_advertise()

        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.debug('O: %s', o)
                if o['method'] == 'NODE_JOIN':
                    self.neighbor_ack(o['args'])
                elif o['method'] == 'PRINT_RING':
                    self.print_ring()
                elif o['method'] == 'PRINT_TABLE':
                    self.print_table()
                elif o['method'] == 'NODE_DISCOVERY':
                    self.propagate_table(o['args'])   
                elif o['method'] == 'TOKEN': # send to worker
                    if o['args']['args']['id']==self.own_id:
                        queueIn.put(o['args'])
                    else:
                        self.send(self.sucessor_addr, o)

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        done = False
        while not done:
            foodRequest = queueIn.get()
            if foodRequest is not None:
                self.logger.debug('Going to cook: %s', foodRequest)
                orderToCook = foodRequest['args']['order']
                msg={'method':'TOKEN','args':
                    {'method':'FOOD_REQ', 'args': 
                    {'id': self.node_table['Restaurant'], 'order': foodRequest['args']['order'], 'client_addr':request['args']['order'], 'orderTicket': orderTicket }}}
                queueOut.get()
                self.logger.debug("Put %s in the out queue")
                work()
            else:
                work()