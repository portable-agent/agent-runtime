from portable_agent.repositories.model_repository import DemoIntentModel
from portable_agent.repositories.policy_repository import DemoPolicyRepository
from portable_agent.services.proposal_service import ProposalService


def get_proposal_service() -> ProposalService:
    return ProposalService(DemoIntentModel(), DemoPolicyRepository())
