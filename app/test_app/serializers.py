from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from test_app.models import UploadedImage


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = UploadedImage
        fields = ('id', 'image')

    def validate_image(self, value):
        # Проверка формата изображения
        valid_formats = ['image/jpeg', 'image/png']
        if value.content_type not in valid_formats:
            raise ValidationError("Формат изображения должен быть JPEG или PNG.")

        # Проверка размера файла
        if value.size > 10485760:
            raise ValidationError("Размер файла изображения не должен превышать 10Мб.")

        return value
