from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.cdn.cdn import CDNService


class UploadFileApi(APIView):
    def post(self, request):
        file = request.FILES["file"]
        url = CDNService().upload(file)
        return Response(status=status.HTTP_200_OK, data={"url": url})
