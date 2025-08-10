from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospitalViewSet, DepartmentViewSet

router = DefaultRouter()
router.register('hospitals', HospitalViewSet)
router.register('departments', DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
