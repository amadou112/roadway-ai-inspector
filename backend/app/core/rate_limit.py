from slowapi import Limiter
from slowapi.util import get_remote_address

# Applied as defense-in-depth against runaway OpenAI usage / demo-data spam on
# the public deployment. Per-process, per-IP limits (fine for a single Render
# instance; would need a shared backend like Redis to hold across replicas).
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Tight budget for endpoints that call the LLM — the real cost exposure.
LLM_RATE_LIMIT = "5/minute;30/hour"
