# Generated migration to remove learningstage_resources ManyToMany field
# 系统采用动态生成机制，不再需要数据库中的 ManyToMany 关联表
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning_paths', '0006_alter_learningstage_recommended_resources'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learningstage',
            name='recommended_resources',
        ),
    ]

