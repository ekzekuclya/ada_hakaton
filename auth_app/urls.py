from rest_framework_nested import routers
from .views import (RegUserViewSet,LoginView, UserProfileViewSet, NotificationViewSet,
                    UserPublicationView, CommentViewSet, TagViewSet)
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)
from . import consumers

websocket_urlpatterns = [
    path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
]

router = routers.DefaultRouter()
router.register('user', UserProfileViewSet, basename='user')
router.register('public', UserPublicationView, basename='public')

public_router = routers.NestedDefaultRouter(router, r'public', lookup='public')
public_router.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(public_router.urls)),
    path('signup/', RegUserViewSet.as_view(), name='signup'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('notification/', NotificationViewSet.as_view(), name='notification'),
    path('tags/', TagViewSet.as_view(), name='tag'),
]
