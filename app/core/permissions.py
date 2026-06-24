from typing import Dict, List
from app.core.exceptions import ValidationError, ForbiddenError


class PermissionValidator:

    VALID_RESOURCES = {"devices", "sensors", "ingests", "contexts"}
    VALID_ACTIONS = {"read", "write", "delete"}

    @classmethod
    def validate(cls, permissions: Dict[str, List[str]]) -> Dict[str, List[str]]:
        if not isinstance(permissions, dict):
            raise ValidationError("'permissions' must be a valid JSON object")

        normalized: Dict[str, List[str]] = {}
        for resource, actions in permissions.items():
            if resource not in cls.VALID_RESOURCES:
                raise ValidationError(
                    f"Unknown resource '{resource}'. Allowed: {sorted(cls.VALID_RESOURCES)}"
                )
            if not isinstance(actions, list) or len(actions) == 0:
                raise ValidationError(
                    f"Actions for '{resource}' must be a non-empty list"
                )

            unique_actions: List[str] = []
            for action in actions:
                if action not in cls.VALID_ACTIONS:
                    raise ValidationError(
                        f"Unknown action '{action}' for resource '{resource}'. "
                        f"Allowed: {sorted(cls.VALID_ACTIONS)}"
                    )
                if action not in unique_actions:
                    unique_actions.append(action)
            normalized[resource] = unique_actions

        return normalized

    @classmethod
    def has_permission(
        cls, permissions: Dict[str, List[str]], resource: str, action: str
    ) -> bool:
        if not isinstance(permissions, dict):
            return False
        granted = permissions.get(resource)
        if not isinstance(granted, list):
            return False
        return action in granted

    @classmethod
    def ensure_permission(
        cls, permissions: Dict[str, List[str]], resource: str, action: str
    ) -> None:
        if not cls.has_permission(permissions, resource, action):
            raise ForbiddenError(
                f"API Key does not grant '{action}' on '{resource}'"
            )
