from .base import *

DEBUG = True
TESTING = False

RQ_QUEUES['default']['HOST'] = 'redis'
