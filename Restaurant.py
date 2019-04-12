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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.bind((self.address))
        self.logger = logging.getLogger("Rececionista {}".format(self.own_id))

    def receiveRequest(self,args,address): 
        #if method == ORDER (vem do client)
        for foodKey in args: #depois guardar nas queues correspondentes
            self.logger.debug('Received: %s %s',args[foodKey],foodKey)

        #responder com ticket para o cliente mais tarde dar pickup
        msg = {'method': 'RECV_ORDER', 'args': '12'} #str(uuid.uuid1())
        p = pickle.dumps(msg)
        #self.send(p, addr)
        self.socket.sendto(p, address)
        self.logger.debug('Sending Client Ticket: %s', msg['args'])

    def grillRequest(self,args): #if grillReq
        pass

    def fryRequest(self,args): #if foodReq
        pass

    def drinkRequest(self,args): #if drinkReq
        pass

    def send(self, p, address):
        #Usar o metodo em Node
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
                if o['method'] == 'ORDER':
                    self.receiveRequest(o['args'],addr)


def main():
    rest = Restaurant(0, ('localhost', 5000), 0, ('localhost', 5000))
    rest.run()

if __name__ == '__main__':
    main()
