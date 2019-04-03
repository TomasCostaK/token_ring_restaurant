# coding: utf-8

import socket
import threading
import logging
import pickle
import collections
import queue
from utils import dht_hash, contains_predecessor, contains_successor

FINGER_TABLE_SIZE = 5
avg_fit = 1024/5

class DHT_Node(threading.Thread):
    def __init__(self, address, dht_address=None, timeout=3, node_id=None):
        threading.Thread.__init__(self)
        self.id = node_id
        self.addr = address
        self.dht_address = dht_address
        # self.finger_table = dict()
        if node_id is None:
            self.node_id = dht_hash(address.__str__())
        if dht_address is None:
            self.successor_id = self.id
            self.successor_addr = address
            self.predecessor_id = None
            self.predecessor_addr = None
            self.inside_dht = True
        else:
            self.inside_dht = False
            self.successor_id = None
            self.successor_addr = None
            self.predecessor_id = None
            self.predecessor_addr = None
        self.req_queue = Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.logger = logging.getLogger("Node {}".format(self.id))

    # def add_finger(self, node_id, node_address):
    #     if len(self.finger_table) < FINGER_TABLE_SIZE:
    #         self.finger_table[node_id] = node_address
    #         self.logger.info('Updated finger table: %s', self.finger_table) 
    #     else:
    #         to_rm = fit_node(node_id)
    #         if to_rm != 0:
    #             self.finger_table[node_id] = node_address
    #             del self.finger_table[to_rm]

    # def fit_node(self, node_id):
    #     # avg_fit = sum(list(self.finger_table)) / FINGER_TABLE_SIZE
    #     for iid in range(list(self.finger_table)):
    #         if (node_id - list(self.finger_table)[iid]) > avg_fit and node_id < list(self.finger_table)[iid+1]:
    #             return list(self.finger_table)[iid+1]
    #     return 0

    # def get_finger_table(self, hash_key):
    #     tmp = sorted(self.finger_table)
    #     tmp.reverse()
    #     self.logger.info('Finger table: %s', tmp)
    #     # TODO: iterate finger table and return closest address
    #     for iid in tmp: # iterate through elements of finger table in reverse order
    #         if hash_key > iid:
    #             return self.finger_table[iid]
    #     # if none fits, return last node
    #     # if len(tmp)==0:
    #     #     return self.addr
    #     self.logger.debug('Returning %s : %s', tmp[0], self.finger_table[tmp[0]])
    #     return self.finger_table[tmp[0]]


    def send(self, address, o):
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

    def node_join(self, args):
        self.logger.debug('Node join: %s', args)
        addr = args['addr']
        identification = args['id']
        # if identification is not None and addr is not None:
        #     self.add_finger(identification, addr)
        if self.id == self.successor_id:
            self.successor_id = identification
            self.successor_addr = addr
            args = {'successor_id': self.id, 'successor_addr': self.addr}
            self.send(addr, {'method': 'JOIN_REP', 'args': args})
        elif contains_successor(self.id, self.successor_id, identification):
            args = {'successor_id': self.successor_id, 'successor_addr': self.successor_addr}
            self.successor_id = identification
            self.successor_addr = addr
            self.send(addr, {'method': 'JOIN_REP', 'args': args})
        else:
            self.logger.debug('Find Successor(%d)', args['id'])
            self.send(self.successor_addr, {'method': 'JOIN_REQ', 'args':args})
        self.logger.info(self)

    # def finger_advertise(self):
    #     if self.successor_id != None:
    #         self.add_finger(self.successor_id, self.successor_addr)


    def notify(self, args):
        self.logger.debug('Notify: %s', args)
        if self.predecessor_id is None or contains_predecessor(self.id, self.predecessor_id, args['predecessor_id']):
            self.predecessor_id = args['predecessor_id']
            self.predecessor_addr = args['predecessor_addr']
        self.logger.info(self)

    def stabilize(self, x, addr):
        self.logger.debug('Stabilize: %s %s', x, addr)
        if x is not None and contains_successor(self.id, self.successor_id, x):
            self.successor_id = x
            self.successor_addr = addr
        args = {'predecessor_id': self.id, 'predecessor_addr': self.addr}
        self.send(self.successor_addr, {'method': 'NOTIFY', 'args':args})

    def put(self, key, value, address):
        self.logger.debug('Put: %s', key)
        # self.logger.debug('%s == %s', self.id, key)
        if self.id == key:
            self.req_queue.put(value)
            self.logger.debug("Sending to %s", address)
            self.send(address, {'method': 'ACK', 'args': { 'value' : value }})
        else:
            # send to DHT
            self.send(self.successor_addr, {'method': 'PUT',  'args':{'key':key, 'value':value }})

    def get(self, key, address):
        return self.req_queue.get()

    def run(self):
        self.socket.bind(self.addr)

        while not self.inside_dht:
            o = {'method': 'JOIN_REQ', 'args': {'addr':self.addr, 'id':self.id}}
            self.send(self.dht_address, o)
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.debug('O: %s', o)
                if o['method'] == 'JOIN_REP':
                    args = o['args']
                    self.successor_id = args['successor_id']
                    self.successor_addr = args['successor_addr']
                    self.inside_dht = True
                    self.logger.info(self)
                    # self.add_finger(self.successor_id, self.successor_addr)

        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.info('O: %s', o)
                if o['method'] == 'JOIN_REQ':
                    self.node_join(o['args'])
                elif o['method'] == 'NOTIFY':
                    self.notify(o['args'])
                elif o['method'] == 'PUT':
                    if 'src_address' in o['args']:
                        self.put(o['args']['key'], o['args']['value'], addr, o['args']['src_address'])
                    else:
                        self.put(o['args']['key'], o['args']['value'], addr)
                elif o['method'] == 'GET':
                    if 'src_address' in o['args']:
                        self.get(o['args']['key'], addr, o['args']['src_address'])
                    else:
                        self.get(o['args']['key'], addr)
                elif o['method'] == 'PREDECESSOR':
                    self.send(addr, {'method': 'STABILIZE', 'args': self.predecessor_id})
                elif o['method'] == 'STABILIZE':
                    self.stabilize(o['args'], addr)
            else:
                # Ask for predecessor to start the stabilize process
                self.send(self.successor_addr, {'method': 'PREDECESSOR'})

    def __str__(self):
        return 'Node ID: {}; DHT: {}; Successor: {}; Predecessor: {}'\
            .format(self.id, self.inside_dht, self.successor_id, self.predecessor_id)

    def __repr__(self):
        return self.__str__()
