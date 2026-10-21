# Development Log

## Entry 1: Environment setup and reference application deployment

**Date:** 2026-10-21
**Phase:** 1 (Foundation)
**Author:** Khaled

### Objective
Prepare the development environment, create a local Kubernetes cluster, and deploy the reference distributed application (Google Online Boutique) so that later components (telemetry, fault injection, recovery orchestrator) have a running target.

### Environment
- Host: Arch Linux, 16 GB DDR5 RAM
- Tools: Docker, kubectl, Minikube, Helm, Git, Python 3 (versions: Docker version 29.9.1, minikube version v1.38.1, `helm version v4.3.0+gbec5b06)
- Cluster: Minikube, Docker driver, 4 CPUs, 8192 MB memory
- Kubernetes version: v1.35.1

### Steps performed

1. **Installed tools** (`sudo pacman -S --needed docker kubectl minikube helm git python python-pip`), enabled the Docker service and added the user to the `docker` group. Verified with `docker run hello-world`.
2. **Created the repository** with the folders `orchestrator/`, `telemetry/`, `load/`, `docs/` and a README containing the setup instructions for Arch Linux and Windows (WSL2). The repository is private on GitHub.
3. **Started the cluster** with `minikube start --driver=docker --cpus=4 --memory=8192`. The cluster was first started with 6144 MB, then deleted (`minikube delete`) and recreated with 8192 MB, because the memory of an existing Docker-driver cluster cannot be changed.
4. **Verified the cluster** with `kubectl get nodes`: one node `minikube`, status `Ready`, role `control-plane`. The single node acts as both control plane and worker.
5. **Deployed Online Boutique:** downloaded the official manifest into `deploy/online-boutique.yaml` (so the exact version is recorded in the repository) and applied it with `kubectl apply -f deploy/online-boutique.yaml`.
6. **Monitored startup** with `kubectl get pods -w`.

### Results
- All 12 pods reached `1/1 Running` in about 5.5 minutes (the loadgenerator was the last, at about 5m23s). Most of this time was image download.
- `emailservice` restarted once (RESTARTS = 1) during startup and stayed healthy afterwards. Likely cause: its first health probe ran before the service was ready, and Kubernetes restarted the container automatically. This is a small example of the built-in self-healing the project builds on.
- Functional test through `kubectl port-forward deployment/frontend 8080:8080` and `http://localhost:8080`: browsed products, added an item to the cart and completed checkout successfully.

### Evidence
- `docs/img/pods-running.png`: output of `kubectl get pods`
- `docs/img/shop-home.png`: Online Boutique home page

### Issues and notes
- None.
- The manifest includes a built-in `loadgenerator`. It will be replaced later by our own Locust setup so that load is controlled for the experiments.

### Next step
Install telemetry: Prometheus and Grafana via Helm, then OpenTelemetry tracing.
