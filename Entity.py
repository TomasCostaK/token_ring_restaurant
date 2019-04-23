# coding: utf-8

import time
import pickle
import socket
import logging
import queue
# import argparse
import threading
from Node import Node

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Entity(Node):
    def __init__(self, own_id, address, root_id, root_address, name='Node', timeout=3):
        Node.__init__(self, own_id, address, root_id, root_address)

    def run(self):
        done = False
        while not done:
            p, addr = super().recv()
            if p is not None:
                o = pickle.loads(p)
                if o['method'] == 'ORDER': # need to wrap in TOKEN
                    msg = { 'method' : 'TOKEN' , 
                            'args' : { 'method' : o['method'], 
                                       'args' : { 'client_addr' : addr, 
                                                  'order' : o['args'] }, 
                                       'dest_id' : self.node_table['Receptionist'] }}
                    super().send(self.successor_address, msg)

                elif o['method'] == 'PICKUP': # need to wrap in TOKEN
                    msg = { 'method' : 'TOKEN' , 
                            'args' : { 'method' : o['method'], 
                                       'args' : { 'client_addr' : addr, 
                                                  'order' : o['args'] }, 
                                       'dest_id' : self.node_table['Employee'] }}
                    super().send(self.successor_address, msg)

                elif o['method'] == 'TOKEN': # send to worker
                    if o['args']=='EMPTY':
                        if not self.queueOut.empty():
                            nextMessage = self.queueOut.get()
                            if nextMessage != None:
                                # wrap in TOKEN
                                if nextMessage['method'] == 'ORDER_RECVD':
                                    super().send(nextMessage['args']['client_addr'], nextMessage)

                                elif nextMessage['method']=='DELIVER': #enviar pra cliente caso method seja deliver
                                    msg = { 'method':'DELIVER' ,
                                            'args': { 'ticket': nextMessage['args']['orderTicket']
                                            }}

                                    clientAddress = nextMessage['args']['client_addr']
                                    self.logger.debug('Sending client %s food', nextMessage['args']['orderTicket'])
                                    super().send(clientAddress, msg)

                                else:
                                    msg = { 'method' : 'TOKEN', 'args' : nextMessage }
                                    msg['args']['dest_id'] = self.node_table[nextMessage['args']['dest']]
                        
                                    #permite mais que um cozinheiro, pois enviamos na mensagem que cozinheiro e que pediu e podemos-lhe responder
                                    if nextMessage['method'] == 'EQPT_REQ':
                                        msg['args']['args']['cookReq'] = self.node_table[nextMessage['args']['cook']]
                                    super().send(self.successor_address, msg)
                                    self.logger.debug('Sending Token: %s', nextMessage['method'])
                        else:
                            super().send(self.successor_address, o)
                    elif o['args']['dest_id']==self.own_id:
                        self.logger.debug('Sending object to Worker Thread')
                        self.queueIn.put(o['args'])
                        msg = { 'method' : 'TOKEN', 'args' : 'EMPTY' }
                        super().send(self.successor_address, msg) #ja o recebeu e agora vai enviar um token vazio para o proximo
                    else:  
                        super().send(self.successor_address, o)


