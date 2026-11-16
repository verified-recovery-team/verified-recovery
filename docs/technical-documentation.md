# Verified Recovery
## Technical Documentation

**Institution:** Damascus University  
**Department:** Computer and Automation Engineering  
**Academic Year:** 2026–2027  
**Project:** Verified Recovery — A deterministic, policy-guided resilience orchestrator for distributed applications

---

# 1. Project Overview

Verified Recovery is a project focused on improving the resilience and recoverability of distributed applications.

Modern distributed applications consist of multiple services that communicate with one another. A failure or degradation in one service can affect other services and reduce the availability of the entire application.

Kubernetes provides basic self-healing capabilities, such as restarting failed containers and maintaining the desired number of replicas. However, these mechanisms do not provide a complete application-level recovery process involving failure diagnosis, controlled recovery decisions, verification of the result, and incident documentation.

Verified Recovery aims to build on top of these capabilities by introducing an external orchestrator that can observe application and infrastructure conditions, interact with Kubernetes, and eventually coordinate a structured recovery process.

The current implementation establishes the foundation of this system: a deployed distributed application, infrastructure monitoring, and a FastAPI-based orchestrator that can inspect metrics, interact with Kubernetes, perform deployment operations, and store incident records.

# 2. Project Objectives

The overall project objectives are:

1. Deploy a realistic distributed application in a Kubernetes environment.
2. Collect infrastructure and application telemetry.
3. Provide an external interface for observing the state of the application.
4. Enable controlled operations on Kubernetes deployments.
5. Maintain records of incidents and their associated information.
6. Develop a deterministic recovery workflow.
7. Verify whether recovery actions achieve their intended result.
8. Provide a documented and reproducible experimental environment.

The first five objectives have an implemented foundation. Automated diagnosis, policy-driven recovery, and post-action verification remain future development work.

# 3. System Architecture

## 3.1 Current architecture

The current implementation consists of four main parts:

**1. Distributed application**

Google Online Boutique is deployed in Kubernetes. It provides a realistic microservices environment containing 12 services.

**2. Monitoring infrastructure**

Prometheus collects metrics from the Kubernetes environment. Grafana provides dashboards for observing infrastructure behavior.

**3. Recovery orchestrator**

A Python application built with FastAPI exposes REST endpoints. It communicates with the Kubernetes API and Prometheus to retrieve information and perform selected operations.

**4. Incident storage**

SQLite provides persistent storage for incident records submitted through the orchestrator API.

## 3.2 Architecture flow

The current system supports the following interactions:

- Kubernetes exposes cluster and deployment information.
- Prometheus provides collected metrics.
- The orchestrator retrieves pod information and CPU metrics.
- The orchestrator can request deployment restarts and replica changes.
- Incident records can be submitted and retrieved through the API.
- Grafana provides a visual representation of monitored infrastructure metrics.

The intended future recovery architecture is:

**Detection → Diagnosis → Policy Decision → Recovery Action → Verification → Fallback**

This is the target architecture, not a claim that the complete automated workflow has already been implemented.

# 4. Technologies Used

| Technology | Purpose | Why it was selected |
|---|---|---|
| Python | Main programming language | Suitable for system integration, automation, and backend development |
| FastAPI | Orchestrator REST API | Provides a structured way to expose system operations and integrate Python components |
| Kubernetes | Container orchestration | Manages distributed services, deployments, replicas, and workload recovery |
| Minikube | Local Kubernetes cluster | Allows experimentation without requiring a production cluster |
| Docker | Container runtime and image management | Runs the containerized application and supports the local Kubernetes environment |
| Google Online Boutique | Reference distributed application | Provides a realistic microservices workload for experiments |
| Prometheus | Metrics collection and querying | Provides time-series infrastructure metrics and PromQL queries |
| Grafana | Monitoring dashboards | Makes infrastructure behavior and metric changes observable |
| Helm | Kubernetes package management | Simplifies deployment and configuration of monitoring components |
| Kubernetes Python Client | Kubernetes integration | Allows the orchestrator to inspect and modify Kubernetes resources programmatically |
| HTTPX | HTTP communication | Provides the HTTP client used to communicate with Prometheus |
| SQLite | Incident persistence | Provides lightweight persistent storage without requiring a separate database server |
| Pydantic Settings | Configuration management | Loads application configuration from environment variables and an environment file |
| Pytest | Automated testing | Verifies application integrations and storage behavior |
| Git and GitHub | Version control and collaboration | Tracks implementation milestones and supports collaboration |

