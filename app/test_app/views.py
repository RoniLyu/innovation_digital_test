from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from test_app.models import UploadedImage
from test_app.serializers import ImageSerializer


class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            image_obj = UploadedImage(image=image)
            image_obj.save()
            return Response({'message': 'Изображение успешно загружено'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



