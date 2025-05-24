from rest_framework import serializers
from accounts.api.v1.serializers import ProfileSerializer
from accounts.models import Profile
from ....models import Registrations, Course


class RegistrationsSerializer(serializers.ModelSerializer):
    """
    Serializer for the Registrations model.
    - Handles the serialization and deserialization of Registrations data.
    - Supports nested and customized representations for related fields.
    """

    courses_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all(),
    )

    class Meta:
        model = Registrations
        fields = [
            "id",
            "term",
            # "user_id",
            "courses_id",
            "created_date",
            "updated_date",
        ]
        # read_only_fields = ["user_id"]

    def get_course_names(self, instance):
        # showing names of courses
        return [course.name for course in instance.courses_id.all()]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # rep["user_id"] = ProfileSerializer(instance.user_id).data
        # rep["user_id"] = rep["user_id"]["username"]
        rep["user"] = instance.user_id.user.username
        rep["courses_id"] = [course.name for course in instance.courses_id.all()]
        return rep

    def create(self, validated_data):
        # validated_data["user_id"] = Profile.objects.get(
        #     user__id=self.context.get("request").user.id
        # )
        validated_data["user_id"] = Profile.objects.get(
            user=self.context.get("request").user
        )
        return super().create(validated_data)
