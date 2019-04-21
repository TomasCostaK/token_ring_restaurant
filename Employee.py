# coding: utf-8

import time
import pickle
import socket
import logging
from utils import work
# import argparse
import threading
import queue
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

queueIn = queue.Queue()
queueOut = queue.Queue()

class Employee(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn
        global queueOut
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
                                if nextMessage['method']=='DELIVER': #enviar pra cliente caso method seja deliver
                                    self.send(nextMessage['args']['client_addr'], nextMessage['args']['orderTicket'])
                                    self.logger.debug('Sending client %s food', nextMessage['args']['orderTicket'])
                                else: #else propaga o token
                                    # wrap in TOKEN
                                    msg = { 'method' : 'TOKEN', 'args' : nextMessage }
                                    msg['args']['dest_id'] = self.node_table[nextMessage['args']['dest']]
                                    self.send(self.successor_address, msg)
                                    self.logger.debug('Sending Token: %s', nextMessage['method'])
                        else:
                            self.send(self.successor_address, o)
                    elif o['args']['dest_id']==self.own_id:
                        self.logger.debug('Sending %s object to Worker Thread', o['args'])
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
        self.queueDone = []
        self.queueWaiting = [] # clients waiting to pickup

    def deliver(self, args):
        if any(orderLista == args['orderTicket'] for orderLista in self.queueDone):
            self.queueDone.remove(args['orderTicket'])
            msg = { 'method' : 'DELIVER',
                    'args' : args }
            queueOut.put(msg)  
            return True                  
        return False

    def wait_in_line(self,args):
        if not self.deliver(args):
            print("Meu pedido ainda nao chegou")
            self.queueWaiting.append(args['order']['orderTicket'])


    def run(self):
        done = False
        while not done:
            foodRequest = queueIn.get()
            if foodRequest is not None:
                if len(self.queueWaiting) != 0:
                    self.deliver(self.queueWaiting[0])

                #o cliente esta pronto a ir buscar
                if foodRequest['method']=='PICKUP':
                    self.wait_in_line(foodRequest['args'])

                #caso a comida esteja pronta
                elif foodRequest['method']=='ORDER_DONE':
                    self.queueDone.append(foodRequest['args']['orderTicket'])
                    print(self.queueDone)
                    print(self.queueWaiting)
                    print(foodRequest['args'])
                    self.deliver(foodRequest['args'])
                work()
            else:
                work()
