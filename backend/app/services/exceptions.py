class DomainError(Exception):
    """Erro de regra de negocio, traduzido para HTTP na camada de API."""


class InvalidCredentialsError(DomainError):
    pass


class EmailAlreadyExistsError(DomainError):
    pass


class InactiveUserError(DomainError):
    pass


class AssetNotFoundError(DomainError):
    pass


class AttachmentNotFoundError(DomainError):
    pass


class UnsupportedFileTypeError(DomainError):
    pass


class FileTooLargeError(DomainError):
    pass


class DockerUnavailableError(DomainError):
    pass


class ZabbixUnavailableError(DomainError):
    pass


class ZabbixNotConfiguredError(DomainError):
    pass


class AssetAlreadyLinkedToZabbixError(DomainError):
    pass


class AssetMissingIpAddressError(DomainError):
    pass
