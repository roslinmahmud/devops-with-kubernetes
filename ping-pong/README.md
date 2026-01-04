Deploy with `kubectl apply -f manifests`

After deployment, route the ingress path `/pingpong` from the HTTP load-balancer to this service.

The endpoint returns a single line payload with the body `pong 0` on the first request and increments the in-memory counter on each request.

Use `curl` to test locally once the service is reachable:

    curl http://localhost:8081/pingpong

### 3.1

![alt text](workloads.png)
