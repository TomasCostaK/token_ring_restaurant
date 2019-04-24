# coding: utf-8

import time
import pickle
import socket
import logging
from utils import work
# import argparse
import threading
import queue
from Entity import Entity

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Employee(threading.Thread):
    def __init__(self, own_id, address, root_id, root_address):
        threading.Thread.__init__(self)
        self.node_comm = Entity(own_id, address, root_id, root_address, 'Employee')
        self.node_comm.start()
        self.logger = logging.getLogger("Employee {}".format(self.node_comm.own_id))
        self.queueDone = []
        self.queueWaiting = [] # clients waiting to pickup

    def deliver(self, args):
        if any(orderLista == args['orderTicket'] for orderLista in self.queueDone):
            self.queueDone.remove(args['orderTicket'])
            self.queueWaiting.remove(args['orderTicket'])
            msg = { 'method' : 'DELIVER',
                    'args' : args }
            self.node_comm.queueOut.put(msg)  
            return True                  
        return False

    def wait_in_line(self,args):
        if not self.deliver(args):
            self.queueWaiting.append(args['order']['orderTicket'])


    def run(self):
        done = False
        while not done:
            foodRequest = self.node_comm.queueIn.get()
            if foodRequest is not None:
                if len(self.queueWaiting) != 0:
                    self.deliver(self.queueWaiting[0])

                #o cliente esta pronto a ir buscar
                if foodRequest['method']=='PICKUP':
                    self.wait_in_line(foodRequest['args'])

                #caso a comida esteja pronta
                elif foodRequest['method']=='ORDER_DONE':
                    self.queueDone.append(foodRequest['args']['orderTicket'])
                    self.deliver(foodRequest['args'])
                work()
            else:
                work()
