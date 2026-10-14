"""quote-api: a tiny API that fetches a random fact from a public upstream API.

Deliberately simple. It exists so there is a real, deployable service whose
deployments can succeed or fail, for the AI SRE agent to watch.
"""
import logging
import os

import httpx
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("quote-api")


def load_config() -> dict:
    """Validate configuration at startup. A bad config crashes the container
    immediately (so Kubernetes shows CrashLoopBackOff) instead of failing later."""
    upstream = os.environ.get("UPSTREAM_URL", "")
    if not upstream.startswith(("http://", "https://")):
        log.critical("FATAL invalid UPSTREAM_URL %r: must start with http:// or https://", upstream)
        raise SystemExit(1)
    return {
        "upstream_url": upstream,
        "version": os.environ.get("APP_VERSION", "dev"),
        "timeout_s": float(os.environ.get("UPSTREAM_TIMEOUT_S", "5")),
    }


CONFIG = load_config()
app = FastAPI(title="quote-api")


@app.get("/health")
def health() -> dict:
    # Intentionally does NOT call the upstream: a flaky third party must not
    # make Kubernetes think this pod is broken.
    return {"status": "ok", "version": CONFIG["version"]}


@app.get("/quote")
def quote() -> dict:
    try:
        resp = httpx.get(CONFIG["upstream_url"], timeout=CONFIG["timeout_s"])
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("upstream call failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"upstream error: {exc}") from exc
    return {"source": CONFIG["upstream_url"], "data": resp.json()}
