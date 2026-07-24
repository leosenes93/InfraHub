class DomainError(Exception):
    """Erro de regra de negocio, traduzido para HTTP na camada de API."""


class InvalidCredentialsError(DomainError):
    pass


class EmailAlreadyExistsError(DomainError):
    pass


class InactiveUserError(DomainError):
    pass
