from collections.abc import Callable

from portable_agent.config.settings import Settings
from portable_agent.repositories.model_repository import DemoIntentModel, IntentModel
from portable_agent.repositories.openai_intent_model import OpenAIIntentModel
from portable_agent.repositories.policy_repository import DemoPolicyRepository
from portable_agent.services.proposal_service import ProposalService


def get_proposal_service() -> ProposalService:
    settings = Settings()
    return ProposalService(
        _MODEL_FACTORIES[settings.model_provider](settings), DemoPolicyRepository()
    )


def _demo_model(settings: Settings) -> IntentModel:
    del settings
    return DemoIntentModel()


def _openai_model(settings: Settings) -> IntentModel:
    api_key = settings.model_api_key
    return OpenAIIntentModel(
        base_url=str(settings.model_base_url),
        model_name=settings.model_name,
        api_key=api_key.get_secret_value() if api_key else None,
        timeout_seconds=settings.model_timeout_seconds,
    )


_MODEL_FACTORIES: dict[str, Callable[[Settings], IntentModel]] = {
    "demo": _demo_model,
    "openai-compatible": _openai_model,
}
