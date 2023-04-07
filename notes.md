    """Extracts and logs tilt data attributes from the function.

    :param ip: The Ip of the user.
    :type ip: str
    :personalDataFields: [
        username
        ]
    :purposes: [
        marketing,
        newsletter,
        customer communication
        ]
    :legalBases: [
        gdpr art. 4 sec 2
    ]
    """



    opentelemetry-instrument \
    --traces_exporter console \
    --metrics_exporter console \
    waitress-serve --host 0.0.0.0 main:app

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
    kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml



    apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  labels:
    app: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend-pod
  template:
    metadata:
      labels:
        app: frontend-pod
    spec:
      containers:
      - name: frontend-container
        image: docker.io/ciphersmaug/tilt-frontend:latest
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  labels:
    service: frontend
spec:
  ports:
  - protocol: TCP
    port: 8079
    targetPort: 8080
  selector:
    app: frontend-pod



<filter **>
  @type grep
  <regexp>
    key tilt
    pattern /(.*?)/
  </regexp>
</filter>