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

class Employee(Node):
	def __init__(self)
		super().__init__(self, 3, address, root_id, root_address, timeout=3)
		self.queueIn = queue.Queue
		self.queueOut = queue.Queue
		self.logger = logging.getLogger("Empregado {}".format(self.id))


	def insertFood(self,args): #if method == FOOD_DONE
		#Um cozinheiro so cozinha um pedido de cada vez e envia
		#um food_done assim que o pedido esta concluido
		self.logger.debug("Adding %s request to the Delivery Queue", args[client_id])
		#Este args vai ter client_address e o pedido tipo hamburger:1, bebida:2
		self.queueOut.put(args)


	def deliverRequest(self,args): #if method == PICKUP
		self.logger.debug("Delivering order to client %s", args[client_id])
		#Arranjar forma de enviar so o pedido mesmo, mudar formato das mensagens do cliente
		#chosenClient = self.deliveryQueue.get()['client_address']
		self.queueIn.put(args)
		p = pickle.dumps({"method": 'DELIVERED', "args": o[args]})
		if not queueOut.empty():
			self.send(tempClient, p)


	def send(self, address, o):
        p = pickle.dumps(o)
        self.socket.sendto(p, address)

def main(port, ring, timeout):


if __name__ == '__main__':
