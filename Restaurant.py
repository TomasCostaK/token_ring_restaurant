# coding: utf-8

import time
import pickle
import socket
import logging
import uuid
import queue
# import argparse
import threading
from utils import work
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

queueIn = queue.Queue()
queueOut = queue.Queue()

class Restaurant(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn
        global queueOut
        w = Worker()
        w.start()
        self.logger = logging.getLogger("Restaurant {}".format(self.own_id))

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
                elif o['method'] == 'ORDER': # need to wrap in TOKEN
                    msg = { 'method' : 'TOKEN' , 
                            'args' : { 'method' : o['method'], 
                                       'args' : { 'client_addr' : addr, 
                                                  'order' : o['args'] }, 
                                       'dest_id' : self.node_table['Receptionist'] }}
                    self.send(self.successor_address, msg)
                elif o['method'] == 'TOKEN': # send to worker
                    if o['args']=='EMPTY':
                        if not queueOut.empty():
                            nextMessage = queueOut.get()
                            if nextMessage != None:
                                # wrap in TOKEN
                                msg = { 'method' : 'TOKEN', 'args' : nextMessage }
                                msg['args']['dest_id'] = self.node_table[nextMessage['args']['dest']]
                                self.send(self.successor_address, msg)
                                self.logger.debug('Sending Token', msg)
                        else:
                            self.send(self.successor_address, o)
                    elif o['args']['dest_id']==self.own_id:
                        self.logger.debug('Sending object to Worker Thread')
                        queueIn.put(o['args'])
                    else:  
                        self.send(self.successor_address, o)

                    # queueIn.put(msg)
                    # self.send(client_address,{'method':'ORDER_RECVD','args':orderTicket})
                    # queueIn.put(o)

            if queueOut.empty() == False:
                self.send(self.successor_address, queueOut.get())

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
                # self.logger.debug('Going to : %s', foodRequest)
                #change here
                work()
            else:
                work()
