# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading
import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Restaurant(Node):
    def __init__(self, own_id, address, root_id, root_address):
	    super().__init__(0, address, root_id, root_address, timeout=3)
	    self.queueIn = queue.Queue
	    self.queueOut = queue.Queue
	    self.logger = logging.getLogger("Rececionista {}".format(self.id))

    def receiveRequest(self,args): 
        #if method == ORDER (vem do client)
        pass
        #responder com ticket para o cliente mais tarde dar pickup

    def grillRequest(self,args): #if grillReq
        pass

    def fryRequest(self,args): #if foodReq
        pass

    def drinkRequest(self,args): #if drinkReq
        pass

    def send(self, address, o):
        #Usar o metodo em Node
        super().send(address,o)


def main():
# logger for the main
    p = self.sock.recvfrom(1024)
    o = pickle.loads(p)
    logger.info('Received ticket %s', o['args'])


if __name__ == '__main__':
    main()
