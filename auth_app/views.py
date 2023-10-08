from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django_filters import exceptions
from rest_framework import generics, response, status, exceptions, viewsets
from .models import CustomUser as User, UserProfile, Notifications, UserPublication, Tag, Comment, AnonymousUser
from .serializers import (RegUserSerializer, LoginSerializer,
                          UserProfileSerializer, NotificationSerializer, UserPublicationSerializer, CommentSerializer)
from rest_framework.permissions import AllowAny
from .permissions import UserProfilePermission, NotificationPermission
from rest_framework.decorators import action
from haka_app import serializers as haka_sz, models as haka_md
from rest_framework.views import APIView
from random import randint, choice
from .utils import get_client_ip
from django.http import Http404, HttpResponseBadRequest
from random import shuffle


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

    # @action(detail=True, methods=['POST'], url_path='subscribe')
    # def follow(self, request, pk):
    #     current_user = request.user
    #     a = UserProfile.objects.get(id=pk)
    #     target_user = a.user
    #
    #     current_user_profile = UserProfile.objects.filter(user=request.user).first()
    #     target_user_profile = UserProfile.objects.filter(user=target_user).first()
    #
    #     current_user_profile.following.add(target_user)
    #     target_user_profile.followers.add(current_user)
    #
    #     current_user_profile.save()
    #     target_user_profile.save()
    #     return response.Response({"detail": "You subscribed"}, status=status.HTTP_200_OK)

    from rest_framework import status

    @action(detail=True, methods=['POST'], url_path='subscribe')
    def follow(self, request, pk):
        try:
           
                current_user = request.user
                a = UserProfile.objects.get(id=pk)
                target_user = a.user

                current_user_profile = UserProfile.objects.filter(user=request.user).first()
                target_user_profile = UserProfile.objects.filter(user=target_user).first()

                if not current_user_profile:
                    return response.Response({"detail": "Current user profile not found"}, status=status.HTTP_404_NOT_FOUND)

                if not target_user_profile:
                    return response.Response({"detail": "Target user profile not found"}, status=status.HTTP_404_NOT_FOUND)

                current_user_profile.following.add(target_user)
                target_user_profile.followers.add(current_user)

                current_user_profile.save()
                target_user_profile.save()
                return response.Response({"detail": "You subscribed"}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return response.Response({"detail": "UserProfile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    def get_following(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        following = user_profile.following.all()
        return response.Response(RegUserSerializer(following, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='visited-events')
    def get_visited_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        visited_events = user_profile.visited_events.all()
        return response.Response(haka_sz.EventSerializer(visited_events, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='future-events')
    def get_future_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        future_events = user_profile.future_events.all()
        print(future_events)
        return response.Response(haka_sz.EventSerializer(future_events, many=True).data, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['GET'], url_path='events')
    # def get_events(self, request, pk):
    #     user_profile = UserProfile.objects.get(id=pk)
    #     events = haka_md.Event.objects.filter(user=user_profile.user)
    #     return response.Response(haka_sz.EventSerializer(events, many=True).data, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=['GET'], url_path='public')
    def get_userprofile_publications(self, request, pk):
        public = UserPublication.objects.filter(user_profile_id=pk)
        return response.Response(UserPublicationSerializer(public, many=True).data, status=status.HTTP_200_OK)


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
    queryset = UserPublication.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            userprofile = UserProfile.objects.get(user=self.request.user)
            if userprofile:
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


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        publication_pk = self.kwargs.get('public_pk')
        try:
            publication = UserPublication.objects.get(id=publication_pk)
            comments = Comment.objects.filter(publication=publication)
            return comments
        except UserPublication.DoesNotExist:
            raise Http404("UserPublication matching query does not exist")

    def create(self, request, *args, **kwargs):
        publication_pk = self.kwargs.get('public_pk')
        if publication_pk:
            publication = UserPublication.objects.get(id=publication_pk)
            content = request.data.get('content')
            if content:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                if self.request.user.is_authenticated:
                    user = self.request.user
                    serializer.save(user=user, content=content, publication=publication)
                    headers = self.get_success_headers(serializer.data)
                    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                ip_address = get_client_ip(self.request)
                session_key = self.request.session.session_key
                if session_key:
                    anonymous, created = AnonymousUser.objects.get_or_create(ip_address=ip_address)
                    anonymous.session_key = session_key
                    serializer.save(anonymous=anonymous, content=content, publication=publication)
                    headers = self.get_success_headers(serializer.data)
                    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                return response.Response({"detail": "Нет сессии, вероятно вы подключены не через браузер"},
                                         status=status.HTTP_400_BAD_REQUEST)
            return response.Response({"detail": "Напишите content"}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({"detail": "Неверный айди публикации"}, status=status.HTTP_404_NOT_FOUND)


class TagViewSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        search_tags = request.GET.get('search', '')
        if not search_tags:
            return response.Response({"detail": "Параметр 'search' должен содержать хэштеги через запятую."},
                                     status=status.HTTP_400_BAD_REQUEST)

        search_tags_list = search_tags.split(',')

        events = haka_md.Event.objects.filter(display_to_all=True, tags__hashtag__in=search_tags_list)
        user_publications = UserPublication.objects.filter(tags__hashtag__in=search_tags_list)

        serialized_events = haka_sz.EventSerializer(events, many=True).data
        serialized_user_publications = UserPublicationSerializer(user_publications, many=True).data

        combined_list = serialized_events + serialized_user_publications
        shuffle(combined_list)

        return response.Response(combined_list)











