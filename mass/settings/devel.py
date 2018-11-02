import socket
from .base import *  # noqa
from fakeredis import FakeRedis, FakeStrictRedis
import django_rq.queues

django_rq.queues.get_redis_connection = lambda _, strict: FakeStrictRedis() if strict else FakeRedis()

# Turn on synchronous mode to execute jobs immediately instead of passing them off to the workers
for config in RQ_QUEUES.values():
    config["ASYNC"] = False

INSTALLED_APPS += [
    'debug_toolbar'
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']

DEBUG = True

RQ_QUEUES['default']['HOST'] = 'localhost'
