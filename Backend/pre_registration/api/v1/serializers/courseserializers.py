from rest_framework import serializers
from ....models import Course
from .categoryserializers import CategorySerializer


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Course model.
    - Responsible for serializing and deserializing Course data.
    - Includes nested serialization for the related Category model.
    """

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "credit",
            "category",
            "prerequisite_course",
            "created_date",
            "updated_date",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category"] = CategorySerializer(
            instance.category, context=self.context
        ).data
        return rep
