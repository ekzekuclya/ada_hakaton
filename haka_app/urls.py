from rest_framework_nested import routers
from django.urls import path, include
from .views import EventViewSet

router = routers.DefaultRouter()
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),

]