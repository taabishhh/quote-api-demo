# Pushes to try

Each file here is a small change you apply with `git apply`, commit, and push.
Every one of them **passes the unit tests**, so CI deploys it. The breaking ones
only fail once they are running in the cluster, which is the realistic case.

| Patch | What it changes | What happens in the cluster |
|---|---|---|
| `00-healthy-add-version-endpoint` | Adds a `/version` endpoint | Deploy succeeds. Nothing for the agent to do. |
| `01-bad-upstream-url` | `upstreamUrl` loses its `https://` | Pods **CrashLoopBackOff**. Logs say `FATAL invalid UPSTREAM_URL`. |
| `02-bad-readiness-path` | Probe path `/health` becomes `/healthz` | Pods are Running but **never Ready**. Events show probe 404s. The workflow's `helm --wait` times out. |
| `03-low-memory-limit` | Memory limit 128Mi becomes 16Mi | Pods are **OOMKilled**, then CrashLoopBackOff. |
| `04-missing-env-var` | Code now needs an `API_TOKEN` env var the chart never sets | Pods **CrashLoopBackOff** with `KeyError: 'API_TOKEN'` in the logs. |

## How to run one

```bash
git apply scenarios/01-bad-upstream-url.patch
git commit -am "Tidy upstream config"
git push
```

Watch the **Actions** tab. The deploy job turns red after about 3 minutes.
Meanwhile the AI SRE agent (running with `--watch`) notices the unhealthy pods,
investigates, and asks you to approve a rollback.

## Clean up between tests

The agent fixes the **cluster** (it rolls the Helm release back). Your **git
history** still contains the bad commit, so fix that too before trying the next
scenario:

```bash
git revert --no-edit HEAD
git push
```

That push deploys the reverted (healthy) code. Then apply the next patch.
