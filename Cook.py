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
                #o cliente esta pronto a ir buscar
                if foodRequest['method']=='COOK':
                    for comida in foodRequest['args']['order']:  #enviar por cada tipo de comida mas testar so um por agora
                        self.logger.debug('Asking permission to use equipments.')
                        {'method':'TOKEN','args':
                        {'method':'EQPT_REQ', 'args': 
                        {'id': self.node_table['Restaurant'] ,'client_addr': foodRequest['args']['client_addr'], 'equipamento':comida, 'orderTicket': orderTicket }}}
                        queueOut.put(msg)

                #caso a comida esteja pronta
                elif foodRequest['method']=='ACCESS_GRANTED':
                    work()
                    #cook here - basicamente pedir acesso ao restaurante e ver se o equipamento que manda esta dentro de uma lista
                    # se estiver pode usar, e tira o da lista, so quando acaba de usar e que manda o 
                    self.logger.debug('Cooking', foodRequest['args']['orderTicket'])
                    msg={'method':'TOKEN','args':
                        {'method':'EQPT_USED', 'args': 
                        {'id': self.node_table['Restaurant'] ,'client_addr': foodRequest['args']['client_addr'], 'orderTicket': orderTicket }}}
                    queueOut.put(msg)
                    self.logger.debug('Going to use the equipment: %s', "") #mudar isto

                    if allfoodisdone:
                        msg={'method':'TOKEN','args':
                            {'method':'ORDER_DONE', 'args': 
                            {'id': self.node_table['Employee'] ,'client_addr': foodRequest['args']['client_addr'], 'orderTicket': orderTicket }}}
                        queueOut.put(msg)
                        self.logger.debug('Client %s food is ready to pickup.', foodRequest['args']['orderTicket'])
            else:
                work()