## 4.1 Why FastAPI?

The orchestrator needs to expose operations to external clients and provide a clear interface between the monitoring/recovery logic and the Kubernetes environment.

FastAPI provides HTTP endpoints for these operations and supports request validation, structured responses, and automatic API documentation.

## 4.2 Why Kubernetes?

The project focuses on resilience in distributed applications. Kubernetes provides the environment in which services are deployed and managed.

It also exposes APIs that allow an external orchestrator to inspect pods, restart deployments, and change replica counts.

## 4.3 Why Prometheus and Grafana?

Prometheus collects and stores time-series metrics. The orchestrator can query these metrics to obtain information about resource consumption.

Grafana provides dashboards that help visualize the behavior of the application and infrastructure, particularly during experiments and fault scenarios.

## 4.4 Why SQLite?

The project requires persistent incident records so that information about incidents can remain available after the orchestrator restarts.

SQLite provides this capability without introducing the operational complexity of a separate database server. It is appropriate for the current prototype and experimental environment.

# 5. Development Environment

The initial experimental environment was configured as follows:

| Component | Configuration |
|---|---|
| Host operating system | Arch Linux |
| RAM | 16 GB DDR5 |
| Container platform | Docker |
| Kubernetes distribution | Minikube |
| Kubernetes driver | Docker |
| Cluster CPUs | 4 |
| Cluster memory | 8192 MB |
| Kubernetes version | v1.35.1 |
| Minikube version | v1.38.1 |
| Docker version | 29.9.1 |
| Helm version | v4.3.0 |
| Python | Python 3 |

The cluster uses a single Minikube node, which acts as both the control-plane and worker node.

This is a local experimental environment, not a production or multi-node deployment.

# 6. Reference Application Deployment

The project uses Google's Online Boutique as its reference application.

Online Boutique is a microservices-based e-commerce application. It contains 12 services that communicate to provide functionality such as browsing products, managing a shopping cart, and completing purchases.

The deployment manifest is stored in:

`deploy/online-boutique.yaml`

The application was deployed into the Kubernetes cluster and its pods were monitored until they reached the Running state.

### Verified results

- All 12 application pods reached `1/1 Running`.
- The frontend was accessible through Kubernetes port forwarding.
- Products could be browsed.
- Items could be added to the shopping cart.
- The checkout process was tested successfully.

The application provides a real distributed workload against which monitoring and recovery operations can be demonstrated.

# 7. Monitoring Infrastructure

Prometheus and Grafana were deployed using the Prometheus community monitoring stack through Helm.

The configuration files are:

- `telemetry/values.yaml`
- `telemetry/custom-rules.yaml`

Prometheus collects Kubernetes infrastructure metrics, including container resource usage.

Custom recording rules were added for:

- Container CPU usage using a five-minute rate.
- Container CPU usage using an instant rate.
- Container memory working set.

These rules aggregate container metrics by namespace, pod, and node.

The custom five-minute CPU recording rule is used by the orchestrator's CPU metrics integration.

Grafana provides dashboards for observing CPU usage, memory usage, and container restarts.

The monitoring environment was used to inspect the state of the application and provide visibility during experiments.

# 8. Orchestrator Implementation

The orchestrator is implemented as a modular Python application.

