from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DrJegViewSet

router = DefaultRouter()
router.register('', DrJegViewSet, basename='dr-jeg')

urlpatterns = [
    path('', include(router.urls)),
]
