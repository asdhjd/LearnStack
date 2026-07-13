# 修复模型字段与数据库列的映射关系
from django.db import migrations


def fix_field_mapping(apps, schema_editor):
    # 这个函数实际上不需要执行任何数据库操作，因为：
    # 1. 数据库中已经存在technology_id列
    # 2. 我们已经在models.py中通过db_column="technology_id"指定了字段映射
    # 3. 我们将字段名从'category'重命名为'technology'
    # 这个迁移只是为了记录这些更改，确保Django的迁移状态与实际数据库结构一致
    pass


def revert_field_mapping(apps, schema_editor):
    # 回滚操作也不需要做任何事情
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('learning_paths', '0003_fix_category_id_type'),
    ]

    operations = [
        # 使用RunPython来手动控制迁移逻辑
        migrations.RunPython(fix_field_mapping, revert_field_mapping),
    ]