from nox_poetry import Session, session


@session(python=['3.11'])
def tests(session: Session) -> None:
    session.install('pytest', '.')
    session.run('pytest')
