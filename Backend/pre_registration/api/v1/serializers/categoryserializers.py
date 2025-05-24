from rest_framework import serializers
from ....models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    - Used to convert Category model instances to JSON format and vice versa.
    - Includes fields: id, name.
    """

    class Meta:
        model = Category
        fields = ["id", "name"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep
