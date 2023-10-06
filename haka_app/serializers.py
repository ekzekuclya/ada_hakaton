from .models import Event
from rest_framework import serializers
from auth_app import serializers as sz


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class MixedScrollList(serializers.ModelSerializer):
    user_publication = sz.UserPublicationSerializer(many=True)
    events = EventSerializer(many=True)