# Verified Recovery — Professor Presentation

## 1. Project overview

**Verified Recovery** is a project that aims to build a deterministic, policy-guided recovery orchestrator for distributed applications.

Modern applications often consist of multiple services communicating with each other. A failure or performance problem in one service can affect other parts of the application.

Kubernetes already provides basic container orchestration and self-healing capabilities. However, our project aims to build an additional layer that can understand system conditions, select controlled recovery actions, execute them, and verify whether they worked.

The long-term workflow is:

**Detection → Diagnosis → Policy Decision → Action → Verification → Fallback**

The project uses Google's Online Boutique as a reference application. It consists of 12 microservices and provides a realistic environment for testing distributed-system behavior.

## 2. What we have accomplished so far

We have completed the initial infrastructure and orchestrator foundation.

### A. Distributed application deployment

- Deployed the Online Boutique application on a local Kubernetes cluster.
- Successfully started its 12 microservices.
- Verified that the application is accessible and functional.
- Tested the shopping workflow, including adding a product to the cart.

**What this demonstrates:** We have a real distributed application that can be used for experiments rather than relying on simulated services.

### B. Monitoring infrastructure

- Deployed Prometheus for collecting and querying system metrics.
- Deployed Grafana for visualizing those metrics.
- Configured custom Prometheus recording rules for CPU and memory measurements.
- Created monitoring views for CPU usage, memory usage, and container restarts.

**What this demonstrates:** We can observe the system's operational state and collect measurements that can later support diagnosis and recovery decisions.

### C. Orchestrator implementation

We developed a FastAPI-based service that communicates with Kubernetes and Prometheus.

It currently provides interfaces to:

- Check the orchestrator's health.
- Retrieve information about running pods.
- Retrieve CPU usage metrics.
- Restart deployments.
- Change deployment replica counts.
- Create and retrieve incident records.

**What this demonstrates:** We have built a separate management layer that can interact with the distributed application and execute operational actions programmatically.

### D. Incident storage

We implemented persistent incident storage using SQLite.

The system can store information such as:

- Affected namespace and resource.
- Trigger information.
- Diagnosis field.
- Intended action.
- Current status.
- Additional details.

Incident records can be created and retrieved through the API.

At this stage, records are submitted manually. Automatic incident detection and creation are future work.

### E. Testing

- Implemented unit tests for the main integrations and incident storage.
- Recorded test result: **22 passed, 9 skipped**.
- Tested the API against the running Kubernetes cluster.
- Verified deployment restart and scaling operations.
- Verified that incident records remain available after restarting the API process.

## 3. What the system can demonstrate today

The clearest demonstration is controlled recovery of a microservice.

We used `cartservice` as the target.

1. Initially, the service had one running replica.
2. We sent a request to the orchestrator to scale it down to zero.
3. Kubernetes removed the cartservice pod.
4. The orchestrator received another request to restore the replica count to one.
5. Kubernetes created a new pod and completed the rollout.
6. We accessed the Online Boutique application again.
7. We verified that the shopping workflow worked, including adding a product to the cart.

This demonstrates that our orchestrator can execute Kubernetes operations through an API and that the resulting service can be restored.

It is important to distinguish this from autonomous recovery: the actions were explicitly requested. Automatic detection and decision-making are not implemented yet.

## 4. Technologies used and why

| Technology | Purpose in the project | Why we selected it |
|---|---|---|
| Python | Main development language | Suitable for automation, APIs, and infrastructure integration |
| FastAPI | Orchestrator backend | Provides REST APIs, validation, and automatic documentation |
| Kubernetes | Manages the microservices | Provides deployment, scaling, and container orchestration |
| Minikube | Local Kubernetes environment | Allows us to develop and test a real cluster locally |
| Docker | Container runtime | Runs the application containers and supports the local cluster |
| Online Boutique | Distributed reference application | Provides a realistic 12-microservice environment |
| Prometheus | Metrics collection and querying | Provides measurable information about system behavior |
| Grafana | Metrics visualization | Makes infrastructure conditions easier to understand |
| Helm | Monitoring-stack deployment | Simplifies installation and configuration of Kubernetes applications |
| Kubernetes Python client | Orchestrator-to-Kubernetes communication | Allows Python code to inspect and control Kubernetes resources |
| HTTPX | Orchestrator-to-Prometheus communication | Allows the backend to query monitoring data |
| SQLite | Incident persistence | Stores incident records without requiring another database server |
| Pydantic Settings | Configuration management | Keeps application configuration organized |
| Pytest | Automated testing | Helps verify implementation behavior |
| Git and GitHub | Version control and collaboration | Tracks changes and supports team development |

## 5. Why not rely on Kubernetes alone?

Kubernetes already handles several operational problems, such as restarting failed containers and maintaining the desired number of replicas.

Our project does not aim to replace Kubernetes.

Instead, it aims to add a higher-level recovery process.

For example:

- Kubernetes can report that a pod is unhealthy.
- Monitoring tools can provide CPU, memory, latency, and error-rate information.
- Our intended orchestrator will use this information to help determine what happened.
- A deterministic policy will select an approved recovery action.
- The orchestrator will execute that action and verify the result.

