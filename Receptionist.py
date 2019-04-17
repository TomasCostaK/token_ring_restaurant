# coding: utf-8

import time
import pickle
import socket
import uuid
import logging
import queue
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Receptionist(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        self.queueIn = queue.Queue()
        self.queueOut = queue.Queue()
        # self.sucessor_addr = ('locahost', 5002)
        # self.sucessor_id = 2
        self.logger = logging.getLogger("Receptionist {}".format(self.own_id))

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
                elif o['method'] == 'TOKEN' and o['args']['args']['idDestino']==self.own_id: #vamos enviar o objeto todo e usamos no args do method:token
                    self.logger.debug("This token is for me")
                    if o['args']['method']=='ORDER':
                        self.receiveRequest(o['args'])
                    #Verifica sempre se há comida para pedir
                    self.askFoodCook(o['args'])


# def main():
#     recept = Receptionist(1, ('localhost', 5001), 0, ('localhost', 5000))
#     recept.run()

# if __name__ == '__main__':
#     main()
