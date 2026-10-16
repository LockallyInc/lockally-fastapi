"""FastAPI integration for the Lockally email API.

Provides a Lockally client as an injectable dependency:

    from fastapi import Depends, FastAPI
    from lockally_fastapi import Lockally, LockallyClient

    app = FastAPI()
    lockally = Lockally(api_key="lk_live_...")   # lk_test_... runs in sandbox

    @app.post("/signup", status_code=202)
    def signup(client: LockallyClient = Depends(lockally)):
        client.send_email(
            from_="alerts@yourdomain.com",
            to="user@example.com",
            subject="Welcome",
            html="<b>Hi!</b>",
        )

Or configure from the environment (`LOCKALLY_API_KEY` / `LOCKALLY_BASE_URL`) and use
the ready-made `LockallyDep` annotated type:

    from lockally_fastapi import LockallyDep

    @app.post("/signup", status_code=202)
    def signup(client: LockallyDep):
        client.send_email(from_="alerts@yourdomain.com", to="user@example.com", ...)
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from lockally_fastapi.client import LockallyClient

__version__ = "0.1.0"
__all__ = ["Lockally", "LockallyClient", "get_lockally", "LockallyDep"]


class Lockally:
    """A configured Lockally provider usable directly as a FastAPI dependency:
    `Depends(lockally)` yields the shared `LockallyClient`."""

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None,
                 client: LockallyClient | None = None) -> None:
        self._client = client or LockallyClient(api_key=api_key, base_url=base_url)

    def __call__(self) -> LockallyClient:
        return self._client

    @property
    def client(self) -> LockallyClient:
        return self._client


@lru_cache
def get_lockally() -> LockallyClient:
    """Build a client from `LOCKALLY_API_KEY` / `LOCKALLY_BASE_URL` (cached)."""
    return LockallyClient(
        api_key=os.environ.get("LOCKALLY_API_KEY"),
        base_url=os.environ.get("LOCKALLY_BASE_URL"),
    )


LockallyDep = Annotated[LockallyClient, Depends(get_lockally)]
