from typing import Annotated

from fastapi import APIRouter, Depends

from portable_agent.config.services import get_proposal_service
from portable_agent.schemas.proposal_schema import ProposalRequest, ProposalResponse
from portable_agent.services.proposal_service import ProposalService

router = APIRouter(prefix="/api/v1", tags=["proposals"])


@router.post("/proposals")
async def create_proposal(
    request: ProposalRequest,
    service: Annotated[ProposalService, Depends(get_proposal_service)],
) -> ProposalResponse:
    proposal = await service.propose(request.utterance, request.context.to_model())
    return ProposalResponse(proposal=proposal)
