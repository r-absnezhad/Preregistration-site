from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class IndexAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"details": "Main Page"}, status=status.HTTP_200_OK)
