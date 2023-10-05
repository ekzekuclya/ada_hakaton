from .models import CustomUser as User, UserProfile, Notifications
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


# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username')
#     followers = serializers.SerializerMethodField()
#     following = serializers.SerializerMethodField()
#
#     def get_followers(self, obj):
#         return UserSerializer(obj.followers.all(), many=True).data
#
#     def get_following(self, obj):
#         return UserSerializer(obj.following.all(), many=True).data
#
#     class Meta:
#         model = UserProfile
#         fields = ['user', 'followers', 'following']

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
        fields = ['user', 'followers', 'following']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'content']


