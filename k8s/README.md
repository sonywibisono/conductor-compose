# Panduan Kubernetes Netflix/Orkes Conductor

Manifests ini dibuat identik 100% dengan konfigurasi Docker Compose di `compose.yaml`.

## Struktur Direktori

```text
k8s/
├── 00-namespace.yaml        # Namespace 'conductor'
├── 01-configmaps.yaml       # ConfigMap redis.conf & config properties Conductor
├── 02-pvc.yaml              # PVC redis-data-pvc & elasticsearch-data-pvc
├── 03-redis-master.yaml     # Redis Master Deployment + Service
├── 04-redis-replica.yaml    # Redis Replica Deployment + Service (dengan wait initContainer)
├── 05-redis-sentinel.yaml   # Redis Sentinel Deployment + Service (dengan wait initContainer)
├── 06-elasticsearch.yaml    # Elasticsearch 7.17.10 Deployment + Service
├── 07-conductor.yaml        # Conductor Server Deployment + Service
├── 08-conductor-ui.yaml     # Conductor UI Deployment + Service (opsional)
├── kustomization.yaml       # Kustomize manifest
├── conductor-all-in-one.yaml # Seluruh manifest dalam satu file
└── README.md                # Panduan ini
```

---

## Pemetaan dari Compose ke Kubernetes

| Komponen di Docker Compose | Komponen di Kubernetes | Keterangan |
| :--- | :--- | :--- |
| `redis-master` | `Deployment/redis-master` & `Service/redis-master` | Port `6379`, password `SandiMasterRedis`, PVC data volume di `/data` |
| `redis-replica` | `Deployment/redis-replica` & `Service/redis-replica` | Replica ke `redis-master:6379`, menunggu master siap |
| `redis-sentinel` | `Deployment/redis-sentinel` & `Service/redis-sentinel` | Port `26379`, memonitor `redis-master`, menunggu master & replica siap |
| `elasticsearch` | `Deployment/elasticsearch` & `Service/elasticsearch` | Single-node, ES_JAVA_OPTS `-Xms512m -Xmx512m`, PVC data volume |
| `conductor` | `Deployment/conductor` & `Service/conductor` | Port `8080` (API), `5050` / `5000`, `9001` (gRPC), memuat ConfigMap config properties |
| `conductor-ui` | `Deployment/conductor-ui` & `Service/conductor-ui` | Port `9090` (target 80), terhubung ke `http://conductor:8080` |
| `./redis.conf` | `ConfigMap/redis-config` | `appendonly yes` dimount ke `/usr/local/etc/redis/redis.conf` |
| `./config-redis.properties` & `./config-es.properties` | `ConfigMap/conductor-config` | Dimount ke `/app/config/*` |
| Volumes `redis`, `elasticdata` | `PersistentVolumeClaim/redis-data-pvc`, `elasticsearch-data-pvc` | Persistent disk storage |

---

## Cara Menjalankan

### Cara 1: Menggunakan Kustomize (Direkomendasikan)

```bash
kubectl apply -k k8s/
```

### Cara 2: Menggunakan File All-in-One

```bash
kubectl apply -f k8s/conductor-all-in-one.yaml
```

### Cara 3: Menggunakan File Terpisah Berurutan

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmaps.yaml
kubectl apply -f k8s/02-pvc.yaml
kubectl apply -f k8s/03-redis-master.yaml
kubectl apply -f k8s/04-redis-replica.yaml
kubectl apply -f k8s/05-redis-sentinel.yaml
kubectl apply -f k8s/06-elasticsearch.yaml
kubectl apply -f k8s/07-conductor.yaml
kubectl apply -f k8s/08-conductor-ui.yaml
```

---

## Memeriksa Status Pod dan Layanan

```bash
kubectl get pods,svc,pvc -n conductor
```

Untuk melihat log Conductor:

```bash
kubectl logs -f deployment/conductor -n conductor
```

---

## Mengakses Layanan dari Luar Cluster (Port-Forward)

Sama seperti port mapping di Docker Compose (`8080:8080`, `9090:80`, `9200:9200`):

```bash
# Akses Conductor API / Swagger UI (http://localhost:8080)
kubectl port-forward svc/conductor 8080:8080 -n conductor

# Akses Conductor UI (http://localhost:9090)
kubectl port-forward svc/conductor-ui 9090:80 -n conductor

# Akses Elasticsearch (http://localhost:9200)
kubectl port-forward svc/elasticsearch 9200:9200 -n conductor

# Akses Redis Master (localhost:6379)
kubectl port-forward svc/redis-master 6379:6379 -n conductor
```

---

## Cara Menghapus

```bash
kubectl delete -k k8s/
# Atau jika ingin menghapus seluruh namespace beserta isinya:
kubectl delete namespace conductor
```
