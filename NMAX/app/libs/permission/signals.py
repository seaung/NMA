"""权限缓存失效信号：用户/角色/权限变动时清除缓存"""
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from app.models.users.users import Roles, Users


def _invalidate(user_id):
    cache.delete(f"user_permissions_{user_id}")


@receiver(post_save, sender=Users)
def _on_user_saved(sender, instance, **kwargs):
    _invalidate(instance.id)


@receiver(m2m_changed, sender=Users.roles.through)
def _on_user_roles_changed(sender, instance, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        _invalidate(instance.id)


@receiver(m2m_changed, sender=Roles.permissions.through)
def _on_role_perms_changed(sender, instance, action, **kwargs):
    if action.startswith("post_"):
        for uid in instance.users.values_list("id", flat=True):
            _invalidate(uid)
