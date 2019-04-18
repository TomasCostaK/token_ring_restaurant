# coding: utf-8

import time
import pickle
import socket
import logging
import uuid
import queue
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Restaurant(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn = queue.Queue()
        global queueOut = queue.Queue()
        w = Worker()
        w.start()
        self.logger = logging.getLogger("Restaurant {}".format(self.own_id))

    def send(self, address, o):
        p = pickle.dumps(o)
        self.socket.sendto(p, address)

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
                    if o['args']=='EMPTY':
                        if queueOut.empty() == False:
                            self.send(self.sucessor_addr, queueOut.get())
                        else:  #esta parte?
                            self.send(self.sucessor_addr, {'method':'TOKEN','args':'EMPTY'})
                    #caso seja para esta pessoa
                    elif o['args']['args']['id']==self.own_id:
                        queueIn.put(o['args'])


class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        done = False
        while not done:
            foodRequest = queueIn.get()
            if foodRequest is not None:
                self.logger.debug('Going to : %s', foodRequest)
                #change here
                work()
            else:
                work()
