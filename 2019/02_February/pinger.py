#!/usr/bin/env python3
import sys
from prometheus_client import Histogram, start_http_server
import subprocess
import time

h = Histogram('ping_latency_seconds', 'Time it takes to ping a host', ['target'])

start_http_server(9116)


hosts = sys.argv[1]
hosts = hosts.split(',')

while True:
    # ping servers
    command = 'fping -A -C 10 -f - -i 10 -q -r 0'.split()
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    _, data = p.communicate(input='\n'.join(hosts).encode('utf-8'))
    # update histogram
    # 77.75.79.53      : 3.56 3.68 2.51 2.63 2.93 7.67 2.49 2.86 -
    for line in data.decode('utf-8').splitlines():
        if not line:
            continue
        line = line.strip()
        pinged_host, pings = line.rsplit(':', 1)
        pinged_host = pinged_host.strip()
        pings = pings.strip()
        for value in pings.split():
            if not value:
                continue
            if value=='-':
                value = 99999999999999999
            h.labels(target=pinged_host).observe(float(value)/1000)
    # sleep
    time.sleep(10)

