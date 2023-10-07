from .models import CustomUser as User, UserProfile, Notifications, UserPublication, Tag, Comment
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class RegUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save(update_fields=['password'])
        # request = self.context.get('request')
        # ip = get_client_ip(request)
        # save_signup_info.delay(user.id, ip)

        return user

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.pop('email')
        res['id'] = instance.id
        return res


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    model = User
    fields = ['username']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    def get_followers(self, obj):
        return obj.followers.count()

    def get_following(self, obj):
        return obj.following.count()

    class Meta:
        model = UserProfile
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserPublicationSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True).data
    user_profile = serializers.SerializerMethodField()
    event_info = serializers.SerializerMethodField()

    def get_user_profile(self, obj):
        user_profile = obj.user_profile
        if user_profile:
            return user_profile.user.username
        return None

    def get_event_info(self, obj):
        if obj.event:
            event = obj.event
            event_info = {
                'id': event.id,
                'title': event.title,
                'followers': event.followers.count()  # Количество фолловеров события
            }
            return event_info
        return None

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user_profile_info = res.pop('user_profile')
        if user_profile_info:
            res['user_profile'] = user_profile_info
        event_info = res.pop('event_info')
        if event_info:
            res['event'] = event_info
        return res

    class Meta:
        model = UserPublication
        fields = '__all__'
        read_only_fields = ('user_profile',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('user', 'anonymous')
