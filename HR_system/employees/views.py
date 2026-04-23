# employees/views.py
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from .models import AttendanceRecord, Department, Employee, LeaveRequest, OvertimeRecord, ShiftSchedule
from .serializers import (
    AttendanceRecordSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    LeaveRequestSerializer,
    LoginSerializer,
    OrgChartNodeSerializer,
    OvertimeRecordSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    ShiftScheduleSerializer,
)


def get_current_employee(request):
    return Employee.objects.filter(user=request.user).first()


def get_employee_editor_groups():
    return set(getattr(settings, 'EMPLOYEE_EDITOR_GROUPS', ['人資群組', '工程主管']))


def can_manage_employee_data(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=get_employee_editor_groups()).exists()


def auto_approve_overtimes(queryset):
    threshold = timezone.now() - timedelta(hours=24)
    pending_records = queryset.filter(status='pending', requested_at__lte=threshold)
    if pending_records.exists():
        pending_records.update(status='approved', auto_approved=True, approved_at=timezone.now())


class EmployeeViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    editor_editable_fields = {
        'employee_id',
        'account',
        'email',
        'name',
        'gender',
        'birthday',
        'id_number',
        'phone',
        'address',
        'emergency_contact',
        'emergency_phone',
        'department',
        'job_title',
        'manager',
        'emp_type',
        'status',
        'position_level',
        'hire_date',
        'resignation_date',
    }

    def get_queryset(self):
        if can_manage_employee_data(self.request.user):
            return Employee.objects.all()

        employee = get_current_employee(self.request)
        if not employee:
            return Employee.objects.none()
        return Employee.objects.filter(pk=employee.pk)

    def _validate_editor_update_fields(self, request):
        disallowed = [field for field in request.data.keys() if field not in self.editor_editable_fields]
        if disallowed:
            return Response(
                {
                    'detail': '包含無法修改的欄位。',
                    'disallowed_fields': disallowed,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def _ensure_editor_permission(self, request):
        if can_manage_employee_data(request.user):
            return None
        return Response({'detail': '你沒有權限修改員工資料。'}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        denied = self._ensure_editor_permission(request)
        if denied:
            return denied
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        denied = self._ensure_editor_permission(request)
        if denied:
            return denied

        invalid_fields = self._validate_editor_update_fields(request)
        if invalid_fields:
            return invalid_fields
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        denied = self._ensure_editor_permission(request)
        if denied:
            return denied

        invalid_fields = self._validate_editor_update_fields(request)
        if invalid_fields:
            return invalid_fields
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        denied = self._ensure_editor_permission(request)
        if denied:
            return denied
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployeeSerializer(employee, context={'request': request}).data)

    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_me(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)

        denied = self._ensure_editor_permission(request)
        if denied:
            return denied

        invalid_fields = self._validate_editor_update_fields(request)
        if invalid_fields:
            return invalid_fields

        serializer = EmployeeSerializer(employee, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='company-edit-access')
    def company_edit_access(self, request):
        return Response(
            {
                'can_manage_employee_data': can_manage_employee_data(request.user),
                'allowed_groups': sorted(list(get_employee_editor_groups())),
            }
        )


class DepartmentViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        token, _ = Token.objects.get_or_create(user=employee.user)
        return Response(
            {
                'token': token.key,
                'employee': EmployeeSerializer(employee, context={'request': request, 'auth_user': employee.user}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account = serializer.validated_data['account']
        password = serializer.validated_data['password']

        user = authenticate(username=account, password=password)
        if not user:
            return Response({'detail': '帳號或密碼錯誤'}, status=status.HTTP_400_BAD_REQUEST)

        employee = Employee.objects.filter(user=user).first()
        if not employee:
            return Response({'detail': '帳號未綁定員工資料'}, status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'employee': EmployeeSerializer(employee, context={'request': request, 'auth_user': user}).data,
            }
        )


class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response({'detail': '已登出'})


class ChangePasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({'old_password': ['舊密碼不正確。']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        employee = Employee.objects.filter(user=user).first()
        if employee:
            employee.password = user.password
            employee.save(update_fields=['password'])

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return Response({'detail': '密碼已更新', 'token': token.key})


class BaseSelfServiceViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        employee = get_current_employee(self.request)
        if not employee:
            return self.queryset.none()
        return self.queryset.filter(employee=employee)

    def perform_create(self, serializer):
        employee = get_current_employee(self.request)
        serializer.save(employee=employee)


class AttendanceRecordViewSet(BaseSelfServiceViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer

    @action(detail=False, methods=['get'], url_path='today-status')
    def today_status(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)

        latest = AttendanceRecord.objects.filter(
            employee=employee,
            clock_in__date=timezone.localdate(),
        ).order_by('-clock_in').first()
        return Response(
            {
                'has_clock_in': bool(latest),
                'clocked_out': bool(latest and latest.clock_out),
                'record': AttendanceRecordSerializer(latest).data if latest else None,
            }
        )

    @action(detail=False, methods=['post'], url_path='clock-in')
    def clock_in(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)

        opened_record = AttendanceRecord.objects.filter(
            employee=employee,
            clock_in__date=timezone.localdate(),
            clock_out__isnull=True,
        ).order_by('-clock_in').first()
        if opened_record:
            return Response({'detail': '今天已經打卡上班，尚未打卡下班。'}, status=status.HTTP_400_BAD_REQUEST)

        record = AttendanceRecord.objects.create(employee=employee, clock_in=timezone.now())
        return Response(AttendanceRecordSerializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='clock-out')
    def clock_out(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)

        opened_record = AttendanceRecord.objects.filter(
            employee=employee,
            clock_in__date=timezone.localdate(),
            clock_out__isnull=True,
        ).order_by('-clock_in').first()
        if not opened_record:
            return Response({'detail': '今天尚未打卡上班，無法打卡下班。'}, status=status.HTTP_400_BAD_REQUEST)

        # 計算工時（小時數）
        now = timezone.now()
        hours_worked = (now - opened_record.clock_in).total_seconds() / 3600
        
        # 檢查是否達到 8 小時
        if hours_worked < 8:
            # 未滿 8 小時，需要備註
            note = request.data.get('note', '').strip()
            if not note:
                return Response(
                    {'detail': '未滿 8 小時工作，必須提供下班備註。'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            opened_record.note = note
        
        opened_record.clock_out = now
        opened_record.save()
        return Response(AttendanceRecordSerializer(opened_record).data)


class ShiftScheduleViewSet(BaseSelfServiceViewSet):
    queryset = ShiftSchedule.objects.all()
    serializer_class = ShiftScheduleSerializer


class LeaveRequestViewSet(BaseSelfServiceViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    @action(detail=False, methods=['get'], url_path='pending-approvals')
    def pending_approvals(self, request):
        """查詢當前登入用戶作為主管的待審核請假"""
        manager = get_current_employee(request)
        if not manager:
            return Response([], status=status.HTTP_200_OK)

        pending = LeaveRequest.objects.filter(
            employee__manager=manager,
            status='pending'
        ).order_by('-start_date')
        return Response(LeaveRequestSerializer(pending, many=True).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """核准請假"""
        manager = get_current_employee(request)
        if not manager:
            return Response({'detail': '找不到主管資料'}, status=status.HTTP_404_NOT_FOUND)

        leave = LeaveRequest.objects.filter(pk=pk, employee__manager=manager).first()
        if not leave:
            return Response({'detail': '找不到可審核的請假申請'}, status=status.HTTP_404_NOT_FOUND)
        if leave.status != 'pending':
            return Response({'detail': '此申請已處理'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = 'approved'
        leave.approved_by = manager
        leave.approved_at = timezone.now()
        leave.save(update_fields=['status', 'approved_by', 'approved_at'])
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """拒絕請假"""
        manager = get_current_employee(request)
        if not manager:
            return Response({'detail': '找不到主管資料'}, status=status.HTTP_404_NOT_FOUND)

        leave = LeaveRequest.objects.filter(pk=pk, employee__manager=manager).first()
        if not leave:
            return Response({'detail': '找不到可審核的請假申請'}, status=status.HTTP_404_NOT_FOUND)
        if leave.status != 'pending':
            return Response({'detail': '此申請已處理'}, status=status.HTTP_400_BAD_REQUEST)

        leave.status = 'rejected'
        leave.approved_by = manager
        leave.approved_at = timezone.now()
        leave.save(update_fields=['status', 'approved_by', 'approved_at'])
        return Response(LeaveRequestSerializer(leave).data)


class OvertimeRecordViewSet(BaseSelfServiceViewSet):
    queryset = OvertimeRecord.objects.all()
    serializer_class = OvertimeRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        auto_approve_overtimes(queryset)
        return queryset

    @action(detail=False, methods=['get'], url_path='pending-approvals')
    def pending_approvals(self, request):
        manager = get_current_employee(request)
        if not manager:
            return Response([], status=status.HTTP_200_OK)

        queryset = OvertimeRecord.objects.filter(employee__manager=manager)
        auto_approve_overtimes(queryset)
        pending = queryset.filter(status='pending').order_by('requested_at')
        return Response(OvertimeRecordSerializer(pending, many=True).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        manager = get_current_employee(request)
        if not manager:
            return Response({'detail': '找不到主管資料'}, status=status.HTTP_404_NOT_FOUND)

        record = OvertimeRecord.objects.filter(pk=pk, employee__manager=manager).first()
        if not record:
            return Response({'detail': '找不到可審核的加班申請'}, status=status.HTTP_404_NOT_FOUND)
        if record.status != 'pending':
            return Response({'detail': '此申請已處理'}, status=status.HTTP_400_BAD_REQUEST)

        record.status = 'approved'
        record.auto_approved = False
        record.approved_by = manager
        record.approved_at = timezone.now()
        record.save(update_fields=['status', 'auto_approved', 'approved_by', 'approved_at'])
        return Response(OvertimeRecordSerializer(record).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        manager = get_current_employee(request)
        if not manager:
            return Response({'detail': '找不到主管資料'}, status=status.HTTP_404_NOT_FOUND)

        record = OvertimeRecord.objects.filter(pk=pk, employee__manager=manager).first()
        if not record:
            return Response({'detail': '找不到可審核的加班申請'}, status=status.HTTP_404_NOT_FOUND)
        if record.status != 'pending':
            return Response({'detail': '此申請已處理'}, status=status.HTTP_400_BAD_REQUEST)

        record.status = 'rejected'
        record.auto_approved = False
        record.approved_by = manager
        record.approved_at = timezone.now()
        record.save(update_fields=['status', 'auto_approved', 'approved_by', 'approved_at'])
        return Response(OvertimeRecordSerializer(record).data)


class OrgChartAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        departments = Department.objects.all().order_by('name')
        serializer = OrgChartNodeSerializer(departments, many=True)
        return Response({'departments': serializer.data})

