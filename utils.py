# coding: utf-8
import time
import math
import random

RESTAURANT_ID = 0
RECEPTIONIST_ID = 1
COOK_ID = 2
EMPLOYEE_ID = 3

def work(mu=2):
    sigma = 0.5
    # generate the number of seconds the work will take
    seconds = math.fabs(random.gauss(mu, sigma))
    # s = np.random.normal(mu, sigma, 1000)
    time.sleep(seconds)
