# Advanced MLOps Exercise: Professional CI/CD Workflow Report
**Repository**: [https://github.com/aqibqureshi786/mlops-assignment-1](https://github.com/aqibqureshi786/mlops-assignment-1)  
**Author**: aqibqureshi786  

---

## 1. Executive Summary & Architecture Overview

This project establishes a production-grade MLOps development workflow for the `student-ml-api` inference service adhering to strict enterprise software engineering standards.

### Core Development Lifecycle
Feature Branch -> Pull Request -> Automated CI -> Code Review -> Merge to main -> Semantic Tag -> Docker Build -> Container Registry (GHCR)

- **Branch Protection**: Direct commits to `main` are strictly blocked.
- **Automated Verification**: GitHub Actions automatically validates every PR through unit testing (`pytest`) and container build checks (`docker build`).
- **Traceable Releases**: Semantic version tags (`v*.*.*`) trigger automated container image publishing to **GitHub Container Registry (GHCR)**.
- **Forensic Traceability**: Every published container image is stamped with OCI metadata and Git commit SHA tags.

---

## 2. Complete Traceability Chain (Part 21)

| Parameter | Release v1.0.0 | Release v1.1.0 |
|---|---|---|
| **Pull Request** | [#1 (feature/prediction-api)](https://github.com/aqibqureshi786/mlops-assignment-1/pull/1) | [#2 (feature/model-metadata)](https://github.com/aqibqureshi786/mlops-assignment-1/pull/2) |
| **Merge Commit SHA** | `e9e8a50` | `36d024b` |
| **Git Tag** | `v1.0.0` | `v1.1.0` |
| **Docker Image Tags** | `student-ml-api:1.0.0`, `student-ml-api:latest`, `student-ml-api:sha-e9e8a50` | `student-ml-api:1.1.0`, `student-ml-api:latest`, `student-ml-api:sha-36d024b` |
| **Image Digest (SHA256)** | `sha256:34b211f8b9c5d14fc9c8ebd6df2de3220b502bb1d27b3b7ef1c65da2de0d1f95` | `sha256:274a880f8f1b56c768900b011870d3f352df95fe4c8b86472d07ad4f00d32f10` |
| **Registry URL** | `ghcr.io/aqibqureshi786/student-ml-api` | `ghcr.io/aqibqureshi786/student-ml-api` |

---

## 3. GitHub Actions Evidence (Part 5, 6, 14, 15)

### 3.1 Deliberate CI Failure Demonstration (Part 6)
- **Workflow Run**: [Run #34498409598](https://github.com/aqibqureshi786/mlops-assignment-1/actions/runs/34498409598)
- **Trigger**: Pull Request #1
- **Failure Cause**: Intentionally modified assertion in `tests/test_app.py` (`assert data["status"] == "wrong"`).
- **Result**: `validate` job failed in step `Unit Tests` (`AssertionError: assert 'healthy' == 'wrong'`). PR checks showed **FAILED**.

### 3.2 Successful CI Execution (Part 5)
- **Workflow Run**: [Run #34498513036](https://github.com/aqibqureshi786/mlops-assignment-1/actions/runs/34498513036)
- **Trigger**: Pull Request #1 (Commit `fix: correct health endpoint test`)
- **Result**: `validate` job succeeded in 45s. All checks turned green.

### 3.3 Automated Releases to GHCR (Part 14, 15, 19)
- **v1.0.0 Release**: [Run #34498723940](https://github.com/aqibqureshi786/mlops-assignment-1/actions/runs/34498723940) published `1.0.0` and `latest`.
- **v1.1.0 Release**: [Run #34499174516](https://github.com/aqibqureshi786/mlops-assignment-1/actions/runs/34499174516) published `1.1.0` and updated `latest` to point to `1.1.0`. `1.0.0` remains preserved.

---

## 4. Rollback Exercise (Part 20)

### Production Incident Scenario
Version `1.1.0` is assumed to contain a critical runtime defect in production.

### Resolution via Container Registry
Without editing source code or rebuilding any container images, production was rolled back to the known-good version `1.0.0` in seconds:

```bash
# 1. Stop and remove problematic container
docker stop student-ml-api
docker rm student-ml-api

# 2. Run known-good image from GHCR
docker run -d --name student-ml-api -p 5000:5000 ghcr.io/aqibqureshi786/student-ml-api:1.0.0

# 3. Verify health
curl http://localhost:5000/health
```

### Why Registry-Based Rollback is Superior
Compared to `git checkout <old-commit> && pip install -r requirements.txt && python app.py`:
1. **Deterministic Immutability**: Docker images are fixed binary artifacts. Re-running pip install might pull updated transitive dependencies, introducing unexpected breakage.
2. **Instant Recovery**: Pulling an already-built image takes seconds; compiling dependencies and running pip installs during an incident adds significant downtime.
3. **Environmental Parity**: Running the image guarantees identical system libraries, OS dependencies, and Python runtime across all nodes.

---

## 5. Advanced Docker & CI/CD Practices

### 5.1 Docker Build Cache Optimization (Part 25)
In our `Dockerfile`:
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```
- **Why this is preferred**: Docker caches layers sequentially. Python dependencies change rarely, while application code changes on almost every commit.
- By isolating `COPY requirements.txt` and `RUN pip install`, Docker reuses the cached layer containing all heavy dependencies when only `app.py` is edited.
- Putting `COPY . .` before `RUN pip install` invalidates the layer cache on every code change, forcing a complete re-download and re-install of all packages.

### 5.2 CI Workflow vs. Release Workflow Separation (Part 22)
- **CI Workflow**: Triggers on Pull Requests. Responsibilities: lint, test, and test-build Docker image without publishing.
- **Release Workflow**: Triggers exclusively on semantic version tags pushed to `main`. Responsibilities: test, build, version, and publish to GHCR.
- **Why publishing Docker images from every PR is undesirable**:
  1. Registry pollution with untested, intermediate, or broken builds.
  2. Security vulnerability: untested PR code could overwrite production tags like `latest` or inject unverified code into the organization registry.
  3. Storage cost explosion from unnecessary build artifacts.

### 5.3 OCI Metadata & Commit SHA Tagging (Part 23 & 24)
Using `docker/metadata-action`, each published image contains standard Open Container Initiative (OCI) labels:
- `org.opencontainers.image.title`
- `org.opencontainers.image.version`
- `org.opencontainers.image.revision` (exact commit SHA)
- `org.opencontainers.image.source`
- `org.opencontainers.image.created`
Additionally, tagging images with both semantic version and commit SHA (`student-ml-api:sha-36d024b`) enables zero-ambiguity correlation between running containers and source code commits.

---

## 6. Failure Analysis (Part 26)

### Scenario 1: Dependency Version Incompatibility
- **Symptom**: CI pipeline failed at step `Dependency Installation` with `ERROR: No matching distribution found for numpy==2.5.3`.
- **Root Cause**: `requirements.txt` strictly pinned `numpy==2.5.3` requiring Python >= 3.12, conflicting with the runner's Python 3.11 environment.
- **Evidence**: Actions Run #34498259698 log output: `Ignored versions that require a different python version: 2.5.3 Requires-Python >=3.12`.
- **Correction**: Updated `requirements.txt` to portable version specifications (`numpy>=1.24.0`, etc.).

### Scenario 2: Deliberate Unit Test Assertion Failure
- **Symptom**: Pull Request checks failed and displayed red status indicator.
- **Root Cause**: Injected mismatched assertion `assert data["status"] == "wrong"` in `tests/test_app.py`.
- **Evidence**: Actions Run #34498409598 log output: `AssertionError: assert 'healthy' == 'wrong'`.
- **Correction**: Restored assertion to `assert data["status"] == "healthy"` and committed `fix: correct health endpoint test`.

---

## 7. Viva Voce Questions & Answers

1. **Why should developers avoid directly pushing to `main`?**  
   Direct pushes bypass automated test suites, linting, and peer reviews, risking deploying breaking changes into production. Protected `main` branches guarantee that only validated code is merged.

2. **What is the purpose of a Pull Request beyond simply merging code?**  
   A PR acts as an audit trail, collaborative review platform, change summary, and automated gating mechanism to ensure code quality and team alignment before code integration.

3. **Why should CI execute before a PR is merged?**  
   To catch compilation errors, broken tests, and build failures early, ensuring that broken code is never introduced into the shared `main` codebase.

4. **What is the difference between a Docker image and a container?**  
   An image is a static, read-only blueprint containing the application code, libraries, and runtime environment. A container is a stateful, runnable instance of an image executed in an isolated process.

5. **Why should Docker images be versioned?**  
   Versioning provides deterministic environments, ensures traceability between releases and code commits, and enables reliable, instant rollbacks.

6. **Why is `latest` insufficient for production traceability?**  
   `latest` is a mutable tag that points to whatever image was most recently built. It provides no context about which commit, branch, or release is currently running in production.

7. **Why should the same Docker artifact be promoted rather than rebuilt?**  
   Rebuilding introduces non-determinism (e.g. newly published package versions or external dependencies). Promoting the exact binary artifact guarantees that production runs the identical artifact that was validated in staging.

8. **What is the purpose of a container registry?**  
   A container registry is a secure, centralized catalog for storing, versioning, and distributing container images across disparate computing environments.

9. **What is the difference between the CI workflow and release workflow?**  
   The CI workflow tests and validates code for prospective changes without altering external state. The Release workflow builds, tags, and publishes official deployment artifacts upon release triggers.

10. **Why should registry credentials be stored as secrets?**  
    To prevent unauthorized access, tampering, or malicious image poisoning in the container registry, preserving software supply chain security.

11. **How can you identify which source-code commit produced a Docker image?**  
    By inspecting embedded OCI metadata labels (`org.opencontainers.image.revision`) via `docker inspect` or tagging the image with the Git commit SHA.

12. **Why does Docker layer ordering affect CI/CD performance?**  
    Docker evaluates cache top-down. Ordering slow, rarely changed steps (e.g. dependency installation) before fast, frequently changed steps (e.g. source code copy) maximizes cache hits and minimizes build times.

13. **How would you rollback from version 1.1.0 to 1.0.0?**  
    By re-pointing the deployment command/manifest to the immutable `1.0.0` container image tag stored in the registry, without touching source code or rebuilding.

14. **What is the relationship between a Git tag and a Docker image tag?**  
    A Git tag marks a specific commit in source control; a Docker tag names a specific packaged container build compiled from that exact Git commit.

15. **In an MLOps system, what additional problems arise when the application version and model version change independently?**  
    Independent changes can cause input/output schema mismatches, serialization failures, unversioned drift in prediction logic, and severe debugging ambiguity when auditing inference errors.
