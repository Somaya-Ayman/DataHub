# DataHub

https://github.com/acryldata/datahub-helm

[somaya@somaya-pc DataHub]$ helm repo add datahub https://helm.datahubproject.io/
"datahub" has been added to your repositories
[somaya@somaya-pc DataHub]$ kubectl create namespace datahub
namespace/datahub created
[somaya@somaya-pc DataHub]$ kubectl create secret generic mysql-secrets --from-literal=mysql-root-password=<add root password> -n datahub
secret/mysql-secrets created
[somaya@somaya-pc DataHub]$ kubectl create secret generic neo4j-secrets --from-literal=neo4j-password=<add your password> -n datahub
secret/neo4j-secrets created
[somaya@somaya-pc DataHub]$ helm install prerequisites datahub/datahub-prerequisites \
  --namespace datahub
NAME: prerequisites
LAST DEPLOYED: Thu Jun 18 13:26:24 2026
NAMESPACE: datahub
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
[somaya@somaya-pc DataHub]$ kubectl get pods -n datahub
NAME                               READY   STATUS              RESTARTS   AGE
opensearch-cluster-master-0        0/1     Init:0/2            0          14s
prerequisites-kafka-controller-0   0/1     Init:0/1            0          14s
prerequisites-mysql-0              0/1     ContainerCreating   0          14s
[somaya@somaya-pc DataHub]$ kubectl get pods -n datahub -w
NAME                               READY   STATUS              RESTARTS   AGE
opensearch-cluster-master-0        0/1     Init:0/2            0          20s
prerequisites-kafka-controller-0   0/1     Init:0/1            0          20s
prerequisites-mysql-0              0/1     ContainerCreating   0          20s


kubectl get pods -n datahub -w
NAME                               READY   STATUS    RESTARTS   AGE
opensearch-cluster-master-0        1/1     Running   0          13m
prerequisites-kafka-controller-0   1/1     Running   0          13m
prerequisites-mysql-0              1/1     Running   0          13m

helm install datahub datahub/datahub \
  --namespace datahub

kubectl get pods -n datahub -w
NAME                                            READY   STATUS              RESTARTS   AGE
datahub-acryl-datahub-actions-74f54c488-bzw8g   0/1     ContainerCreating   0          10s
datahub-datahub-frontend-97bc74b4d-447km        0/1     ContainerCreating   0          10s
datahub-datahub-gms-68f84c8c68-44s2d            0/1     ContainerCreating   0          10s
datahub-system-update-59p4c                     0/1     Completed           0          117s
datahub-system-update-nonblk-wh6dg              1/1     Running             0          10s
opensearch-cluster-master-0                     1/1     Running             0          28m
prerequisites-kafka-controller-0                1/1     Running             0          28m
prerequisites-mysql-0                           1/1     Running             0          28m
datahub-datahub-frontend-97bc74b4d-447km        0/1     ErrImagePull        0          18s
datahub-datahub-frontend-97bc74b4d-447km        0/1     ImagePullBackOff    0          32s
^C[somaya@somaya-pc DataHub]$ kubectl describe pod -n datahub datahub-datahub-frontend-97bc74b4d-447km
Name:             datahub-datahub-frontend-97bc74b4d-447km
Namespace:        datahub
Priority:         0
Service Account:  datahub-app-sa
Node:             minikube/192.168.49.2
Start Time:       Thu, 18 Jun 2026 13:54:38 +0300
Labels:           app.kubernetes.io/instance=datahub
                  app.kubernetes.io/name=datahub-frontend
                  pod-template-hash=97bc74b4d
Annotations:      <none>
Status:           Pending
IP:               10.244.0.9
IPs:
  IP:           10.244.0.9
