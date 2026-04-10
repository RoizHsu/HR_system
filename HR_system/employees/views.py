# employees/views.py
from django.contrib.auth import authenticate
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


def auto_approve_overtimes(queryset):
    threshold = timezone.now() - timedelta(hours=12)
    pending_records = queryset.filter(status='pending', requested_at__lte=threshold)
    if pending_records.exists():
        pending_records.update(status='approved', auto_approved=True, approved_at=timezone.now())


class EmployeeViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployeeSerializer(employee).data)

    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_me(self, request):
        employee = get_current_employee(request)
        if not employee:
            return Response({'detail': '找不到對應員工資料'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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
                'employee': EmployeeSerializer(employee).data,
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
                'employee': EmployeeSerializer(employee).data,
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

        opened_record.clock_out = timezone.now()
        opened_record.save(update_fields=['clock_out'])
        return Response(AttendanceRecordSerializer(opened_record).data)


class ShiftScheduleViewSet(BaseSelfServiceViewSet):
    queryset = ShiftSchedule.objects.all()
    serializer_class = ShiftScheduleSerializer


class LeaveRequestViewSet(BaseSelfServiceViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer


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