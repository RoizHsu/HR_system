# Generated manually for employee auth and self-service modules

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='employees.department', verbose_name='上層部門'),
        ),
        migrations.AddField(
            model_name='employee',
            name='account',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='帳號'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='電子郵件'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='密碼(雜湊)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='position_level',
            field=models.PositiveIntegerField(default=1, verbose_name='職位階層'),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='employee',
            name='address',
            field=models.TextField(blank=True, default='', verbose_name='地址'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='出生日期'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='emergency_contact',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='緊急聯絡人姓名'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='emergency_phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='緊急聯絡人電話'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', '男'), ('F', '女'), ('O', '其他')], default='O', max_length=1, verbose_name='性別'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='hire_date',
            field=models.DateField(blank=True, null=True, verbose_name='到職日'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='id_number',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='身份證字號'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='job_title',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='職稱'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='name',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='姓名'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='聯絡電話'),
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clock_in', models.DateTimeField(verbose_name='上班打卡')),
                ('clock_out', models.DateTimeField(blank=True, null=True, verbose_name='下班打卡')),
                ('note', models.CharField(blank=True, default='', max_length=255, verbose_name='備註')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='employees.employee', verbose_name='員工')),
            ],
            options={'ordering': ['-clock_in']},
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('annual', '特休'), ('sick', '病假'), ('personal', '事假'), ('compensatory', '補休')], max_length=20, verbose_name='假別')),
                ('start_date', models.DateField(verbose_name='起始日')),
                ('end_date', models.DateField(verbose_name='結束日')),
                ('reason', models.CharField(blank=True, default='', max_length=255, verbose_name='請假原因')),
                ('status', models.CharField(choices=[('pending', '審核中'), ('approved', '已核准'), ('rejected', '已拒絕')], default='pending', max_length=20, verbose_name='審核狀態')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='employees.employee', verbose_name='員工')),
            ],
            options={'ordering': ['-start_date']},
        ),
        migrations.CreateModel(
            name='OvertimeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_date', models.DateField(verbose_name='加班日期')),
                ('hours', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='加班時數')),
                ('reason', models.CharField(blank=True, default='', max_length=255, verbose_name='加班原因')),
                ('status', models.CharField(choices=[('pending', '審核中'), ('approved', '已核准'), ('rejected', '已拒絕')], default='pending', max_length=20, verbose_name='審核狀態')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='overtime_records', to='employees.employee', verbose_name='員工')),
            ],
            options={'ordering': ['-work_date']},
        ),
        migrations.CreateModel(
            name='ShiftSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift_date', models.DateField(verbose_name='排班日期')),
                ('start_time', models.TimeField(verbose_name='上班時間')),
                ('end_time', models.TimeField(verbose_name='下班時間')),
                ('shift_type', models.CharField(blank=True, default='一般班', max_length=50, verbose_name='班別')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_schedules', to='employees.employee', verbose_name='員工')),
            ],
            options={'ordering': ['-shift_date', 'start_time']},
        ),
    ]
