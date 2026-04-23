# Generated migration for LeaveRequest approval fields

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_overtimerecord_approved_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='核准時間'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leave_requests', to='employees.employee', verbose_name='核准主管'),
        ),
    ]
