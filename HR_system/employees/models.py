from django.contrib.auth.models import User
from django.db import models

class Department(models.Model):
    name = models.CharField("部門名稱", max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="上層部門",
    )
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    # 枚舉選項
    GENDER_CHOICES = [('M', '男'), ('F', '女'), ('O', '其他')]
    TYPE_CHOICES = [('full_time', '全職'), ('part_time', '兼職'), ('intern', '實習')]
    STATUS_CHOICES = [('active', '在職'), ('resigned', '離職'), ('on_leave', '留停')]

    # 1. 個人資訊 (核心)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    employee_id = models.CharField("員工編號", max_length=20, unique=True)
    account = models.CharField("帳號", max_length=50, unique=True, null=True, blank=True)
    password = models.CharField("密碼(雜湊)", max_length=128, null=True, blank=True)
    email = models.EmailField("電子郵件", unique=True, null=True, blank=True)
    name = models.CharField("姓名", max_length=50, blank=True, default='')
    gender = models.CharField("性別", max_length=1, choices=GENDER_CHOICES, blank=True, default='O')
    birthday = models.DateField("出生日期", null=True, blank=True)
    id_number = models.CharField("身份證字號", max_length=10, blank=True, default='')
    phone = models.CharField("聯絡電話", max_length=20, blank=True, default='')
    address = models.TextField("地址", blank=True, default='')
    emergency_contact = models.CharField("緊急聯絡人姓名", max_length=50, blank=True, default='')
    emergency_phone = models.CharField("緊急聯絡人電話", max_length=20, blank=True, default='')

    # 2. 職位資訊
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="部門")
    job_title = models.CharField("職稱", max_length=100, blank=True, default='')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="直屬主管")
    emp_type = models.CharField("員工類型", max_length=20, choices=TYPE_CHOICES, default='full_time')
    status = models.CharField("員工狀態", max_length=20, choices=STATUS_CHOICES, default='active')
    position_level = models.PositiveIntegerField("職位階層", default=1)

    # 3. 合約資訊
    hire_date = models.DateField("到職日", null=True, blank=True)
    resignation_date = models.DateField("離職日", null=True, blank=True)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records', verbose_name="員工")
    clock_in = models.DateTimeField("上班打卡")
    clock_out = models.DateTimeField("下班打卡", null=True, blank=True)
    note = models.CharField("備註", max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-clock_in']


class ShiftSchedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='shift_schedules', verbose_name="員工")
    shift_date = models.DateField("排班日期")
    start_time = models.TimeField("上班時間")
    end_time = models.TimeField("下班時間")
    shift_type = models.CharField("班別", max_length=50, blank=True, default='一般班')

    class Meta:
        ordering = ['-shift_date', 'start_time']


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('annual', '特休'),
        ('sick', '病假'),
        ('personal', '事假'),
        ('compensatory', '補休'),
    ]
    STATUS_CHOICES = [
        ('pending', '審核中'),
        ('approved', '已核准'),
        ('rejected', '已拒絕'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests', verbose_name="員工")
    leave_type = models.CharField("假別", max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField("起始日")
    end_date = models.DateField("結束日")
    reason = models.CharField("請假原因", max_length=255, blank=True, default='')
    status = models.CharField("審核狀態", max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-start_date']


class OvertimeRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', '審核中'),
        ('approved', '已核准'),
        ('rejected', '已拒絕'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_records', verbose_name="員工")
    work_date = models.DateField("加班日期")
    hours = models.DecimalField("加班時數", max_digits=5, decimal_places=2)
    reason = models.CharField("加班原因", max_length=255, blank=True, default='')
    status = models.CharField("審核狀態", max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-work_date']