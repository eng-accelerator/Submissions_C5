"""
Supabase JWT verification utility.
Scaffolded for future use — not enforced on MVP endpoints.
"""
from typing import Optional

import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.settings import get_settings

security = HTTPBearer(auto_error=False)


async def verify_supabase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[dict]:
    """
    Verifies a Supabase JWT by calling the Supabase /auth/v1/user endpoint.
    Returns the user dict if valid, or None if no token was provided.
    Raises 401 if the token is invalid.
    """
    if not credentials:
        return None

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase auth is not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY)",
        )

    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_service_role_key,
            },
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.json()
