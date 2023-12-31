from nox_poetry import Session, session


@session(python=['3.8', '3.9', '3.10', '3.11', '3.12'])
def tests(session: Session) -> None:
    session.install(
        '.',
        'colorama',
        'pytest-cov',
        'pytest',
    )

    params = (
        ['--cov=pest_cli', 'tests/', '--cov-report=xml'] if session.python == '3.11' else ['tests/']
    )

    session.run('pytest', *params)
