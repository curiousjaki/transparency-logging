# transparency-logging
```
podman build -t tilt-frontend ./src/frontend/
podman run -d -p 8080:8080 --name my-container localhost/tilt-frontend:latest 
podman container rm my-container

podman exec -it my-container /bin/bash
```