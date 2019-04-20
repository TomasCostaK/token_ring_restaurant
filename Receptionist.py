# coding: utf-8

import time
import pickle
import socket
import uuid
import logging
import queue
from utils import work
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

# Chef
# Restaurant
# Employee
# Receptionist

queueIn = queue.Queue()
queueOut = queue.Queue()

class Receptionist(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn
        global queueOut
        w = Worker()
        w.start()
        self.logger = logging.getLogger("Receptionist {}".format(self.own_id))

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
                    #caso seja para esta pessoa
                    if o['args']['args']['id']==self.own_id:
                        queueIn.put(o['args'])
                    else:  
                        self.send(self.sucessor_addr, o)
                elif o['method'] == 'ORDER':
                    self.send(client_address,{'method':'ORDER_RECVD','args':orderTicket})
                    queueIn.put(o)

            if not queueOut.empty():
                #verifica se tem que enviar para alguem
                nextMessage = queueOut.get()
                if nextMessage != None:
                    self.send(self.sucessor_addr, {'method':'TOKEN', 'args':nextMessage })
                    self.logger.debug('Sending Token', nextMessage)

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global queueIn
        global queueOut

    def run(self):
        done = False
        while not done:
            foodRequest = queueIn.get()
            if foodRequest is not None:
                self.logger.debug('Got request: %s', foodRequest)
                orderTicket = uuid.uuid1()
                msg={'method':'COOK', 'args': {'id': self.node_table['Chef'], 'order': foodRequest['args']['order'], 'client_addr':foodRequest['args']['client_addr'], 'orderTicket': orderTicket }}
                queueOut.put(msg)
                #warn client the order is confirmed
                self.logger.debug("Put %s in the out queue")
                work()
            else:
                work()
