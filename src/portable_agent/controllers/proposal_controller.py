from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from portable_agent.config.services import get_proposal_service
from portable_agent.config.token_verifier import TokenVerifier
from portable_agent.models.user import TokenUser
from portable_agent.schemas.proposal_schema import ProposalRequest, ProposalResponse
from portable_agent.services.proposal_service import ProposalService


def build_router(token_verifier: TokenVerifier) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["proposals"])
    bearer = HTTPBearer(
        auto_error=False,
        bearerFormat="JWT",
        scheme_name="bearerAuth",
    )

    async def get_user(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer)],
    ) -> TokenUser:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise _unauthorized()
        user = await token_verifier.verify(credentials.credentials)
        if user is None:
            raise _unauthorized()
        return user

    @router.post("/proposals", response_model=ProposalResponse)
    async def create_proposal(
        request: ProposalRequest,
        user: Annotated[TokenUser, Depends(get_user)],
        service: Annotated[ProposalService, Depends(get_proposal_service)],
    ) -> ProposalResponse:
        result = await service.propose(request.text, request.context.to_model(user))
        return ProposalResponse(
            proposal=result.proposal,
            clarification=result.clarification,
        )

    return router


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )
