from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user

        if not user.is_authenticated:
            return False

        roles = user.roles.all()

        required_permission = getattr(view, 'required_permissions', [])

        for role in roles:
            role_permissions = role.permissions.all()
            if all(permission in role_permissions.values_list('name', flat=True) for permission in required_permission):
                return True
        return False


