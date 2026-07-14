def queueRequests(target, wordlists):
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=100,
        requestsPerConnection=1000,
        pipeline=True,
        maxQueueSize=20000
    )
    
    while True:
        engine.queue(target.req)

def handleResponse(req, interesting):
    if interesting:
        table.add(req)