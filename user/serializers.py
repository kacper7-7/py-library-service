from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=5, write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
