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

class Employee(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn = queue.Queue()
        global queueOut = queue.Queue()
        w = Worker()
        w.start()
        self.logger = logging.getLogger("Employee {}".format(self.own_id))

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
                        nextMessage = queueOut.get()
                        #assim so vai responder ao cliente quando o token lhe chegar vazio
                        if nextMessage != None:
                            if nextMessage['method']=='PICKUP': #enviar pra cliente caso method seja deliver
                                self.send(nextMessage['args']['cliente_addr'], pickle.loads(nextMessage['args']['orderTicket']))
                                self.logger.debug('Sending client %s food', nextMessage['args']['orderTicket'])

                            else: #else propaga o token
                                self.send(self.sucessor_addr, nextMessage)
                                self.logger.debug('Sending Token', nextMessage)

                        else:  #esta parte?
                            self.send(self.sucessor_addr, o)
                    #caso seja para esta pessoa
                    elif o['args']['args']['id']==self.own_id:
                        queueIn.put(o['args'])


class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queueDone = queue.Queue()

    def run(self):
        done = False
        while not done:
            foodRequest = queueIn.get()
            if foodRequest is not None:
                #o cliente esta pronto a ir buscar
                if foodRequest['method']=='PICKUP':
                self.logger.debug('Client %s is waiting to pickup.', foodRequest['args']['orderTicket'])
                    while True:
                        if foodRequest['args']['orderTicket'] in queueDone:
                            queueDone.put(foodRequest)                           
                            break

                #caso a comida esteja pronta
                elif foodRequest['method']=='ORDER_DONE':
                    queueDone.put(foodRequest['args']['orderTicket'])
                    self.logger.debug('Food for %s is done.', foodRequest['args']['orderTicket'])
                work()
            else:
                work()
