from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('questions', '0008_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='pinned',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
