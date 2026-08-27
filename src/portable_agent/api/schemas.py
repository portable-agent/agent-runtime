from pydantic import BaseModel, Field

from portable_agent.domain.models import ActionProposal, ConversationContext


class ProposalRequest(BaseModel):
    utterance: str = Field(min_length=1, max_length=10_000)
    context: ConversationContext


class ProposalResponse(BaseModel):
    proposal: ActionProposal | None
