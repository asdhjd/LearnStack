# Generated migration to remove QuestionLike model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0004_alter_communityreport_answer_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='QuestionLike',
        ),
    ]

