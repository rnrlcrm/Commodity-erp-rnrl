from __future__ import annotations

from enum import Enum


class PermissionCodes(str, Enum):
    ORG_CREATE = "org.create"
    ORG_READ = "org.read"
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    ROLE_CREATE = "role.create"
    ROLE_ASSIGN_PERMS = "role.assign_permissions"

    @classmethod
    def all(cls) -> list[str]:
        return [p.value for p in cls]
