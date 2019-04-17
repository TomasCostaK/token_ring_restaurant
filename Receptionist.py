# coding: utf-8

import time
import pickle
import socket
import uuid
import logging
import queue
import utils.py
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Receptionist(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        global queueIn = Queue()
        global queueOut = Queue()
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
                elif o['method'] == 'TOKEN' and o['args']['args']['id']==self.own_id: # send to worker
                    queueIn.put(o['args'])
                else: # send to next
                    self.send(self.sucessor_addr, o)

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def receiveRequest(self,objeto): #Acknowledge pedido
        # adicionar a fila de pedidos a entregar ao cook, ex msg: {'method': 'ORDER', 'args': {'hamburger': 1, 'idDestino': 1}}
        objeto['args']['idDestino']=self.sucessor_id
        msg = {'method':'ORDER_RECVD', 'args': str(uuid.uuid1())} #send clients unique ticket
        self.logger.debug("Received: %s , order is now in the queue", objeto['args'])
        self.queueOut.put(objeto,False)
        msgDict = {'method': 'TOKEN', 'args': ''}
        #Enviar para o cliente a dizer que recebeu
        self.send(msg, objeto['args']['clientAddr'])
        #Enviar o token vazio para dizer que pode ser usado
        self.send(msgDict, self.sucessor_addr)

    def askFoodCook(self,args):
        if args=='': #esta vazio podemos usar
            pass

    def run(self):
        done = False
        while not done:
            foodRequest = commsThread.getInQueue()
            if foodRequest is not None:
                self.logger.debug('Got request: %s', foodRequest)
                client_address=foodRequest['args']['client_addr']
                orderTicket = uuid.uuid1()
                msg={'method':'TOKEN','args':
                    {'method':'COOK', 'args': 
                    {'id': self.node_table['Chef'], 'order': foodRequest['args']['order'], 'client_addr':request['args']['order'], 'orderTicket': orderTicket }}}
                commsThread.putOutQueue()
                self.send(client_address,{'method':'ORDER_RECVD','args':orderTicket}) #warn client the order is confirmed
                self.logger.debug("Put %s in the out queue")
                work()
            else:
                work()