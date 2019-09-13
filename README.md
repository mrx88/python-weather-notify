![](https://github.com/mrx88/python-weather-notify/workflows/Weather%20Notify%20CI/CD%20pipeline/badge.svg)
# python-weather-notify

# Background

Weather Notify is a personal fun/experiment project to parse Foreca weather site and notify if raining probability is over 60%.

Automated notification is sent to Microsoft Teams web hook and SMS to defined mobile number using Twilio SMS API.

Weather Notify is deployed to k8s cluster as cronjob resource, it has fully automated CI/CD pipeline as code defined using GitHub actions.

# Prerequisites

1. Microsoft Teams [web hook](https://docs.microsoft.com/en-us/microsoftteams/platform/concepts/connectors/connectors-using) configured
2. [Twilio SMS](https://www.twilio.com/docs/sms) configured
3. [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) deployed to k8s cluster:

````
kubectl create secret generic ms-teams-token --from-literal=hook=<webhooktoken>
kubectl create secret generic twilio-sid --from-literal=value=<twilio_sid>
kubectl create secret generic twilio-token --from-literal=value=<twilio_token>
kubectl create secret generic twilio-sms-from --from-literal=value=<twilio_sms_from_number>
kubectl create secret generic twilio-sms-to --from-literal=value=<twilio_sms_to_number>
````

# Weather Notify

Usage:
```
$ ./foreca_notify.py --help
Usage: foreca_notify.py [OPTIONS]

  Main function

Options:
  --country TEXT  Define Country
  --city TEXT     Define City
  --help          Show this message and exit.
  ```
python:3.7.2 has been used for developing.

# Deployment

Build docker image and push it to registry. In this example, Azure Container Registry has been used.

K8s cronjob resource is used for executing weather notify container after every 5min in k8s cluster.

For deploying the cronjob k8s resource to k8s cluster:

```
kubectl apply -f k8s/cron.yaml
```

# Verify

```
# Check if cronjob has been created

kubectl get cronjobs
NAME                          SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
foreca-weather-notification   */5 * * * *   False     0        <none>          58s
```

```
# Check pod details and logs

kubectl describe pods/foreca-weather-notification-1567963500-txfhs 
Name:               foreca-weather-notification-1567963500-txfhs
Namespace:          default
Priority:           0
PriorityClassName:  <none>
Node:               aks-nodepool1-17813710-vmss000000/10.240.0.4
Start Time:         Sun, 08 Sep 2019 20:25:07 +0300
Labels:             controller-uid=9a5efb8b-d25d-11e9-a531-8af3d7ece86b
                    job-name=foreca-weather-notification-1567963500
Annotations:        <none>
Status:             Succeeded
IP:                 10.244.0.61
Controlled By:      Job/foreca-weather-notification-1567963500
Containers:
  foreca-weather-notification:
    Container ID:   docker://683fad374968e50a892fb4447cf74de5366553169678d8044f7ea7dee4ce180d
    Image:          martinacrdev.azurecr.io/python-weather-notify:latest
    Image ID:       docker-pullable://martinacrdev.azurecr.io/python-weather-notify@sha256:366cd30ad38c40801f362649ee397b1d8300a9b38f53e14c9ea898c8fa44635d
    Port:           <none>
    Host Port:      <none>
    State:          Terminated
      Reason:       Completed
      Exit Code:    0
      Started:      Sun, 08 Sep 2019 20:25:17 +0300
      Finished:     Sun, 08 Sep 2019 20:25:18 +0300
    Ready:          False
    Restart Count:  0
    Limits:
      cpu:     500m
      memory:  128Mi
    Requests:
      cpu:     500m
      memory:  128Mi
    Environment:
      MS_TEAMS_TOKEN:   <set to the key 'hook' in secret 'ms-teams-token'>    Optional: false
      TWILIO_SID:       <set to the key 'value' in secret 'twilio-sid'>       Optional: false
      TWILIO_TOKEN:     <set to the key 'value' in secret 'twilio-token'>     Optional: false
      TWILIO_SMS_FROM:  <set to the key 'value' in secret 'twilio-sms-from'>  Optional: false
      TWILIO_SMS_TO:    <set to the key 'value' in secret 'twilio-sms-to'>    Optional: false
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-mptcn (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             False
  ContainersReady   False
  PodScheduled      True
Volumes:
  default-token-mptcn:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-mptcn
    Optional:    false
QoS Class:       Guaranteed
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type    Reason          Age    From                                        Message
  ----    ------          ----   ----                                        -------
  Normal  Scheduled       7m41s  default-scheduler                           Successfully assigned default/foreca-weather-notification-1567963500-txfhs to aks-nodepool1-17813710-vmss000000
  Normal  Pulling         7m40s  kubelet, aks-nodepool1-17813710-vmss000000  pulling image "martinacrdev.azurecr.io/python-weather-notify:latest"
  Normal  Pulled          7m36s  kubelet, aks-nodepool1-17813710-vmss000000  Successfully pulled image "martinacrdev.azurecr.io/python-weather-notify:latest"
  Normal  Created         7m31s  kubelet, aks-nodepool1-17813710-vmss000000  Created container
  Normal  Started         7m31s  kubelet, aks-nodepool1-17813710-vmss000000  Started container
  Normal  SandboxChanged  7m29s  kubelet, aks-nodepool1-17813710-vmss000000  Pod sandbox changed, it will be killed and re-created.
  
```

```
# Check pod (weather notify application) logs

kubectl logs pods/foreca-weather-notification-1567963500-txfhs     
2019-09-08 17:25:17,871 - DEBUG - Starting new HTTP connection (1): www.foreca.com:80
2019-09-08 17:25:17,964 - DEBUG - http://www.foreca.com:80 "GET /Estonia/Viimsi?details=20160804&units=eu&tf=24h HTTP/1.1" 302 None
2019-09-08 17:25:17,966 - DEBUG - Starting new HTTPS connection (1): www.foreca.com:443
2019-09-08 17:25:18,430 - DEBUG - https://www.foreca.com:443 "GET /Estonia/Viimsi?details=20160804&units=eu&tf=24h HTTP/1.1" 200 None
2019-09-08 17:25:18,547 - DEBUG - Hour:  21:00, Rain: 16%, Humidity: 70%, Temp: 61°, Now time: 2019-09-08 17:25:18.546984, Alerttime: 2019-09-08 17:00:00
2019-09-08 17:25:18,547 - DEBUG - Alert time: 2019-09-08 17:00:00
2019-09-08 17:25:18,547 - INFO - Alert message: OK:  Raining probability is low in Viimsi (16%)
```

# CI/CD pipeline (GitHub Actions)

For experimenting with Github Actions beta, I've set up CI/CD pipeline (as code) accordingly to automatically build, test and deploy to k8s cluster.

Pipeline jobs are defined accordingly:

1) Build
 * Sets up pipenv and installs dependencies from Pipfile
 * Does code linting using pycodestyle(pep8) and pylint
 * Checks for code vulnerabilities using pipenv check
 * Builds Docker image from Dockerfile
 * Pushes Docker image to Azure Container Registry

2) Test
* Sets up [Kind](https://github.com/kubernetes-sigs/kind) k8s testing cluster
* Pulls the Docker image from ACR
* Starts the weather notify container for testing
* Creates testing secrets for Kind k8s cluster
* Deploys the cronjob resource to Kind k8s cluster
* Lists running cronjobs.

3) Deploy 
* Deploys the cronjob resource to real k8s cluster
* Lists running cronjobs.

**NOTE:** Environment variables should be defined accordingly in GitHub secrets.
 
Pipeline as code .yml configuration is defined in [.github/workflows/main.yml](.github/workflows/main.yml)


# Development
I've used [pipenv](https://github.com/pypa/pipenv) for development, when contributing install dependencies automatically from Pipfile:

```

# Use pipenv shell
pipenv shell

# Install dependencies from Pipfile
pipenv install

# Or install both develop and default packages from Pipfile
pipenv install --dev

# Lock and declare all dependencies once development is done 
pipenv lock
```
