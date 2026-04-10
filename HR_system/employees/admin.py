from django.contrib import admin
from .models import AttendanceRecord, Department, Employee, LeaveRequest, OvertimeRecord, ShiftSchedule

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # 顯示的欄位
    list_display = ('employee_id', 'account', 'name', 'department', 'job_title', 'emp_type', 'status', 'hire_date')
    
    # 篩選器
    list_filter = ('department', 'emp_type', 'status', 'gender')
    
    # 搜尋框
    search_fields = ('employee_id', 'name', 'id_number')
    
    # 詳情頁的分組設定 (讓介面更整齊)
    fieldsets = (
        ('基本資訊', {
            'fields': ('account','employee_id', 'name', 'gender', 'birthday', 'id_number')
        }),
        ('職位與合約', {
            'fields': ('department', 'job_title', 'manager', 'emp_type', 'status', 'hire_date', 'resignation_date')
        }),
        ('聯絡資訊', {
            'fields': ('phone', 'address', 'emergency_contact', 'emergency_phone')
        }),
    )


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'clock_in', 'clock_out', 'note')
    list_filter = ('clock_in', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__name', 'employee__account', 'note')
    ordering = ('-clock_in',)


@admin.register(ShiftSchedule)
class ShiftScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift_date', 'start_time', 'end_time', 'shift_type')
    list_filter = ('shift_date', 'shift_type', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__name', 'employee__account', 'shift_type')
    ordering = ('-shift_date', 'start_time')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'reason')
    list_filter = ('leave_type', 'status', 'start_date', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__name', 'employee__account', 'reason')
    ordering = ('-start_date',)


@admin.register(OvertimeRecord)
class OvertimeRecordAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'work_date',
        'hours',
        'status',
        'auto_approved',
        'approved_by',
        'requested_at',
        'approved_at',
    )
    list_filter = ('status', 'auto_approved', 'work_date', 'employee__department')
    search_fields = ('employee__employee_id', 'employee__name', 'employee__account', 'reason')
    ordering = ('-requested_at',)