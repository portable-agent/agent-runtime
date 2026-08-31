from pydantic import ValidationError

from portable_agent.models.proposal import (
    ActionPlan,
    CalendarEvent,
    Clarification,
    ProposalResult,
    UserContext,
)
from portable_agent.repositories.model_repository import ModelRepository
from portable_agent.repositories.policy_repository import PolicyRepository


class ProposalService:
    def __init__(self, model: ModelRepository, policy: PolicyRepository) -> None:
        self._model = model
        self._policy = policy

    async def propose(self, text: str, context: UserContext) -> ProposalResult:
        reply = await self._model.propose(text, context)
        if reply is None:
            return ProposalResult()
        if reply.kind != "calendar.create_event":
            return ProposalResult()
        if reply.connector not in context.available_tools:
            return ProposalResult()

        missing_fields = _get_missing_fields(reply.payload)
        if missing_fields:
            return ProposalResult(
                clarification=Clarification(
                    question=_get_question(missing_fields),
                    missing_fields=missing_fields,
                )
            )

        try:
            event = CalendarEvent.model_validate(reply.payload)
        except ValidationError:
            return ProposalResult()

        risk = await self._policy.get_risk(reply, context)
        return ProposalResult(
            proposal=ActionPlan(
                kind=reply.kind,
                connector=reply.connector,
                payload=event.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_defaults=True,
                    exclude_none=True,
                ),
                explanation=reply.explanation,
                risk=risk,
                requires_approval=True,
            )
        )


_REQUIRED_FIELDS = ("title", "startAt", "endAt", "timeZone")
_FIELD_NAMES = {
    "title": "название",
    "startAt": "время начала",
    "endAt": "время окончания",
    "timeZone": "часовой пояс",
}


def _get_missing_fields(payload: dict[str, object]) -> list[str]:
    return [
        field
        for field in _REQUIRED_FIELDS
        if field not in payload or payload[field] is None or payload[field] == ""
    ]


def _get_question(missing_fields: list[str]) -> str:
    names = [_FIELD_NAMES[field] for field in missing_fields]
    fields_text = names[0] if len(names) == 1 else f"{', '.join(names[:-1])} и {names[-1]}"
    return f"Укажи {fields_text} встречи."
