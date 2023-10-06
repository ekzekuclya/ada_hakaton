from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django_filters import exceptions
from rest_framework import generics, response, status, exceptions, viewsets
from .models import CustomUser as User, UserProfile, Notifications, UserPublication, Tag
from .serializers import (RegUserSerializer, LoginSerializer,
                          UserProfileSerializer, NotificationSerializer, UserPublicationSerializer)
from rest_framework.permissions import AllowAny
from .permissions import UserProfilePermission, NotificationPermission
from rest_framework.decorators import action
from haka_app import serializers as haka_sz, models as haka_md
from rest_framework.views import APIView
from random import randint, choice


class RegUserViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegUserSerializer
    permission_classes = [AllowAny]     # Исключение Auth






class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]     # Исключение auth

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,   # Сериализируем данные юзера
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'],
                            password=serializer.validated_data['password'])

        if not user:
            raise exceptions.AuthenticationFailed()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        token, _ = Token.objects.get_or_create(user=user)

        return response.Response(data={"token": token.key},
                                 status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [UserProfilePermission]

    @action(detail=True, methods=['POST'], url_path='subscribe')
    def follow(self, request, pk):
        current_user = request.user
        a = UserProfile.objects.get(id=pk)
        target_user = a.user

        current_user_profile = UserProfile.objects.filter(user=request.user).first()
        target_user_profile = UserProfile.objects.filter(user=target_user).first()

        current_user_profile.following.add(target_user)
        target_user_profile.followers.add(current_user)

        current_user_profile.save()
        target_user_profile.save()
        return response.Response({"detail": "You subscribed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='unsubscribe')
    def unfollow(self, request, pk):
        current_user = request.user
        a = UserProfile.objects.get(id=pk)
        target_user = a.user

        current_user_profile = UserProfile.objects.filter(user=request.user).first()
        target_user_profile = UserProfile.objects.filter(user=target_user).first()

        current_user_profile.following.remove(target_user)
        target_user_profile.followers.remove(current_user)

        current_user_profile.save()
        target_user_profile.save()
        return response.Response({"detail": "You unsubscribed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='followers')
    def get_followers(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        followers = user_profile.followers.all()
        return response.Response(RegUserSerializer(followers, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='following')
    def get_followers(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        following = user_profile.following.all()
        return response.Response(RegUserSerializer(following, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='visited-events')
    def get_visited_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        visited_events = user_profile.visited_events.all()
        return response.Response(haka_sz.EventSerializer(visited_events, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='future-events')
    def get_visited_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        future_events = user_profile.future_events.all()
        return response.Response(haka_sz.EventSerializer(future_events, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='events')
    def get_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        events = haka_md.Event.objects.filter(user=user_profile.user)
        return response.Response(haka_sz.EventSerializer(events, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='friends')
    def get_friends(self, request, pk):
        user_profile = self.get_object()
        friend_profiles = UserProfile.objects.filter(followers=user_profile.user)

        friends_list = []
        for friend_profile in friend_profiles:
            if user_profile.user in friend_profile.following.all():
                friends_list.append({
                    'user_id': friend_profile.user.id,
                    'username': friend_profile.user.username,
                })

        return response.Response(friends_list, status=status.HTTP_200_OK)


class NotificationViewSet(APIView):
    queryset = Notifications.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [NotificationPermission]

    def get(self, request):
        if self.request.user.is_authenticated:
            user = self.request.user
            notifications = Notifications.objects.filter(user=user)
            return response.Response(NotificationSerializer(notifications, many=True).data, status=status.HTTP_200_OK)
        else:
            return response.Response(NotificationSerializer(Notifications.objects.none()).data, status=status.HTTP_404_NOT_FOUND)


class UserPublicationView(viewsets.ModelViewSet):
    serializer_class = UserPublicationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_pk = self.kwargs.get('user_pk')

        if user_pk:
            user_profile = UserProfile.objects.get(user_id=user_pk)
            return UserPublication.objects.filter(user_profile=user_profile)
        else:
            return UserPublication.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            userprofile_pk = self.kwargs['user_pk']
            if userprofile_pk:
                userprofile = UserProfile.objects.get(id=userprofile_pk)
                serializer.save(user_profile=userprofile)

    def create(self, request, *args, **kwargs):
        tags = request.data.get('tags')
        if tags:
            tags_list = []
            for i in request.data['tags']:
                tag, created = Tag.objects.get_or_create(hashtag=i)
                tags_list.append(tag.id)
            request.data['tags'] = tags_list
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)















