from .models import Event
from .serializers import EventSerializer, MixedScrollList
from rest_framework import viewsets, filters, response, status, generics
from rest_framework.decorators import action
from .permissions import DefaultPermission
from auth_app import models as auth_md, serializers as auth_sz
from .utils import get_client_ip
from random import shuffle
from rest_framework.views import APIView


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [DefaultPermission]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    @action(detail=True, methods=['POST'], url_path='follow')
    def follow(self, request, pk):
        event = Event.objects.get(id=pk)
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


# class MixedFeedView(viewsets.ModelViewSet):
#     serializer_class = MixedScrollList
#     permission_classes = [DefaultPermission]
#
#     def get_queryset(self):
#         events = Event.objects.all()
#         user_publications = auth_md.UserPublication.objects.all()
#         mixed_feed = {
#             'user_publication': user_publications,
#             'events': events,
#         }
#         return mixed_feed


class MixedFeedView(APIView):
    permission_classes = [DefaultPermission]

    def get(self, request):
        events = Event.objects.all()
        user_publications = auth_md.UserPublication.objects.all()

        serialized_events = EventSerializer(events, many=True).data
        serialized_user_publications = auth_sz.UserPublicationSerializer(user_publications, many=True).data

        combined_list = serialized_events + serialized_user_publications

        shuffle(combined_list)

        return response.Response(combined_list)














