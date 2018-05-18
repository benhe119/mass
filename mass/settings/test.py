from .base import *  # noqa
from fakeredis import FakeRedis, FakeStrictRedis

import django_rq.queues
django_rq.queues.get_redis_connection = lambda _, strict: FakeStrictRedis() if strict else FakeRedis()

# Turn on synchronous mode to execute jobs immediately instead of passing them off to the workers
for config in RQ_QUEUES.values():
    config["ASYNC"] = False

DEBUG = True
TESTING = True

RQ_QUEUES['default']['HOST'] = 'localhost'