This creates a controlled and auditable recovery workflow rather than simply executing arbitrary actions.

## 6. What remains to be done

The current implementation is the foundation, not the final autonomous system.

The next stages include:

- Completing distributed tracing with OpenTelemetry.
- Completing controlled fault-injection experiments using Chaos Mesh.
- Completing load testing using Locust and establishing performance baselines.
- Implementing automatic incident detection.
- Implementing diagnosis using collected telemetry.
- Defining deterministic recovery policies.
- Connecting policy decisions to approved Kubernetes actions.
- Implementing automated post-action verification.
- Implementing fallback behavior when recovery fails.
- Recording the complete recovery process for auditing.

Some infrastructure and orchestrator work is complete, while the remaining Phase 1 team experiments and integration still need to be finalized.

## 7. Suggested live demonstration

The following is a practical sequence, assuming the environment is running and all required components are available.

### Step 1 — Show the application

Open Online Boutique in the browser.

Explain that it consists of 12 independent microservices working together as one application.

### Step 2 — Show the monitoring infrastructure

Open Grafana and show the available CPU, memory, and restart information.

Explain that monitoring provides the operational data needed for future diagnosis.

### Step 3 — Show the orchestrator

Open the FastAPI documentation at:

`http://127.0.0.1:8000/docs`

Show the available API operations.

Briefly explain that the orchestrator communicates with Kubernetes and Prometheus.

### Step 4 — Demonstrate a controlled failure

Show that cartservice initially has one replica.

Use the orchestrator's scaling endpoint to set its replica count to zero.

Show the resulting Kubernetes state.

Explain that the service has been deliberately taken out of operation through the orchestrator API.

### Step 5 — Restore the service

Use the same API to restore the replica count to one.

Show the rollout completing and the new pod becoming ready.

### Step 6 — Verify application behavior

Return to the browser and test the shopping workflow.

Explain that this confirms the service has become functional again.

### Step 7 — Explain the next stage

Conclude by explaining that the current demonstration uses explicit API requests. The next major engineering step is to connect monitoring, detection, diagnosis, policy decisions, actions, and verification into one automated workflow.

Do not demonstrate fault injection or load testing as completed unless the team's actual results and evidence are available.

---

## 8. Short spoken explanation

A suggested two-minute explanation:

"Our project is called Verified Recovery. Its goal is to build a controlled recovery system for distributed applications.

We are using Google's Online Boutique, which consists of 12 microservices, as our test environment. We deployed it on Kubernetes using Minikube, then added Prometheus and Grafana to monitor system metrics.

After establishing the infrastructure, we developed a separate orchestrator using Python and FastAPI. It communicates with Kubernetes and Prometheus. Currently, it can retrieve pod information and CPU metrics, restart deployments, scale services, and store incident records.

One of our practical demonstrations was taking cartservice down to zero replicas through our API, then restoring it to one replica. We verified that Kubernetes recreated the pod and that the shopping application worked again.

The important point is that we are not trying to replace Kubernetes. We are building a higher-level recovery process around it. Kubernetes manages the containers, monitoring provides system information, and our orchestrator is intended to make controlled recovery decisions based on that information.

Our current work establishes the infrastructure and operational interfaces. The next stages are automatic detection, diagnosis, deterministic policy selection, recovery verification, and fallback. We are also completing the team's tracing, fault-injection, and load-testing work."

---

## 9. Questions the professor may ask

### Why did you choose Online Boutique?

Because it is a realistic microservices application with multiple independent services and dependencies. It allows us to investigate how failures and performance problems can affect a distributed application.

### Why Kubernetes?

Because it is widely used for container orchestration and provides the infrastructure needed to deploy, monitor, scale, and manage microservices.

### What is the difference between Prometheus and Grafana?

Prometheus collects and queries metrics. Grafana visualizes those metrics through dashboards.

### What does your orchestrator add?

It provides a separate management layer that communicates with monitoring and Kubernetes. Its intended role is to coordinate diagnosis and controlled recovery actions rather than relying only on individual infrastructure components.

### Is the system already autonomous?

No. The current implementation provides the infrastructure, monitoring integration, operational APIs, and incident storage. The automated decision and recovery workflow is still under development.

### Why is recovery verification important?

Executing an action does not necessarily mean the problem has been solved. The system must check whether the affected service and application actually recovered.

### Why deterministic policies?

Recovery operations can affect availability and data. Deterministic policies make the allowed decisions explicit, predictable, and auditable.

### What is the role of AI in the project?

AI is intended to assist with diagnosis, not to make unrestricted recovery decisions. The recovery action should remain constrained by deterministic policies and an approved action catalogue.

### What is the main achievement so far?

We have moved beyond a theoretical design. We have a deployed distributed application, monitoring infrastructure, a working orchestrator API, Kubernetes operational control, persistent incident storage, automated tests, and a demonstrated service restoration scenario.

---

## 10. Main message to communicate

The project has progressed from its initial design to a working infrastructure and orchestrator foundation.

We can deploy and monitor a real microservices application, interact with its infrastructure through our own API, execute controlled service operations, and verify application behavior after restoration.

The remaining work is to connect these capabilities into the complete automated, deterministic, and verifiable recovery workflow.