# Verified Recovery

A deterministic, policy-guided resilience orchestrator for distributed applications.
Damascus University, Computer and Automation Engineering, 2026-2027.

## Repository layout

| Folder | Purpose |
|---|---|
| `orchestrator/` | Recovery state machine, policies, actions, verification (FastAPI) |
| `telemetry/` | Prometheus, Grafana, OpenTelemetry, Chaos Mesh configs, dataset |
| `load/` | Load generation, plant identification, PI controller |
| `docs/` | Documentation |

## Environment setup

Required tools: Docker, kubectl, Minikube, Helm, Git, Python 3.

### Arch Linux

```bash
sudo pacman -S --needed docker kubectl minikube helm git python python-pip
sudo systemctl enable --now docker.service
sudo usermod -aG docker $USER   # then log out and back in
docker run hello-world
```

### Windows (via WSL2)

1. In PowerShell (Administrator): `wsl --install -d Ubuntu`, then restart.
2. Install Docker Desktop and enable Ubuntu under Settings > Resources > WSL Integration.
3. Give WSL at least 4 CPUs and 6-8 GB RAM.
4. In the Ubuntu terminal:

```bash
sudo apt update && sudo apt install -y git python3 python3-pip python3-venv curl

curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Work inside the WSL filesystem (`~/`), not `/mnt/c`.

### Start the cluster (all systems)

```bash
minikube start --driver=docker --cpus=4 --memory=6144
kubectl get nodes    # expected: minikube   Ready
```

### Python environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python packages only inside the venv.

## Phase 1 status

- [x] Environment setup
- [ ] Deploy Online Boutique
- [ ] Telemetry (Prometheus, Grafana, OpenTelemetry)
- [ ] Orchestrator skeleton and system interfaces
- [ ] Fault injection smoke test
- [ ] Load generation and baseline
