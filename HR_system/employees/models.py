from django.db import models

# Create your models here.
from django.db import models

class Department(models.Model):
    name = models.CharField("部門名稱", max_length=100)
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    # 枚舉選項
    GENDER_CHOICES = [('M', '男'), ('F', '女'), ('O', '其他')]
    TYPE_CHOICES = [('full_time', '全職'), ('part_time', '兼職'), ('intern', '實習')]
    STATUS_CHOICES = [('active', '在職'), ('resigned', '離職'), ('on_leave', '留停')]

    # 1. 個人資訊 (核心)
    employee_id = models.CharField("員工編號", max_length=20, unique=True)
    name = models.CharField("姓名", max_length=50)
    gender = models.CharField("性別", max_length=1, choices=GENDER_CHOICES)
    birthday = models.DateField("出生日期")
    id_number = models.CharField("身份證字號", max_length=10)
    phone = models.CharField("聯絡電話", max_length=20)
    address = models.TextField("地址")
    emergency_contact = models.CharField("緊急聯絡人姓名", max_length=50)
    emergency_phone = models.CharField("緊急聯絡人電話", max_length=20)

    # 2. 職位資訊
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="部門")
    job_title = models.CharField("職稱", max_length=100)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="直屬主管")
    emp_type = models.CharField("員工類型", max_length=20, choices=TYPE_CHOICES, default='full_time')
    status = models.CharField("員工狀態", max_length=20, choices=STATUS_CHOICES, default='active')

    # 3. 合約資訊
    hire_date = models.DateField("到職日")
    resignation_date = models.DateField("離職日", null=True, blank=True)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"