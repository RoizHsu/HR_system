# employees/views.py
from django.contrib.auth import authenticate
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
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


class ShiftScheduleViewSet(BaseSelfServiceViewSet):
    queryset = ShiftSchedule.objects.all()
    serializer_class = ShiftScheduleSerializer


class LeaveRequestViewSet(BaseSelfServiceViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer


class OvertimeRecordViewSet(BaseSelfServiceViewSet):
    queryset = OvertimeRecord.objects.all()
    serializer_class = OvertimeRecordSerializer


class OrgChartAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        departments = Department.objects.all().order_by('name')
        serializer = OrgChartNodeSerializer(departments, many=True)
        return Response({'departments': serializer.data})