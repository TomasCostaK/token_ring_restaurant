# coding: utf-8

import time
import pickle
import socket
import logging
import uuid
import queue
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Restaurant(Node):
    def __init__(self, own_id, address, root_id, root_address,timeout=3):
        super().__init__(0, address, root_id, root_address)
        self.queueIn = queue.Queue
        self.queueOut = queue.Queue
        self.queueGrill = queue.Queue
        self.queueDrinks = queue.Queue
        self.queueFries = queue.Queue
        #HardcodedAddress do rececionista
        self.sucessor_address = ('localhost', 5001)
        self.sucessor_id = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind((self.address))
        self.logger = logging.getLogger("Rececionista {}".format(self.own_id))

    def receiveRequest(self,objeto,clientAddr): 
        #if method == ORDER (vem do client)
        self.logger.debug('Got from client')
        objeto['args']['idDestino']=self.sucessor_id
        objeto['args']['clientAddr']=clientAddr
        #responder com ticket para o cliente mais tarde dar pickup
        msgDict = {'method': 'TOKEN', 'args': objeto}
        #self.send(p, addr)
        self.logger.debug('Sending %s Ticket: %s', self.sucessor_address, msgDict)
        self.send(msgDict, self.sucessor_address)

    def deliverOrder(self,args,address):

        msgDict = {'method': 'FOOD_DELIVERED', 'args': str(uuid.uuid1())}
        #self.send(p, addr)
        self.logger.debug('Sending %s food to client with ticket: %s', address ,msgDict['args'])
        self.send(msgDict, address)

    def grillRequest(self,args): #if grillReq
        pass

    def fryRequest(self,args): #if foodReq
        pass

    def drinkRequest(self,args): #if drinkReq
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
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.debug('Received O: %s', o)
                if o['method'] == 'ORDER': #vamos enviar o objeto todo e usamos no args do method:token
                    self.receiveRequest(o,addr)
                if o['method'] == 'PICKUP':
                    self.deliverOrder(o['args'],addr)


def main():
    rest = Restaurant(0, ('localhost', 5000), 0, ('localhost', 5000))
    rest.run()

if __name__ == '__main__':
    main()
