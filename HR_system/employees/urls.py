# employees/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceRecordViewSet,
    ChangePasswordAPIView,
    DepartmentViewSet,
    EmployeeViewSet,
    LeaveRequestViewSet,
    LoginAPIView,
    LogoutAPIView,
    OrgChartAPIView,
    OvertimeRecordViewSet,
    RegisterAPIView,
    ShiftScheduleViewSet,
)

router = DefaultRouter()
router.register(r'list', EmployeeViewSet) # 設定為 /api/employees/list/
router.register(r'departments', DepartmentViewSet)
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'shifts', ShiftScheduleViewSet, basename='shifts')
router.register(r'leaves', LeaveRequestViewSet, basename='leaves')
router.register(r'overtimes', OvertimeRecordViewSet, basename='overtimes')

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/logout/', LogoutAPIView.as_view()),
    path('auth/change-password/', ChangePasswordAPIView.as_view()),
    path('org-chart/', OrgChartAPIView.as_view()),
    path('', include(router.urls)),
]