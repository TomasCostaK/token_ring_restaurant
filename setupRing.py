

# coding: utf-8

import logging
import time
import socket
import pickle
from Node import Node


# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')


def main(number_nodes):
    # logger for the main
    logger = logging.getLogger('Restaurant')
    # list with all the nodes
    ring = []

    tsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tsocket.settimeout(3)

    # initial node on DHT
    node = Node(3, ('localhost', 5003), 3, ('localhost', 5003))
    node.start()
    ring.append(node)
    logger.info(node)

    for i in range(number_nodes):
        if i==3: 
            continue
        node = Node(i, ('localhost', 5000+i), 3, ('localhost', 5003))
        node.start()
        ring.append(node)
        logger.info(node)

    # Await for DHT to get stable
    time.sleep(5)

    msg = { 'method' : 'PRINT_TABLE' }
    tsocket.sendto(pickle.dumps(msg), ('localhost', 5003))

    for node in ring:
        node.join()


if __name__ == '__main__':
    main(5)

