from portable_agent.domain.models import ConversationContext, ProposedToolCall, RiskLevel


class LocalPolicyGateway:
    async def classify(self, call: ProposedToolCall, context: ConversationContext) -> RiskLevel:
        del context
        if call.kind.startswith(("wallet.", "payment.")):
            return RiskLevel.HIGH
        if call.kind.startswith(("calendar.create", "jira.create", "jira.update")):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