Controlled By:  ReplicaSet/datahub-datahub-frontend-97bc74b4d
Containers:
  datahub-frontend:
    Container ID:   
    Image:          docker.io/acryldata/datahub-frontend-react:v1.6.0
    Image ID:       
    Ports:          9002/TCP (http), 4318/TCP (jmx), 4319/TCP (prometheus)
    Host Ports:     0/TCP (http), 0/TCP (jmx), 0/TCP (prometheus)
    State:          Waiting
      Reason:       ImagePullBackOff
    Ready:          False
    Restart Count:  0
    Limits:
      memory:  1400Mi
    Requests:
      cpu:      100m
      memory:   512Mi
    Liveness:   http-get http://:http/admin delay=60s timeout=1s period=30s #success=1 #failure=4
    Readiness:  http-get http://:http/admin delay=60s timeout=1s period=30s #success=1 #failure=4
    Environment:
      DATAHUB_GMS_BASE_PATH_ENABLED:                   false
      ENTITY_VERSIONING_ENABLED:                       false
      ENABLE_PROMETHEUS:                               true
      DATAHUB_GMS_HOST:                                datahub-datahub-gms
      DATAHUB_GMS_PORT:                                8080
      DATAHUB_SECRET:                                  <set to the key 'datahub.gms.secret' in secret 'datahub-gms-secret'>  Optional: false
      DATAHUB_APP_VERSION:                             1.6.0
      DATAHUB_PLAY_MEM_BUFFER_SIZE:                    10MB
      DATAHUB_ANALYTICS_ENABLED:                       true
      KAFKA_BOOTSTRAP_SERVER:                          prerequisites-kafka:9092
      ENFORCE_VALID_EMAIL:                             true
      KAFKA_PRODUCER_COMPRESSION_TYPE:                 none
      KAFKA_PRODUCER_MAX_REQUEST_SIZE:                 5242880
      KAFKA_CONSUMER_MAX_PARTITION_FETCH_BYTES:        5242880
      KAFKA_PROPERTIES_PARTITION_ASSIGNMENT_STRATEGY:  org.apache.kafka.clients.consumer.CooperativeStickyAssignor
      ELASTIC_CLIENT_HOST:                             opensearch-cluster-master
      ELASTIC_CLIENT_PORT:                             9200
      ELASTIC_CLIENT_USE_SSL:                          false
      DATAHUB_TRACKING_TOPIC:                          DataHubUsageEvent_v1
      METADATA_SERVICE_AUTH_ENABLED:                   true
      DATAHUB_SYSTEM_CLIENT_ID:                        __datahub_system
      DATAHUB_SYSTEM_CLIENT_SECRET:                    <set to the key 'system_client_secret' in secret 'datahub-auth-secrets'>  Optional: false
      AUTH_SESSION_TTL_HOURS:                          24
      AUTH_COOKIE_SAME_SITE:                           LAX
      AUTH_COOKIE_SECURE:                              false
      FRONTEND_GRACEFUL_SHUTDOWN_ENABLED:              false
      FRONTEND_BEFORE_SERVICE_UNBIND_TIMEOUT:          10s
      FRONTEND_SERVICE_REQUESTS_DONE_TIMEOUT:          65s
      FRONTEND_SERVICE_STOP_TIMEOUT:                   15s
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-hwtrt (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       False 
  ContainersReady             False 
  PodScheduled                True 
Volumes:
  kube-api-access-hwtrt:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  58s                default-scheduler  Successfully assigned datahub/datahub-datahub-frontend-97bc74b4d-447km to minikube
  Warning  Failed     41s                kubelet            Failed to pull image "docker.io/acryldata/datahub-frontend-react:v1.6.0": Error response from daemon: Head "https://registry-1.docker.io/v2/acryldata/datahub-frontend-react/manifests/v1.6.0": Get "https://auth.docker.io/token?scope=repository%3Aacryldata%2Fdatahub-frontend-react%3Apull&service=registry.docker.io": context deadline exceeded (Client.Timeout exceeded while awaiting headers)
  Warning  Failed     41s                kubelet            Error: ErrImagePull
  Normal   BackOff    40s                kubelet            Back-off pulling image "docker.io/acryldata/datahub-frontend-react:v1.6.0"
  Warning  Failed     40s                kubelet            Error: ImagePullBackOff
  Normal   Pulling    26s (x2 over 56s)  kubelet            Pulling image "docker.io/acryldata/datahub-frontend-react:v1.6.0"
[somaya@somaya-pc DataHub]$ ^C

helm install datahub datahub/datahub   --namespace datahub   --timeout 20m
NAME: datahub
LAST DEPLOYED: Thu Jun 18 13:52:48 2026
NAMESPACE: datahub
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
[somaya@somaya-pc DataHub]$ 

kubectl get pods -n datahub -w
NAME                                            READY   STATUS              RESTARTS   AGE
datahub-acryl-datahub-actions-74f54c488-bzw8g   0/1     ContainerCreating   0          4m8s
datahub-datahub-frontend-97bc74b4d-447km        0/1     ImagePullBackOff    0          4m8s
datahub-datahub-gms-68f84c8c68-44s2d            0/1     ContainerCreating   0          4m8s
datahub-system-update-59p4c                     0/1     Completed           0          5m55s
datahub-system-update-nonblk-wh6dg              0/1     Completed           0          4m8s
opensearch-cluster-master-0                     1/1     Running             0          32m
prerequisites-kafka-controller-0                1/1     Running             0          32m
prerequisites-mysql-0                           1/1     Running             0          32m

minikube ssh
Linux minikube 5.14.0-701.el9.x86_64 #1 SMP PREEMPT_DYNAMIC Mon May 4 09:10:57 UTC 2026 x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
docker@minikube:~$ docker login

USING WEB-BASED LOGIN

i Info → To sign in with credentials on the command line, use 'docker login -u <username>'
         

Your one-time device confirmation code is: GMRK-TBDP
Press ENTER to open your browser or submit your device code here: https://login.docker.com/activate

Waiting for authentication in the browser…
exit
^Clogin canceled
docker@minikube:~$ docker pull acryldata/datahub-frontend-react:v1.6.0
v1.6.0: Pulling from acryldata/datahub-frontend-react
a5bfa7101982: Already exists 
b5d920927575: Already exists 
3e1295fc6e22: Already exists 
1d53393b78f0: Already exists 
9201e51fe8c1: Already exists 
7c6e71c1fdfd: Already exists 
4b14fbe9f208: Already exists 
8d99fd8fea9c: Already exists 
5f460b97a17e: Already exists 
cdea145aa115: Already exists 
4df5fafa2a01: Already exists 
12c3db7f21b8: Already exists 
d3b24c7dac48: Already exists 
b49c09b6ee51: Downloading [==================================>                ]  82.71MB/118.7MB
6cb599a19b84: Waiting 
8447a12ba234: Waiting 
635e5ed3d04e: Waiting 
29b6a971058b: Waiting 
bd9ddc54bea9: Waiting 

taHub]kubectl delete pod -n datahub datahub-datahub-frontend-97bc74b4d-447kmkm
pod "datahub-datahub-frontend-97bc74b4d-447km" deleted from datahub namespace
^C[somaya@somaya-pc DataHub]$ kubectget pods -n datahub -wkm
NAME                                            READY   STATUS        RESTARTS   AGE
datahub-acryl-datahub-actions-74f54c488-bzw8g   1/1     Running       0          17m
datahub-datahub-frontend-97bc74b4d-447km        0/1     Terminating   0          17m
datahub-datahub-frontend-97bc74b4d-hfqd4        0/1     Running       0          5m54s
datahub-datahub-gms-68f84c8c68-44s2d            1/1     Running       0          17m
datahub-system-update-59p4c                     0/1     Completed     0          19m
datahub-system-update-nonblk-wh6dg              0/1     Completed     0          17m
opensearch-cluster-master-0                     1/1     Running       0          45m
prerequisites-kafka-controller-0                1/1     Running       0          45m
prerequisites-mysql-0                           1/1     Running       0          45m
datahub-datahub-frontend-97bc74b4d-447km        0/1     Error         0          18m
datahub-datahub-frontend-97bc74b4d-447km        0/1     Error         0          18m
datahub-datahub-frontend-97bc74b4d-447km        0/1     Error         0          18m
^C[somaya@somaya-pc DataHub]$ kubectl get pods -n datahub -w
NAME                                            READY   STATUS      RESTARTS   AGE
datahub-acryl-datahub-actions-74f54c488-bzw8g   1/1     Running     0          18m
datahub-datahub-frontend-97bc74b4d-hfqd4        0/1     Running     0          6m18s
datahub-datahub-gms-68f84c8c68-44s2d            1/1     Running     0          18m
datahub-system-update-59p4c                     0/1     Completed   0          19m
datahub-system-update-nonblk-wh6dg              0/1     Completed   0          18m
opensearch-cluster-master-0                     1/1     Running     0          46m
prerequisites-kafka-controller-0                1/1     Running     0          46m
prerequisites-mysql-0                           1/1     Running     0          46m

 kubectl get pods -n datahub -w
NAME                                            READY   STATUS      RESTARTS   AGE
datahub-acryl-datahub-actions-74f54c488-bzw8g   1/1     Running     0          19m
datahub-datahub-frontend-97bc74b4d-hfqd4        1/1     Running     0          7m22s
datahub-datahub-gms-68f84c8c68-44s2d            1/1     Running     0          19m
datahub-system-update-59p4c                     0/1     Completed   0          20m
datahub-system-update-nonblk-wh6dg              0/1     Completed   0          19m
opensearch-cluster-master-0                     1/1     Running     0          47m
prerequisites-kafka-controller-0                1/1     Running     0          47m
prerequisites-mysql-0                           1/1     Running     0          47m
^C[somaya@somaya-pc DataHub]kubectl port-forward svc/datahub-datahub-frontend 9002:9002 -n datahubub
Forwarding from 127.0.0.1:9002 -> 9002
Forwarding from [::1]:9002 -> 9002

