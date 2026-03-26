# employees/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r'list', EmployeeViewSet) # 設定為 /api/employees/list/
router.register(r'departments', DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]