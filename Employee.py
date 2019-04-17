# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading
import queue
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Employee(Node):
    def __init__(self, own_id, address, root_id, root_address):
        super().__init__(own_id, address, root_id, root_address)
        self.queueIn = queue.Queue()
        self.queueOut = queue.Queue()
        self.logger = logging.getLogger("Employee {}".format(self.own_id))

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

    def run(self):
        self.socket.bind(self.address)

        self.neighbor_advertise()

        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.info('O: %s', o)
                if o['method'] == 'NODE_JOIN':
                    self.neighbor_ack(o['args'])
                elif o['method'] == 'PRINT_RING':
                    self.print_ring()
                elif o['method'] == 'PRINT_TABLE':
                    self.print_table()
                elif o['method'] == 'NODE_DISCOVERY':
                    self.propagate_table(o['args'])
                elif o['method'] == 'FOOD_DONE':
                    self.insertFood(o['args'])
                elif o['method'] == 'PICKUP':
                    self.deliverRequest(o['args'])

