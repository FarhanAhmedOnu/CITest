# Generated by Django 5.0 on 2024-10-31 20:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Exam_Office_System', '0002_alter_student_expelled_alter_student_hall_clearance_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='result',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='examregistration',
            name='exams',
        ),
        migrations.AddField(
            model_name='examregistration',
            name='exam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='Exam_Office_System.exam'),
        ),
        migrations.AddField(
            model_name='result',
            name='registration',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result', to='Exam_Office_System.examregistration'),
        ),
        migrations.AlterField(
            model_name='certificateapplication',
            name='token',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='marksheetapplication',
            name='token',
            field=models.CharField(blank=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='marks',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='result',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='result',
            name='student',
        ),
    ]
