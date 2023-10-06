from rest_framework_nested import routers
from .views import RegUserViewSet,LoginView, UserProfileViewSet, NotificationViewSet, UserPublicationView
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)


router = routers.DefaultRouter()
router.register('user', UserProfileViewSet, basename='user')
router.register('notification', NotificationViewSet, basename='notification')

user_router = routers.NestedDefaultRouter(router, r'user', lookup='user')
user_router.register('publications', UserPublicationView, basename='publications')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(user_router.urls)),
    path('signup/', RegUserViewSet.as_view(), name='signup'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


]