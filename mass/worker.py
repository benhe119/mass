import sys
import django
from rq import Connection, Worker

sys.path.append('../mass')
django.setup()


with Connection():
    qs = sys.argv[1:] or ['default']
    rq_worker = Worker(qs)
    rq_worker.work()
