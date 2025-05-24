from rest_framework import serializers
from ...models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contact model, responsible for serializing and deserializing contact form data.
    """

    class Meta:
        model = Contact
        fields = [
            "id",
            "name",
            "email",
            "subject",
            "message",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "created_date"]