Its main entry point is:

`orchestrator/app/main.py`

The application uses FastAPI and initializes its integrations during application startup.

The main integrations are:

- `KubernetesIntegration`
- `PrometheusIntegration`
- `IncidentStore`

The application configuration is managed through `orchestrator/app/config.py`.

## 8.1 Health endpoint

**Endpoint:** `GET /health`

Purpose:

Checks whether the orchestrator API is running.

Example response:

```json
{
  "status": "ok"
}
```

## 8.2 Pod inspection

**Endpoint:** `GET /pods`

Optional query parameter: `namespace`

Purpose:

Retrieves pod information from Kubernetes.

The returned information includes:

- Pod name.
- Pod phase.
- Total container restart count.

Example:

`GET /pods?namespace=default`

This endpoint allows the orchestrator to inspect the state of workloads without requiring the user to execute Kubernetes commands directly.

## 8.3 CPU metrics

**Endpoint:** `GET /cpu`

Optional query parameter: `namespace`

Purpose:

Retrieves CPU usage metrics from Prometheus for a specified Kubernetes namespace.

The integration:

1. Validates the namespace.
2. Builds a PromQL query using the custom five-minute CPU recording rule.
3. Sends the query to the Prometheus HTTP API.
4. Checks the response.
5. Converts the returned metric values into structured data.

The returned information includes:

- Namespace.
- Pod.
- Node.
- CPU usage in cores.

Live tests returned metrics for both the `default` and `monitoring` namespaces.

## 8.4 Deployment restart

**Endpoint:** `POST /deployments/{namespace}/{name}/restart`

Purpose:

Requests a rolling restart of a Kubernetes deployment.

The orchestrator patches the deployment's pod template with a new `kubectl.kubernetes.io/restartedAt` annotation.

Kubernetes detects the template change and performs a rollout.

This allows the orchestrator to initiate a deployment restart through its own API rather than requiring direct manual interaction with Kubernetes.

## 8.5 Deployment scaling

**Endpoint:** `PATCH /deployments/{namespace}/{name}/scale`

Request body:

```json
{
  "replicas": 2
}
```

Purpose:

Changes the desired number of replicas for a deployment.

The endpoint validates the replica count and sends a patch request to the Kubernetes API.

Negative replica counts are rejected.

This operation provides a direct way to demonstrate how the orchestrator can control the availability of a service.

# 9. Incident Storage

Incident information is stored using SQLite.

The implementation is located in:

`orchestrator/app/integrations/incident_store.py`

The default database location is:

`data/incidents.db`

The database contains an `incidents` table with the following fields:

| Field | Description |
|---|---|
| id | Unique incident identifier |
| created_at | UTC creation timestamp |
| namespace | Kubernetes namespace |
| resource_type | Type of affected resource |
| resource_name | Name of affected resource |
| trigger | Incident trigger information |
| diagnosis | Diagnosis information, if supplied |
| action | Action information, if supplied |
| status | Incident status |
| details | Optional additional information stored as JSON |

The database is initialized when the FastAPI application starts.

The API provides three operations:

- `POST /incidents` — creates an incident record.
- `GET /incidents` — retrieves incident records with pagination.
- `GET /incidents/{incident_id}` — retrieves a specific incident.

The implementation uses parameterized SQL statements and stores additional details as JSON.

**Important current limitation:** Incident records are submitted through the API. The system does not yet automatically detect failures, create incident records from telemetry, or connect incident creation to an automated recovery workflow.

# 10. Testing and Verification

The project uses Pytest for unit testing.

The tests cover:

- Kubernetes integration behavior.
- Prometheus integration behavior.
- Incident storage operations.

