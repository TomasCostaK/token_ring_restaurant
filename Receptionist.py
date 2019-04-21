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
                        #caso esteja vazio e tenha algo para enviar
                        if not queueOut.empty():
                            #verifica se tem que enviar para alguem
                            nextMessage = queueOut.get()
                            if nextMessage != None:
                                if nextMessage['method'] == 'ORDER_RECVD':
                                    self.send(nextMessage['args']['client_addr'], nextMessage)
                                else:
                                    # wrap in TOKEN
                                    msg = { 'method' : 'TOKEN', 'args' : nextMessage }
                                    msg['args']['dest_id'] = self.node_table[nextMessage['args']['dest']]
                                    self.send(self.successor_address, msg)
                                    self.logger.debug('Sending Token: %s', nextMessage['method'])
                        else:
                            self.send(self.successor_address, o)
                            #caso nao esteja vazio e seja para ele
                    elif o['args']['dest_id']==self.own_id:
                        self.logger.debug('Sending object to Worker Thread')
                        queueIn.put(o['args'])
                        msg = { 'method' : 'TOKEN', 'args' : 'EMPTY' }
                        self.send(self.successor_address, msg) #ja o recebeu e agora vai enviar um token vazio para o proximo
                        #caso nao esteja vazio e nao seja para ele
                    else:  
                        self.send(self.successor_address, o)


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
                # send confirmation with ticket to client
                orderTicket = uuid.uuid1()
                msg = { 'method' : 'ORDER_RECVD', 'args': { 'orderTicket' : orderTicket, 'client_addr' : foodRequest['args']['client_addr'] }} # send confirmation back to client
                queueOut.put(msg)

                msg = { 'method' : 'COOK', 'args': { 'dest' : 'Cook', 'order' : foodRequest['args']['order'], 'client_addr' : foodRequest['args']['client_addr'], 'orderTicket' : orderTicket }}
                queueOut.put(msg)

                # self.logger.debug("Put %s in the out queue")
                work()
            else:
                work()
