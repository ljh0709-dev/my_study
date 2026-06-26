import hmac
from typing import Annotated

from fastapi import Header, HTTPException, status

from .config import settings


def require_internal_secret(
    x_internal_secret: Annotated[str | None, Header()] = None,
):
    provided = x_internal_secret or ''
    if not hmac.compare_digest(provided, settings.internal_ai_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid internal service credential.',
        )

