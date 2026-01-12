## Comparison of Cloud SQL (DBaaS) and Self‑Managed PostgreSQL on GKE

### Initialization and Setup Effort
Using Google Cloud SQL is easier and faster to set up. A database instance can be created in a few minutes using the Google Cloud Console or configuration tools. Google takes care of installing PostgreSQL, setting up storage, and handling basic security settings.

On the other hand, running PostgreSQL on GKE requires more setup work. The team must choose or create a PostgreSQL image, configure PersistentVolumeClaims, manage secrets such as passwords, and make sure the database works correctly inside the Kubernetes cluster. Extra effort is also needed to handle high availability.

### Costs
Cloud SQL uses a pay‑as‑you‑go pricing model. The cost depends on the selected CPU, memory, storage size, and whether high availability is enabled. This can be more expensive compared to self‑managed solutions, but the higher price includes management and maintenance by Google.

Running PostgreSQL on GKE can reduce direct infrastructure costs, especially if the Kubernetes cluster is already used for other services. Storage through PersistentVolumes may be cheaper, and there is no separate DBaaS fee. However, extra costs may appear in the form of development time, monitoring tools, and operational work. 

### Maintenance and Operations
Maintenance is one of the biggest advantages of Cloud SQL. Google automatically handles software updates, security patches, monitoring, replication, and failure recovery. This reduces the risk of errors and lowers the amount of work required from the dev team.

With self‑managed PostgreSQL on GKE, all maintenance tasks must be handled by the owner. This includes updates, backups, performance tuning, monitoring, and recovery planning. Although this approach gives more control over the database configuration, it also increases responsibility and operational complexity.

### Backup Methods and Ease of Use
Cloud SQL includes built‑in backup features. Automated daily backups and point‑in‑time recovery can be enabled easily. Restoring data from a backup is simple and can be done through the Cloud Console.

In contrast, for PostgreSQL on GKE, backups must be set up manually. Common solutions include scheduled database dumps or volume snapshots. While these methods work well, they require careful configuration and regular testing. 

## Deploy Project

Deploy with ```kubectl apply -f manifests```

Goto ```http://localhost:8081/``` to access app home 

## Build instruction
```docker build -t roslinmahmud/todo-app:latest ./todo-app```

```docker push roslinmahmud/todo-app```

```docker run -d -p 8000:8000 roslinmahmud/todo-app```

## Kubernetes GKE Deployment
Deploy with ```kubectl apply -k .```


