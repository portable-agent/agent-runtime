from pytest import MonkeyPatch

from portable_agent.config.settings import Settings


def test_settings_when_environment_is_set_should_read_secure_values(
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_OIDC_AUDIENCE", "runtime-test")
    monkeypatch.setenv("AGENT_ALLOWED_HOSTS", '["agent-runtime", "localhost"]')
    monkeypatch.setenv("AGENT_DOCS_ENABLED", "false")
    monkeypatch.setenv("AGENT_MODEL_PROVIDER", "openai-compatible")
    monkeypatch.setenv("AGENT_MODEL_BASE_URL", "http://model.test/v1")
    monkeypatch.setenv("AGENT_MODEL_NAME", "test-model")
    monkeypatch.setenv("AGENT_MODEL_API_KEY", "test-key")

    settings = Settings()

    assert settings.oidc_audience == "runtime-test"
    assert settings.allowed_hosts == ["agent-runtime", "localhost"]
    assert settings.docs_enabled is False
    assert settings.model_provider == "openai-compatible"
    assert str(settings.model_base_url) == "http://model.test/v1"
    assert settings.model_name == "test-model"
    assert settings.model_api_key is not None
    assert settings.model_api_key.get_secret_value() == "test-key"
