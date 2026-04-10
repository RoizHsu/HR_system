# employees/serializers.py
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from .models import AttendanceRecord, Department, Employee, LeaveRequest, OvertimeRecord, ShiftSchedule

class DepartmentSerializer(serializers.ModelSerializer):
    parent_name = serializers.ReadOnlyField(source='parent.name')

    class Meta:
        model = Department
        fields = ['id', 'name', 'parent', 'parent_name']


class EmployeeSerializer(serializers.ModelSerializer):
    # 顯示友善欄位名稱方便前端直接渲染
    department_name = serializers.ReadOnlyField(source='department.name')
    manager_name = serializers.ReadOnlyField(source='manager.name')

    class Meta:
        model = Employee
        exclude = ['password']
        read_only_fields = ['user']


class RegisterSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_account(self, value):
        if User.objects.filter(username=value).exists() or Employee.objects.filter(account=value).exists():
            raise serializers.ValidationError('此帳號已被使用。')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists() or Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError('此 Email 已被使用。')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '兩次密碼輸入不一致。'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        account = validated_data['account']
        email = validated_data['email']
        raw_password = validated_data['password']

        user = User.objects.create_user(username=account, email=email, password=raw_password)

        employee = Employee.objects.create(
            user=user,
            employee_id=f"EMP{timezone.now().strftime('%Y%m%d%H%M%S')}",
            account=account,
            email=email,
            password=user.password,
        )
        return employee


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '兩次新密碼輸入不一致。'})
        validate_password(attrs['new_password'])
        return attrs


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        read_only_fields = ['employee']


class ShiftScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftSchedule
        fields = '__all__'
        read_only_fields = ['employee']


class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['employee']


class OvertimeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRecord
        fields = '__all__'
        read_only_fields = ['employee']


class OrgChartNodeSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'parent', 'employees']

    def get_employees(self, obj):
        employees = Employee.objects.filter(department=obj).order_by('position_level', 'name')
        return [
            {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'name': employee.name,
                'job_title': employee.job_title,
                'position_level': employee.position_level,
                'manager_id': employee.manager_id,
            }
            for employee in employees
        ]