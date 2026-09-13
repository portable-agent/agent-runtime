from uuid import UUID

from pydantic import BaseModel


class TokenUser(BaseModel):
    tenant_id: UUID
    user_id: UUID
