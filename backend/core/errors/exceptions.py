from __future__ import annotations

class DomainError(Exception):
    code = "domain_error"

class AuthError(DomainError):
    code = "auth_error"

class ValidationError(DomainError):
    code = "validation_error"

class NotFoundError(DomainError):
    code = "not_found"

class BadRequestException(DomainError):
    code = "bad_request"

class NotFoundException(DomainError):
    code = "not_found"
