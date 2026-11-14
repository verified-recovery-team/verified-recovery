# Chaos Mesh Setup and Pod Recovery Experiments
- **Contributor:** Musab Zuriqat
- **Date:** 2026-11-14
- **Project:** Verified Recovery
## 1. Objective

Install Chaos Mesh in the local Kubernetes cluster and perform PodChaos experiments against the Online Boutique application to test Kubernetes self-healing capabilities and measure the time required for a replacement Pod to become ready.

## 2. Environment

- Kubernetes: Minikube
- Container Runtime: containerd
- Helm: v3.22.1
- Chaos Mesh: v2.8.8
- Application: Google Online Boutique

## 3. Chaos Mesh Installation

Added the Chaos Mesh Helm repository and updated the repository information:

```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
```

Created a namespace named `chaos-mesh` and installed Chaos Mesh using Helm.

Configuration file: `telemetry/chaos-mesh-values.yaml`

```yaml
chaosDaemon:
  runtime: containerd
  socketPath: /run/containerd/containerd.sock

dashboard:
  securityMode: true
```

Installation command:

```bash
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --version 2.8.8 \
  -n chaos-mesh \
  -f telemetry/chaos-mesh-values.yaml
```

After installation, all six Chaos Mesh Pods reached the `Running` state, with all containers ready (`1/1`).

## 4. First Experiment: PodChaos

Created the following file:

`telemetry/chaos/pod-kill-cartservice.yaml`

The configuration targets one Pod belonging to the cartservice deployment.

Experiment configuration:

- Kind: `PodChaos`
- Action: `pod-kill`
- Mode: `one`
- Target namespace: `default`
- Target label: `app=cartservice`

Applied the experiment using:

```bash
kubectl apply -f telemetry/chaos/pod-kill-cartservice.yaml
```

The original cartservice Pod was terminated, and Kubernetes created a replacement Pod through the Deployment controller. This demonstrated Kubernetes self-healing behavior.

After the experiment, the PodChaos resource was deleted:

```bash
kubectl delete -f telemetry/chaos/pod-kill-cartservice.yaml
```

No precise recovery-time measurement was collected during this first experiment.

## 5. Second Experiment: Recovery Time Measurement

The experiment was repeated to obtain a more useful recovery-time measurement.

A monitoring loop repeatedly checked the cartservice Pod status, using a configured sleep interval of 0.2 seconds between checks.

The experiment start time was recorded before applying the fault:

```text
T0 = 19:06:18.396
```

The original Pod was replaced by a new Pod:

```text
cartservice-574c7f4cdd-b4s6p
```

The replacement Pod was first observed in the `Pending` state. It then entered the `Running` state while remaining `READY=false`.

The first observation of `READY=true` occurred at:

```text
T1 = 19:06:51.171
```

### Observed Recovery Time Calculation

```text
Recovery Time = T1 - T0
              = 32.775 seconds
              ≈ 32.8 seconds
```

This value represents the observed time from the start of the fault-injection command until the replacement Pod was first observed as ready.

The effective monitoring interval was approximately 0.4–0.5 seconds because of `kubectl` command execution overhead.

**Important:** This measurement represents Pod recovery time until the replacement Pod became Ready. It does not represent an exact end-to-end application service recovery time.

## 6. Application Functional Verification

After the replacement Pod became ready:

1. Opened the Online Boutique frontend.
2. Opened a product page.
3. Attempted to add the product to the shopping cart.

The user confirmed that the application was working correctly and that adding the product to the cart succeeded.

This verified that the application's basic functionality was restored after recovery. However, no exact timestamp was recorded for the successful shopping-cart operation.

## 7. Cleanup and Final Verification

Deleted the PodChaos resource after the second experiment:

```bash
kubectl delete -f telemetry/chaos/pod-kill-cartservice.yaml
```

The final verification showed:

- All 12 Online Boutique Pods were `Running`, with all containers ready (`1/1`).
- All 6 Chaos Mesh Pods were `Running`, with all containers ready (`1/1`).
- The replacement cartservice Pod was healthy.
- No container restarts were reported in the final Pod listing.

## 8. Results and Limitations

The experiments demonstrated that Kubernetes can automatically recreate a terminated Pod when it is managed by a Deployment.

The second experiment measured an observed Pod recovery time of approximately **32.8 seconds**.

The application's basic functionality was also verified after recovery.

Limitations:

- The measurement represents the time required for the replacement Pod to become Ready, not the complete service recovery time.
- No exact timestamp was recorded for the successful shopping-cart operation.
- The impact of the failure on p95 latency and error rates has not yet been measured.

## 9. Next Steps

1. Complete the Chaos Mesh experiment documentation.
2. Configure OpenTelemetry Collector to receive traces from supported Online Boutique services.
3. Convert trace data into Prometheus metrics.
4. Expose latency and error-rate metrics in Prometheus and Grafana.
5. Document which services support tracing and which do not.
