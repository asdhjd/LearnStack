# 修复category_id列类型以匹配引用表的id列
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning_paths', '0002_auto_20251011_1607'),
    ]

    operations = [
        # 修改category_id列类型为bigint（有符号），与categories_technologycategory.id匹配
        migrations.RunSQL(
            "ALTER TABLE learning_paths_learningpath MODIFY COLUMN category_id bigint NOT NULL;",
            "ALTER TABLE learning_paths_learningpath MODIFY COLUMN category_id bigint unsigned NOT NULL;"
        ),
        # 添加外键约束
        migrations.RunSQL(
            "ALTER TABLE learning_paths_learningpath ADD CONSTRAINT fk_learningpath_category FOREIGN KEY (category_id) REFERENCES categories_technologycategory(id) ON DELETE CASCADE;",
            "ALTER TABLE learning_paths_learningpath DROP FOREIGN KEY fk_learningpath_category;"
        ),
    ]