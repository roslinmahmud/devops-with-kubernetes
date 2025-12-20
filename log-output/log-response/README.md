Deploy with ```kubectl apply -f manifests```

Goto ```http://localhost:8000/docs``` to request the current status (timestamp and the random string) 

### Build and Push 
```docker build -t roslinmahmud/log-response ./log-output/log-response```

```docker push roslinmahmud/log-response```