"""数据范围（行级权限）辅助：根据角色 data_scope 计算可见部门"""

from app.models.users.users import Departments


def _collect_descendants(root_id: int) -> set:
    result = {root_id}
    frontier = [root_id]
    while frontier:
        children = list(Departments.objects.filter(parent_id__in=frontier).values_list("id", flat=True))
        new = [c for c in children if c not in result]
        result.update(new)
        frontier = new
    return result


def get_data_scope(user):
    """返回 (is_all, dept_ids)

    - is_all=True 表示可见全部数据
    - dept_ids 为允许可见的部门 id 集合；为空且 is_all=False 时按本人(创建人)过滤
    """
    if user.is_superuser:
        return True, set()

    is_all = False
    dept_ids = set()
    for role in user.roles.all():
        scope = role.data_scope
        if scope == "ALL":
            is_all = True
        elif scope == "DEPT_AND_CHILD":
            if user.dept_id:
                dept_ids |= _collect_descendants(user.dept_id)
        elif scope == "DEPT":
            if user.dept_id:
                dept_ids.add(user.dept_id)
        elif scope == "CUSTOM":
            dept_ids |= set(role.departments.values_list("id", flat=True))
        # SELF 不增加部门范围
    if is_all:
        return True, set()
    return False, dept_ids


def filter_by_data_scope(queryset, user, dept_field="department", owner_field="created_by"):
    """按数据范围过滤 queryset"""
    is_all, dept_ids = get_data_scope(user)
    if is_all:
        return queryset
    if dept_ids:
        return queryset.filter(**{f"{dept_field}__in": list(dept_ids)})
    # 仅本人数据
    return queryset.filter(**{owner_field: user})
