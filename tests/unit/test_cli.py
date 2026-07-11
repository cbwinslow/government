from pathlib import Path

from typer.testing import CliRunner

from opendiscourse.cli.app import app

runner = CliRunner()


def write_config(path: Path, root: Path) -> None:
    path.write_text(
        "\n".join(
            [
                'environment = "test"',
                "[storage]",
                f'root = "{root.as_posix()}"',
                f'temp_root = "{(root / ".tmp").as_posix()}"',
            ]
        )
    )


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_config_show_redacts_database_dsn(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    write_config(config, tmp_path / "lake")

    result = runner.invoke(app, ["config", "show", "--config-file", str(config)])

    assert result.exit_code == 0
    assert "**********" in result.stdout
    assert "postgresql+psycopg" not in result.stdout


def test_doctor_initializes_storage(tmp_path: Path) -> None:
    root = tmp_path / "lake"
    config = tmp_path / "config.toml"
    write_config(config, root)

    result = runner.invoke(app, ["doctor", "--config-file", str(config)])

    assert result.exit_code == 0
    assert "configuration" in result.stdout
    assert (root / "objects" / "sha256").is_dir()


def test_fixture_sync_runs_complete_cycle(tmp_path: Path) -> None:
    config = tmp_path / "config.toml"
    write_config(config, tmp_path / "lake")

    result = runner.invoke(app, ["fixture", "sync", "--config-file", str(config)])

    assert result.exit_code == 0
    assert "complete" in result.stdout
    assert "True" in result.stdout
