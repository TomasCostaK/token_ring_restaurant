<<<<<<< HEAD
<<<<<<< HEAD
def main(port, ring, timeout):
# logger for the main
=======


=======
>>>>>>> f5b244b6810c9005753f0eda3349ebe0e17a3c99
# coding: utf-8

import logging
import time
import socket
import pickle
from Node import Node
from Restaurant import Restaurant
from Receptionist import Receptionist
from Cook import Cook
from Employee import Employee

# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')


def main(number_nodes):
    # logger for the main
<<<<<<< HEAD
>>>>>>> 5996cd4d264de76b589019ca8777876af1b12bb4
=======
>>>>>>> f5b244b6810c9005753f0eda3349ebe0e17a3c99
    logger = logging.getLogger('Restaurant')

    # list with all the nodes
    ring = []

<<<<<<< HEAD
<<<<<<< HEAD
    # initial node on DHT
    node = Node(0, ('localhost', 5000), 0, ('localhost', 5000))
=======
    tsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tsocket.settimeout(3)

    # initial node on DHT
    node = Node(3, ('localhost', 5003), 3, ('localhost', 5003))
>>>>>>> 5996cd4d264de76b589019ca8777876af1b12bb4
    node.start()
    ring.append(node)
    logger.info(node)

<<<<<<< HEAD
    for i in range(number_nodes-1):
        node = Node(i+1, ('localhost', 5001+i), 0, ('localhost', 5000))
=======
    for i in range(number_nodes):
        if i==3: 
            continue
        node = Node(i, ('localhost', 5000+i), 3, ('localhost', 5003))
>>>>>>> 5996cd4d264de76b589019ca8777876af1b12bb4
        node.start()
        ring.append(node)
        logger.info(node)

    # Await for DHT to get stable
<<<<<<< HEAD
    time.sleep(10)
=======
=======
    # socket
    tsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tsocket.settimeout(3)

    # create Restaurant 
    restaurant = Restaurant(0, ('localhost', 5000), 0, ('localhost', 5000))
    restaurant.start()
    ring.append(restaurant)
    logger.info(restaurant)

    # create Cook 
    cook = Cook(2, ('localhost', 5002), 0, ('localhost', 5000))
    cook.start()
    ring.append(cook)
    logger.info(cook)

    # create Receptionist 
    receptionist = Receptionist(1, ('localhost', 5001), 0, ('localhost', 5000))
    receptionist.start()
    ring.append(receptionist)
    logger.info(receptionist)
    
    # create Employee 
    employee = Employee(3, ('localhost', 5003), 0, ('localhost', 5000))
    employee.start()
    ring.append(employee)
    logger.info(employee)

    # Await for DHT to get stable
>>>>>>> f5b244b6810c9005753f0eda3349ebe0e17a3c99
    time.sleep(5)

    # Print the ring order for debug
    msg = { 'method' : 'PRINT_RING' }
    tsocket.sendto(pickle.dumps(msg), ('localhost', 5000))

    # Start building the table from the root node
    msg = { 'method' : 'NODE_DISCOVERY', 'args' : { 'table' : {} , 'rounds' : 0 } }
    tsocket.sendto(pickle.dumps(msg), ('localhost', 5000))

    # Await for DHT to get stable
    time.sleep(5)

    # Print the ring order for debug
    msg = { 'method' : 'PRINT_TABLE' }
<<<<<<< HEAD
    tsocket.sendto(pickle.dumps(msg), ('localhost', 5003))
>>>>>>> 5996cd4d264de76b589019ca8777876af1b12bb4
=======
    tsocket.sendto(pickle.dumps(msg), ('localhost', 5000))
>>>>>>> f5b244b6810c9005753f0eda3349ebe0e17a3c99

    for node in ring:
        node.join()

if __name__ == '__main__':
    main(5)
<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> 5996cd4d264de76b589019ca8777876af1b12bb4
=======
>>>>>>> f5b244b6810c9005753f0eda3349ebe0e17a3c99
