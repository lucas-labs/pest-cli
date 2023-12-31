def test_cli_structure() -> None:
    """cli :: the app should have all expected commands."""
    from pest_cli.app import app
    from pest_cli.cli import Group

    commands = app.list_commands(None)

    assert isinstance(app, Group) is True

    assert commands == [
        'generate',
    ]
