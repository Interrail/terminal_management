from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class CustomTokenVerifySerializer(TokenVerifySerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        token = attrs["token"]

        try:
            token_obj = AccessToken(token)
            user = User.objects.get(id=token_obj["user_id"])
            data["user_id"] = user.id
            data["username"] = user.username
            data["first_name"] = user.first_name
            data["last_name"] = user.last_name
            # Add any other user fields you want to include
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        return data
