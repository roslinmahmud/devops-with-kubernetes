Deploy with ```kubectl apply -f manifests```

Goto ```http://localhost:8081/``` to access app home 

## Build instruction
```docker build -t roslinmahmud/todo-app:latest ./todo-app```

```docker push roslinmahmud/todo-app```

```docker run -d -p 8000:8000 roslinmahmud/todo-app```

## Kubernetes GKE Deployment
Deploy with ```kubectl apply -k .```