from multiprocessing import cpu_count
from proxyservice import settings

workers_initial = cpu_count()
workers = round(workers_initial * 2 + 1)

if workers < 1 or settings.IS_DEVELOPMENT:
    workers = 1


bind = f'0.0.0.0:{settings.FLASK_RUN_PORT}'
worker_class = 'gevent'
timeout = 1500
