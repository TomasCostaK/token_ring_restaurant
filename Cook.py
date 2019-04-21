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

queueIn = queue.Queue()
queueOut = queue.Queue()

class Cook(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn
        global queueOut
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
                #self.logger.debug('O: %s', o)
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
                        msg = { 'method' : 'TOKEN', 'args' : 'EMPTY' }
                        self.send(self.successor_address, msg) #ja o recebeu e agora vai enviar um token vazio para o proximo
                    else:  
                        self.send(self.successor_address, o)

        

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global queueIn
        global queueOut
        self.equipmentsTime = {'hamburger':3,'drinks':1,'fries':5}


    def wait_on_item(self, food):
        # wait until acces is granted to equipment needed
        answer = queueIn.get()
        if answer['method'] == 'ACCESS_GRANTED' and answer['args']['equipment'] == food:
            # access granted to equipment
            time = equipmentsTime['equipment']
            work(time)
            return
        else: # put msg back in queueIn to be processed again
            queueIn.put(answer)
            self.wait_on_item(food)

    def cook_item(self, food):
        msg = {'method':'EQPT_REQ', 
               'args': { 'dest': 'Restaurant' ,
                         'equipment' : food }}
        queueOut.put(msg)
        self.wait_on_item(food)
        # notify restaurant that equipment is free
        msg = { 'method' : 'EQPT_USED', 
                'args' : { 'dest' : 'Restaurant', 
                           'equipment': food }}
        queueOut.put(msg)


    def cook(self, args):
        for food in args['order']: 
            for i in range(int(args['order'][food])):
                self.cook_item(food)
                
        # when all items from request are ready, send message to Employee            
        msg = {'method' : 'ORDER_DONE', 
               'args' : { 'dest': 'Employee' ,
                        'client_addr': foodRequest['args']['client_addr'],
                        'orderTicket': foodRequest['args']['orderTicket'] }}
        queueOut.put(msg)


    def run(self):
        done = False
        while not done:
            foodRequest = queueIn.get()
            if foodRequest is not None:
                # o cliente esta pronto a ir buscar
                if foodRequest['method']=='COOK':
                    self.cook(foodRequest['args'])
            else:
                work()
