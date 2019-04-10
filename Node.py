# coding: utf-8

import time
import pickle
import socket
import logging
# import argparse
import threading

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

class Node(threading.Thread):
    def __init__(self, id, address, timeout=3):
        self.id = id
        self.address = address
        self.successor_id = None
        self.successor_addr = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.logger = logging.getLogger("Node {}".format(self.id))



def main(port, ring, timeout):


if __name__ == '__main__':
