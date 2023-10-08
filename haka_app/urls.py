from rest_framework_nested import routers
from django.urls import path, include
from .views import EventViewSet, MixedFeedView


router = routers.DefaultRouter()
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('mixed/', MixedFeedView.as_view(), name='mixed-feed'),

]