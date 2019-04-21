# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading
from utils import work
import queue
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Cook(threading.Thread):
    def __init__(self, own_id, address, root_id, root_address):
        threading.Thread.__init__(self)
        self.equipmentsTime = {'hamburger':3,'drinks':1,'fries':5}
        self.node_comm = Node(own_id, address, root_id, root_address)
        self.node_comm.start()
        self.logger = logging.getLogger("Cook {}".format(self.own_id))

    def wait_on_item(self, food):
        # wait until acces is granted to equipment needed
        answer = self.node_comm.queueIn.get()
        if answer['method'] == 'ACCESS_GRANTED' and answer['args']['equipment'] == food:
            # access granted to equipment
            time = self.equipmentsTime[answer['args']['equipment']]
            work(time)
            return
        else: # put msg back in queueIn to be processed again
            self.node_comm.queueIn.put(answer)
            self.wait_on_item(food)

    def cook_item(self, food):
        msg = {'method':'EQPT_REQ', 
               'args': { 'dest': 'Restaurant' ,
                         'equipment' : food ,
                         'cook' : 'Cook'}}
        self.node_comm.queueOut.put(msg)
        self.wait_on_item(food)
        # notify restaurant that equipment is free
        msg = { 'method' : 'EQPT_USED', 
                'args' : { 'dest' : 'Restaurant', 
                           'equipment': food}}
        self.node_comm.queueOut.put(msg)


    def cook(self, args):
        for food in args['order']: 
            for i in range(int(args['order'][food])):
                self.cook_item(food)
                
        # when all items from request are ready, send message to Employee            
        msg = {'method' : 'ORDER_DONE', 
               'args' : { 'dest': 'Employee' ,
                        'client_addr': args['client_addr'],
                        'orderTicket': args['orderTicket'] }}
        self.node_comm.queueOut.put(msg)


    def run(self):
        done = False
        while not done:
            foodRequest = self.node_comm.queueIn.get()
            if foodRequest is not None:
                # o cliente esta pronto a ir buscar
                if foodRequest['method']=='COOK':
                    self.cook(foodRequest['args'])
            else:
                work()
