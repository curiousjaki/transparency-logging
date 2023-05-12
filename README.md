# Transparency Logging Example

## Requirements

- git
- running kubernetes cluster
- docker
- skaffold

## Quick start

```
git clone git@github.com:ciphersmaug/transparency-logging.git
skaffold run
```

Then set up the elasticsearch index to enable event log retrieval.
Utilize Kibana for an easy Index set-up: http://localhost/5601
```
kubectl -n elastic-kibana port-forward svc/kibana 5601
```

Afterwards you can check out the mining dashboard under: http://localhost:8501
```
kubectl port-forward svc/dashboard-service 8501
```


## Interesting port-forwards
```
kubectl port-forward svc/frontend-service 8081
kubectl port-forward svc/jaeger 16686

kubectl -n elastic-kibana port-forward svc/kibana 5601
kubectl port-forward svc/dashboard-service 8501

kubectl -n elastic-kibana port-forward svc/elasticsearch 9200
```

## Destroy deployment
```
skaffold delete
```