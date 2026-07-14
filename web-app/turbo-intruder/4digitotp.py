def queueRequests(target, wordlists):
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=100, 
        requestsPerConnection=1000, 
        pipeline=True,
        maxQueueSize=20000
    )
    
    for i in range(10000):
        payload = "{:04}".format(i)
        engine.queue(target.req, payload)

def handleResponse(req, interesting):
    if interesting:
        table.add(req)