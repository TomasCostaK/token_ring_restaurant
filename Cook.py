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

class Cook(Node):
	def __init__(self)
		super().__init__(self, 2, address, root_id, root_address, timeout=3)
		self.queueIn = queue.Queue
		self.queueOut = queue.Queue
		self.logger = logging.getLogger("Cozinheiro {}".format(self.id))


	def receiveRequest(self,args): #if method == FOOD_REQ


	def requestGrill(self,args): #if args hambg


	def requestFry(self,args): #if args fries


	def requestDrink(self,args): #if args drinks


	def foodDone(self,args): #avisa o empregado que esta pronto


	def send(self, address, o):
        p = pickle.dumps(o)
        self.socket.sendto(p, address)

def main(port, ring, timeout):


if __name__ == '__main__':
