from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

# Configure an audit logger if not already configured by global logging setup.
logger = logging.getLogger("audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")  # JSON already formatted below
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Context var populated by request-id middleware
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def audit_log(
    action: str,
    user_id: Any | None,
    entity: str,
    entity_id: Any | None,
    details: dict | None = None,
    correlation_id: str | None = None,
) -> str:
    """Emit a structured audit record.

    Returns the correlation_id used so callers can chain additional events.
    """
    if correlation_id is None:
        correlation_id = str(uuid4())
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "action": action,
        "user_id": user_id,
        "entity": entity,
        "entity_id": entity_id,
        "details": details or {},
    }
    rid = request_id_ctx.get()
    if rid:
        payload["request_id"] = rid
    logger.info(json.dumps(payload), extra={"audit": True, "action": action})
    return correlation_id

