def main(port, ring, timeout):
# logger for the main
    logger = logging.getLogger('Restaurant')
    # list with all the nodes
    ring = []

    # initial node on DHT
    node = Node(0, ('localhost', 5000), 0, ('localhost', 5000))
    node.start()
    ring.append(node)
    logger.info(node)

    for i in range(number_nodes-1):
        node = Node(i+1, ('localhost', 5001+i), 0, ('localhost', 5000))
        node.start()
        ring.append(node)
        logger.info(node)

    # Await for DHT to get stable
    time.sleep(10)

    for node in ring:
        node.join()


if __name__ == '__main__':
    main(5)
