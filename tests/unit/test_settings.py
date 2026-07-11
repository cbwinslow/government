from pathlib import Path

from opendiscourse.config.settings import load_settings


def test_environment_overrides_toml(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "settings.toml"
    config.write_text('[storage]\nroot = "./from-file"\ntemp_root = "./from-file/.tmp"\n')
    monkeypatch.setenv("OPENDISCOURSE_STORAGE__ROOT", str(tmp_path / "from-env"))

    settings = load_settings(config)

    assert settings.storage.root == tmp_path / "from-env"
    assert settings.storage.temp_root == Path("from-file/.tmp")


def test_redacted_configuration_hides_secrets(monkeypatch) -> None:
    monkeypatch.setenv("OPENDISCOURSE_SOURCES__FEC_API_KEY", "sensitive")
    settings = load_settings(None)

    redacted = settings.redacted_dict()

    assert redacted["database"]["dsn"] == "**********"
    assert redacted["sources"]["fec_api_key"] == "**********"


def test_generic_user_agent_is_rejected(tmp_path: Path) -> None:
    config = tmp_path / "settings.toml"
    config.write_text('[http]\nuser_agent = "python"\n')

    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        load_settings(config)


def test_explicit_missing_configuration_is_rejected(tmp_path: Path) -> None:
    import pytest

    missing = tmp_path / "missing.toml"
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_settings(missing)
