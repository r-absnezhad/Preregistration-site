from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from ...models import Contact
from .serializers import ContactSerializer
from .permissions import IsAuthenticatedOrAdmin


class ContactViewSet(viewsets.ModelViewSet):
    """
    This viewset handles Contact objects, allowing CRUD operations on Contact records.It allows authenticated users
    to create new contact records, and admin users to view, update, and delete existing records.
    """

    permission_classes = [IsAuthenticatedOrAdmin]
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {"email": ["exact", "in"], "name": ["exact", "in"]}
    search_fields = ["email", "message", "subject"]
    ordering_fields = ["created_date", "email"]