The latest verified test command was:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q
```

Result:

**22 passed, 9 skipped.**

The skipped tests are not counted as passing tests.

Additional live integration checks were performed against the running Minikube cluster.

## 10.1 Live API verification

The following operations were verified:

| Operation | Result |
|---|---|
| `GET /health` | Successful |
| `GET /pods` | Successful |
| `GET /cpu` | Successful for tested namespaces |
| Deployment restart | Successfully tested on frontend |
| Deployment scaling | Successfully tested on frontend |
| Incident creation | HTTP 201 |
| Incident listing | HTTP 200 |
| Incident retrieval | HTTP 200 |
| Retrieval of nonexistent incident | HTTP 404 |
| Incident persistence after API restart | Verified |

## 10.2 Cartservice recovery demonstration

A live experiment was conducted using the orchestrator API.

The target was the `cartservice` deployment in the `default` namespace.

**Step 1 — Initial state**

The deployment was running with one replica.

**Step 2 — Scale down**

The following API operation was executed:

```http
PATCH /deployments/default/cartservice/scale
```

Request:

```json
{
  "replicas": 0
}
```

Result:

- HTTP 200 returned by the orchestrator.
- Kubernetes reported zero desired and available replicas.
- No cartservice pods remained.

**Step 3 — Restore service**

The same endpoint was called with:

```json
{
  "replicas": 1
}
```

Result:

- HTTP 200 returned by the orchestrator.
- Kubernetes successfully completed the deployment rollout.
- A new cartservice pod reached `1/1 Running`.

**Step 4 — Functional verification**

The frontend was accessed through:

```bash
kubectl port-forward svc/frontend 8080:80
```

The application was opened at:

`http://127.0.0.1:8080`

Product browsing and adding an item to the cart worked after cartservice had been restored.

This experiment demonstrates that the orchestrator can control a real Kubernetes deployment through its API and that the affected service can be restored to its previous replica count.

It is an important integration demonstration, but it is not yet an automated failure-detection and recovery scenario.

# 11. Repository Structure

The main repository structure is:

```text
verified-recovery/
├── deploy/
│   └── online-boutique.yaml
├── docs/
│   ├── devlog.md
│   ├── technical-documentation.md
│   └── img/
├── load/
├── orchestrator/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── integrations/
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   └── unit/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── telemetry/
│   ├── values.yaml
│   └── custom-rules.yaml
├── README.md
└── .gitignore
```

# 12. Current Limitations and Future Development

The current implementation establishes the infrastructure and system interfaces needed for the larger recovery orchestrator.

The following capabilities remain part of the planned development:

1. **Automated failure detection:** Detecting service degradation or failure from telemetry rather than relying on manual API requests.
2. **Application-level diagnosis:** Identifying which service or condition is responsible for an incident.
3. **Deterministic recovery policies:** Selecting an allowed recovery action according to predefined rules.
4. **Automated recovery execution:** Connecting detected incidents to controlled recovery operations.
5. **Post-action verification:** Checking whether the recovery action restored the expected service behavior.
6. **Fallback handling:** Defining what happens when an attempted recovery fails.
7. **Distributed tracing:** Integrating OpenTelemetry to investigate requests across microservices.
8. **Fault injection experiments:** Evaluating system behavior under controlled failures.
9. **Load testing and baselines:** Measuring system behavior under controlled workload conditions.

The project is intended to evolve from the current manually invoked operational API into a structured and verifiable recovery system.

# 13. Conclusion

The current version of Verified Recovery provides a working foundation for a Kubernetes-based resilience orchestrator.

A distributed microservices application has been deployed and functionally tested. Infrastructure monitoring is available through Prometheus and Grafana. A modular FastAPI application can retrieve pod information, query CPU metrics, restart deployments, and change replica counts. Incident information can also be stored persistently and retrieved through the API.

The most significant practical demonstration so far is the controlled scaling down and restoration of the cartservice deployment through the orchestrator API, followed by functional verification through the frontend application.

These results establish the infrastructure, observability, and operational interfaces required for the next development stages: automated detection, diagnosis, policy-guided recovery, and verification.
