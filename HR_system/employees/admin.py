from django.contrib import admin
from .models import Department, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # 顯示的欄位
    list_display = ('employee_id', 'name', 'department', 'job_title', 'emp_type', 'status', 'hire_date')
    
    # 篩選器
    list_filter = ('department', 'emp_type', 'status', 'gender')
    
    # 搜尋框
    search_fields = ('employee_id', 'name', 'id_number')
    
    # 詳情頁的分組設定 (讓介面更整齊)
    fieldsets = (
        ('基本資訊', {
            'fields': ('employee_id', 'name', 'gender', 'birthday', 'id_number')
        }),
        ('職位與合約', {
            'fields': ('department', 'job_title', 'manager', 'emp_type', 'status', 'hire_date', 'resignation_date')
        }),
        ('聯絡資訊', {
            'fields': ('phone', 'address', 'emergency_contact', 'emergency_phone')
        }),
    )