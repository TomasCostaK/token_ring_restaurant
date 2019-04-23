# coding: utf-8

import time
import pickle
import socket
import uuid
import logging
import queue
from utils import work
# import argparse
import threading
from Node import Node
from Entity import Entity

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

# Chef
# Restaurant
# Employee
# Receptionist

class Receptionist(Node):
    def __init__(self, own_id, address, root_id, root_address):
        threading.Thread.__init__(self)
        self.node_comm = Entity(own_id, address, root_id, root_address, 'Receptionist')
        self.node_comm.start()
        self.logger = logging.getLogger("Receptionist {}".format(self.node_comm.own_id))

    def run(self):
        done = False
        while not done:
            foodRequest = self.node_comm.queueIn.get()
            if foodRequest is not None:
                # send confirmation with ticket to client
                orderTicket = uuid.uuid1()
                msg = { 'method' : 'ORDER_RECVD', 'args': { 'orderTicket' : orderTicket, 'client_addr' : foodRequest['args']['client_addr'] }} # send confirmation back to client
                self.node_comm.queueOut.put(msg)

                msg = { 'method' : 'COOK', 'args': { 'dest' : 'Cook', 'order' : foodRequest['args']['order'], 'client_addr' : foodRequest['args']['client_addr'], 'orderTicket' : orderTicket }}
                self.node_comm.queueOut.put(msg)

                # self.logger.debug("Put %s in the out queue")
                work()
            else:
                work()
