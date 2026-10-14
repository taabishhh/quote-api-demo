# quote-api-demo

A deliberately tiny API (FastAPI) that fetches a random fact from a public API.
It exists so the AI SRE agent has a real service to watch.

```
git push  ->  GitHub Actions  ->  tests -> build image -> push to ECR -> helm upgrade --wait  ->  EKS cluster
                                                                                                      |
                                              AI SRE agent (--watch) notices unhealthy pods <---------+
```

Endpoints: `GET /health`, `GET /quote`.

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
UPSTREAM_URL=https://catfact.ninja/fact uvicorn app.main:app --port 8000
curl localhost:8000/health
```

## Set it up on GitHub

1. Create an empty GitHub repo (for example `quote-api-demo`) and push this folder to it.
2. Build the cluster side with the Terraform in the `ai-sre-agent` repo (see its `docs/CICD_DEMO.md`).
   It creates the ECR repository, the cluster, and a login role for this repo.
3. In this repo on GitHub, go to **Settings, Secrets and variables, Actions, Variables**
   and add the four values that `terraform output github_actions_config` prints:
   `AWS_REGION`, `AWS_ROLE_ARN`, `EKS_CLUSTER_NAME`, `ECR_REPOSITORY`.
4. Push to `main` (or run the workflow by hand from the Actions tab). The first deploy should be green.

Then try the pushes in [`scenarios/`](scenarios/README.md).

## Layout

```
app/                FastAPI service
tests/              unit tests (run in CI before anything deploys)
chart/quote-api/    Helm chart (what gets deployed)
.github/workflows/  the deploy pipeline
scenarios/          git patches that break (or don't break) the deploy
Dockerfile
```
