from pathlib import Path

from click.testing import CliRunner
from prompt_toolkit.application import create_app_session
from prompt_toolkit.output import DummyOutput


def test_generate_app_command(tmp_path):
    with create_app_session(output=DummyOutput()):
        runner = CliRunner()

        with runner.isolated_filesystem(tmp_path):
            from pest_cli.cli.commands.generate import generate

            cwd = Path.cwd()

            result = runner.invoke(
                generate,
                [
                    'application',
                    'myapp',
                    '--dm',
                    'poetry',
                    '--yes',
                    '--cwd',
                    str(cwd),
                ],
            )

            assert result.exit_code == 0

            # check that the files were generated
            assert (cwd / 'myapp').exists()
            assert (cwd / 'myapp' / 'pyproject.toml').exists()
            assert (cwd / 'myapp' / 'README.md').exists()
            assert (cwd / 'myapp' / 'poetry.toml').exists()
            assert (cwd / 'myapp' / '.gitignore').exists()
            assert (cwd / 'myapp' / 'myapp' / 'main.py').exists()
            assert (cwd / 'myapp' / 'myapp' / 'app_module.py').exists()
            assert (cwd / 'myapp' / 'myapp' / 'hello').exists()
            assert (cwd / 'myapp' / 'myapp' / 'hello' / 'module.py').exists()
            assert (cwd / 'myapp' / 'myapp' / 'hello' / 'hello_controller.py').exists()
            assert (cwd / 'myapp' / 'myapp' / 'hello' / 'greeter_service.py').exists()
