from pytest import MonkeyPatch

from portable_agent.config.settings import Settings


def test_settings_when_environment_is_set_should_read_secure_values(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_OIDC_AUDIENCE", "runtime-test")
    monkeypatch.setenv("AGENT_ALLOWED_HOSTS", '["agent-runtime", "localhost"]')
    monkeypatch.setenv("AGENT_DOCS_ENABLED", "false")

    settings = Settings()

    assert settings.oidc_audience == "runtime-test"
    assert settings.allowed_hosts == ["agent-runtime", "localhost"]
    assert settings.docs_enabled is False
