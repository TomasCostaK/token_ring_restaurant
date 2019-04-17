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
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Receptionist(Node):
    def __init__(self, own_id, address, root_id, root_address,timeout=3):
        super().__init__(1, address, root_id, root_address, timeout=3)
        self.queueIn = queue.Queue
        self.queueOut = queue.Queue
        self.sucessor_addr = ('locahost', 5002)
        self.sucessor_id = 2
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind((self.address))
        self.logger = logging.getLogger("Rececionista {}".format(self.own_id))

    #Acknowledge pedido
    def receiveRequest(self,objeto): 
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
            

    def send(self, o, address):
        p = pickle.dumps(o)
        self.socket.sendto(p, address)

    def recv(self):
        try:
            p, addr = self.socket.recvfrom(1024)
        except socket.timeout:
            return None, None
        else:
            if len(p) == 0:
                return None, addr
            else:
                return p, addr

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
def main():
    recept = Receptionist(1, ('localhost', 5001), 0, ('localhost', 5000))
    recept.run()

if __name__ == '__main__':
    main()
