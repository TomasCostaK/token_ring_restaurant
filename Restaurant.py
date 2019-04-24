# coding: utf-8

import time
import pickle
import socket
import logging
import uuid
import queue
# import argparse
import threading
from utils import work
from Entity import Entity


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Restaurant(threading.Thread):
    def __init__(self, own_id, address, root_id, root_address):
        threading.Thread.__init__(self)
        self.node_comm = Entity(own_id, address, root_id, root_address, 'Restaurant')
        self.node_comm.start()
        self.logger = logging.getLogger("Restaurant {}".format(self.node_comm.own_id))
        self.queueWaiting = queue.Queue()
        self.equipmentsDict = {'hamburger':0,'drinks':0,'fries':0}

    def lockEquipment(self, args):
        #weird workaround? dpes this make sense?
        #caso a fila esteja vazia atendemos logo este pedido, senao vemos os que estao na fila
        # print('Locking eqpt...')
        if self.equipmentsDict[args['equipment']] == 0:
            self.equipmentsDict[args['equipment']] = 1
            msg ={'method':'ACCESS_GRANTED', 
                    'args': { 'dest': 'Cook' , #mudar esta linha para enviar para o id origem
                              'equipment' : args['equipment'] }}
            self.node_comm.queueOut.put(msg)
        else:
            self.queueWaiting.put(args)
            

    def releaseEquipment(self,args):
        #por o eqpt a 0 caso nao haja ninguem a usar
        # if self.queueWaiting.empty():
        self.equipmentsDict[args['equipment']] = 0
        # else:
        #     self.lockEquipment(self.queueWaiting.get())

    def run(self):
        done = False
        while not done:
            if not self.queueWaiting.empty(): # if request is waiting
                self.lockEquipment(self.queueWaiting.get())
            else:
                foodRequest = self.node_comm.queueIn.get()
            if foodRequest is not None: # if new request came in
                # print('What came in:', foodRequest['method'])
                if foodRequest['method']=='EQPT_REQ':
                    # print('Sending to func lockEquipment')
                    self.lockEquipment(foodRequest['args'])
                elif foodRequest['method']=='EQPT_USED':
                    # print('Sending to func releaseEquipment')
                    self.releaseEquipment(foodRequest['args'])
                # else:
                    # print('Did not enter any')
            else:
                work()
