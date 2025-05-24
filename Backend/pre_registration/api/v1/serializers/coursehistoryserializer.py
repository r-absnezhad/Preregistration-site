from rest_framework import serializers
from django.shortcuts import get_object_or_404
from accounts.models import User
from ....models import CourseHistory, Course


class ImportSerializer(serializers.Serializer):
    """
    Serializer for importing course history from an excel file, responsible for serializing and deserializing course history's data.
    """

    file = serializers.FileField()


class CourseHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseHistory model.
    - Handles serialization and deserialization of CourseHistory objects.
    - Includes additional custom fields and validation logic for enhanced functionality.
    """

    username_registration = serializers.CharField(write_only=True)
    username = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField(read_only=True)
    course = serializers.SlugRelatedField(
        queryset=Course.objects.all(),
        slug_field="name",
    )

    class Meta:
        model = CourseHistory
        fields = [
            "id",
            "username_registration",
            "username",
            "course",
            "grade",
            "status",
            "created_date",
        ]

    def get_status(self, obj):
        return obj.status

    def get_username(self, obj):
        return obj.profile.user.username

    def validate(self, data):
        user = get_object_or_404(User, username=data["username"])
        course = get_object_or_404(Course, name=data["course"])
        data["profile"] = user.profile
        data["course"] = course
        return data

    def create(self, validated_data):
        validated_data.pop("username")
        return super().create(validated_data)
