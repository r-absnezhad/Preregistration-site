from rest_framework import serializers
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from ....models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, responsible for serializing and deserializing users.
    """

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_verified",
            "created_date",
            "updated_date",
            "password",
        ]
        read_only_fields = ["password"]

        def create(self, validated_data):
            # get password from request data
            password = validated_data.pop("password", None)
            # create user
            instance = self.Meta.model(**validated_data)
            if password is not None:
                instance.set_password(password)  # hashing the password
            instance.save()
            return instance


class CustomChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the user's password.
    This serializer ensures the old password is valid, and the new password meets the requirements.
    It also ensures that the new passwords match before saving the new password.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validate the passwords provided by the user.
        - Checks that the new password and its confirmation match.
        - Validates the new password against Django's password validation rules.
        """

        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"detail": "passwords must be the same"})
        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return super().validate(attrs)


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user, including validation of password and email.
    """

    password1 = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password1"]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password1"):
            raise serializers.ValidationError({"detail": "passwords must be the same"})
        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)


class ActivationResendApiViewSerializer(serializers.Serializer):
    """
    Serializer for handling requests to resend the account activation email.
    """

    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"details": "User does not exist."})

        if user_obj.is_verified:
            raise serializers.ValidationError(
                {"details": "User is already verified and activated."},
            )

        attrs["user"] = user_obj
        return super().validate(attrs)
