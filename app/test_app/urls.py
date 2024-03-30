from django.urls import path

from test_app.views import UploadImageView

urlpatterns = [
    path('upload-image/', UploadImageView.as_view(), name='upload_image'),
]