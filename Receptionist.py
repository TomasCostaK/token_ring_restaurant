import utils

class Receptionist(DHT_Node):
    def __init__(self, address, dht_address=None, timeout=3):
        super().__init__(self, addres, dht_address, timeout, RECEPTIONIST_ID)

    def receive_request(self, key, value, address, client_address):
        if key is not RECEPTIONIST_ID:
            super().put(self, key, value, address, client_address)
        # ...

    def send_request(self, key, address, client_address):
        super().get(self, key, address, client_address)

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

