# Generated by Django 4.0.5 on 2022-06-16 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_alter_author_first_name_alter_author_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='edumaterial',
            name='pdf_file_content',
            field=models.BinaryField(null=True),
        ),
    ]