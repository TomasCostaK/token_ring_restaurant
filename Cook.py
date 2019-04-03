import utils

#Cook LifeCycle: wairForRequest, requestUtensils, useUtensils, (...)

class Cook(DHT_Node):
	def __init__(self, address, dht_address=None, timeout=3):
		super().__init__(self, address, dht_address, timeout, COOK_ID)

	def waitForRequest():
		#
		super().put(self, key, value, address, client_address)

	def requestUtensils():


	def useUtensils():


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
                    self.add_finger(self.successor_id, self.successor_addr)

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
