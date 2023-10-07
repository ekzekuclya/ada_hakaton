from datetime import timedelta

from celery.utils.time import timezone

from .models import Event
from .serializers import EventSerializer, MixedScrollList
from rest_framework import viewsets, filters, response, status, generics
from rest_framework.decorators import action
from .permissions import DefaultPermission
from auth_app import models as auth_md, serializers as auth_sz
from .utils import get_client_ip
from random import shuffle
from rest_framework.views import APIView
from .tasks import notify_event_start


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(is_archived=False)
    serializer_class = EventSerializer
    permission_classes = [DefaultPermission]

    def create(self, request, *args, **kwargs):
        tags = request.data['tags']
        if tags:
            tags_list = []
            for i in request.data['tags']:
                tag, created = auth_md.Tag.objects.get_or_create(hashtag=i)
                tags_list.append(tag.id)
            request.data['tags'] = tags_list
        serializer = self.get_serializer(data=request.data)
        event = serializer.instance
        notify_event_start.apply_async((), eta=event.start_event_date - timedelta(hours=24))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = self.request.user
        if self.request.user.is_event_maker:
            serializer.save(user=user, priority='weeks_event')
        else:
            serializer.save(user=user, priority='users_event')

    @action(detail=True, methods=['POST'], url_path='follow')
    def follow(self, request, pk):
        event = Event.objects.get(id=pk)
        while event.limit_of_followers is None or event.count_followers() < event.limit_of_followers:
            if event.can_subscribe == 'all':
                if request.user.is_authenticated:
                    event.followers.add(request.user)
                    event.save()
                    return response.Response({"detail": "Вы успешно подписались"}, status=status.HTTP_200_OK)
                ip_address = get_client_ip(request)
                session_key = request.session.session_key
                if session_key:
                    anonymous, created = auth_md.AnonymousUser.objects.get_or_create(ip_address=ip_address)
                    anonymous.session_key = session_key
                    event.anonymous_followers.add(anonymous)
                    event.save()
                    return response.Response({"detail": "Вы успешно подписались "
                                                 "как Анонимный пользователь"}, status=status.HTTP_200_OK)
                return response.Response({"detail": "Вы успешно подписались"}, status=status.HTTP_200_OK)
            elif event.can_subscribe == 'authenticated_users':
                if request.user.is_authenticated:
                    if request.user not in event.followers.all():
                        event.followers.add(request.user)
                        event.save()
                        return response.Response({"detail": "Вы успешно подписались"}, status=status.HTTP_200_OK)
                    return response.Response({"detail": "Вы уже подписаны"})
                return response.Response({"detail": "Вы должны быть авторизованными, что бы подписаться"},
                                         status=status.HTTP_400_BAD_REQUEST)
            elif event.can_subscribe == 'friends':
                if request.user.is_authenticated:
                    request_user_profile = auth_md.UserProfile.objects.get(user=request.user)
                    event_user_profile = auth_md.UserProfile.objects.get(user=event.user)
                    if request_user_profile.user in event_user_profile.followers.all() and event_user_profile.user in request_user_profile.followers.all():
                        event.followers.add(request.user)
                        event.save()
                        return response.Response({"detail": "Вы успешно подписались"}, status=status.HTTP_200_OK)
                    return response.Response({"detail": "Вы должны быть подписаны друг на друга, что бы подписаться"},
                                             status=status.HTTP_400_BAD_REQUEST)
                return response.Response({"detail": "Вы должны авторизоваться и являться другом, что бы подписаться"},
                                         status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"detail": "Ивент уже набрал людей"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['GET'], url_path='subscribers')
    def get_subscribed_followers(self, request, pk):
        event = Event.objects.get(id=pk)
        subscribers = event.followers.all()
        serializer = auth_sz.LoginSerializer(subscribers, many=True)

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='public')
    def get_event_publications(self, request, pk):
        public = auth_md.UserPublication.objects.filter(event_id=pk)
        return response.Response(auth_sz.UserPublicationSerializer(public, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='tweet')
    def tweet(self, request, pk):
        user_profile = auth_md.UserProfile.objects.get(user=self.request.user)
        event = Event.objects.get(id=pk)
        description = self.request.data.get('description')
        if event.user == user_profile.user:
            if description:
                public = auth_md.UserPublication.objects.create(
                    user_profile=user_profile,
                    event=event,
                    description=description
                )
                return response.Response(auth_sz.UserPublicationSerializer(public).data, status=status.HTTP_200_OK)
            else:
                return response.Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)
        elif event.user != user_profile.user:
            if description:
                public = auth_md.UserPublication.objects.create(
                    user_profile=user_profile,
                    event=event,
                    description=description
                )
                return response.Response(auth_sz.UserPublicationSerializer(public).data, status=status.HTTP_200_OK)
            else:
                return response.Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({'error': 'You do not have permission to add publications to this event'},
                                     status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['POST'], url_path='remove-followers')
    def remove_follower_from_event_followers(self, request, pk):
        event = Event.objects.get(id=pk)
        if event:
            user = request.user
            if event.user == user:
                user_to_remove = request.data.get('users_id')
                if user_to_remove:
                    for i in user_to_remove:
                        user = auth_md.CustomUser.objects.get(id=i)
                        user_profile = auth_md.UserProfile.objects.get(user=user)
                        if user in event.followers.all():
                            event.followers.remove(user)
                            event.save()
                            if event in user_profile.future_events.all():
                                user_profile.future_events.remove(event)
                                user_profile.save()
                            return response.Response(EventSerializer(event).data, status=status.HTTP_200_OK)
                        return response.Response({"detail": "Указанного юзера нет в ваших ивент подписках"}, status=status.HTTP_400_BAD_REQUEST)
                    return response.Response(EventSerializer(event).data, status=status.HTTP_200_OK)
                return response.Response({"detail": "Введите id юзеров, которых хотите удалить"}, status=status.HTTP_400_BAD_REQUEST)
            return response.Response({"detail": "Вы не имеет право редактировать этот Ивент"}, status=status.HTTP_403_FORBIDDEN)
        return response.Response({"detail": "Ивент не найдет"}, status=status.HTTP_404_NOT_FOUND)


class MixedFeedView(APIView):
    permission_classes = [DefaultPermission]

    def get(self, request):
        events = Event.objects.filter(display_to_all=True)
        user_publications = auth_md.UserPublication.objects.all()

        serialized_events = EventSerializer(events, many=True).data
        serialized_user_publications = auth_sz.UserPublicationSerializer(user_publications, many=True).data

        combined_list = serialized_events + serialized_user_publications

        print(combined_list)
        shuffle(combined_list)

        return response.Response(combined_list)














