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
	def __init__(self)
		super().__init__(self, 0, address, root_id, root_address, timeout=3)
		self.queueIn = queue.Queue
		self.queueOut = queue.Queue
		self.logger = logging.getLogger("Rececionista {}".format(self.id))


	def receiveRequest(self,args): #if method == ORDER (vem do client)
	#responder com ticket para o cliente mais tarde dar pickup

	def grillRequest(self,args): #if grillReq


	def fryRequest(self,args): #if foodReq


	def drinkRequest(self,args): #if drinkReq


	def send(self, address, o):


def main(port, ring, timeout):
# logger for the main
    logger = logging.getLogger('Restaurant')
    # list with all the nodes
    ring = []

    # initial node on DHT
    node = Node(0, ('localhost', 5000), 0, ('localhost', 5000))
    node.start()
    ring.append(node)
    logger.info(node)

    for i in range(number_nodes-1):
        node = Node(i+1, ('localhost', 5001+i), 0, ('localhost', 5000))
        node.start()
        ring.append(node)
        logger.info(node)

    # Await for DHT to get stable
    time.sleep(10)

    for node in ring:
        node.join()


if __name__ == '__main__':
    main(5)