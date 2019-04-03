# coding: utf-8
RESTAURANT_ID = 0
RECEPTIONIST_ID = 1
COOK_ID = 2
EMPLOYEE_ID = 3

# FNV-1a Hash Function
def dht_hash(text, seed=0, maximum=1024):
    FNV_prime = 16777619
    offset_basis = 2166136261
    h = offset_basis + seed
    for char in text:
        h = h ^ ord(char)
        h = h * FNV_prime
    return h % maximum


def contains_predecessor(identification, predecessor, node):
    if predecessor < node < identification:
        return True
    elif node > predecessor > identification:
        return True
    return False


def contains_successor(identification, successor, node):
    if identification < node <= successor:
        return True
    elif successor < identification and (node > identification or node < successor):
        return True
    return False

