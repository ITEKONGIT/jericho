def queueRequests(target, wordlists):
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=100,
        requestsPerConnection=1000,
        pipeline=True,
        maxQueueSize=20000
    )
    
    # Send the attached request as-is, 10000 times
    for i in range(10000):
        engine.queue(target.req)

def handleResponse(req, interesting):
    if interesting:
        table.add(req)