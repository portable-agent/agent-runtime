from typing import Annotated

from fastapi import APIRouter, Depends

from portable_agent.api.schemas import ProposalRequest, ProposalResponse
from portable_agent.application.proposal_service import ProposalService

router = APIRouter(prefix="/api/v1", tags=["proposals"])


def proposal_service() -> ProposalService:
    from portable_agent.infrastructure.deterministic_model import DeterministicDevelopmentModel
    from portable_agent.infrastructure.local_policy import LocalPolicyGateway

    return ProposalService(DeterministicDevelopmentModel(), LocalPolicyGateway())


@router.post("/proposals")
async def create_proposal(
    request: ProposalRequest,
    service: Annotated[ProposalService, Depends(proposal_service)],
) -> ProposalResponse:
    return ProposalResponse(proposal=await service.propose(request.utterance, request.context))
