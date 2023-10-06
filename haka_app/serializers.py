from .models import Event
from rest_framework import serializers
from auth_app import serializers as sz


class EventSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    # followers = serializers.StringRelatedField(many=True)
    followers = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True)

    def get_followers(self, obj):
        # Ограничьте количество фолловеров до 10
        followers = obj.followers.all()[:10]

        # Если есть более 10 фолловеров, то верните их количество
        if obj.followers.count() > 5:
            return f"{obj.followers.count()} followers"

        # В противном случае, верните имена фолловеров
        return [follower.username for follower in followers]

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('priority', 'user')


class MixedScrollList(serializers.ModelSerializer):
    user_publication = sz.UserPublicationSerializer(many=True)
    events = EventSerializer(many=True)