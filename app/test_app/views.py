import cv2
import numpy as np
from django.core.files.base import ContentFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from test_app.models import UploadedImage
from test_app.serializers import ImageSerializer


class UploadImageView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_image = serializer.validated_data['image']
            # Загрузка предобученной модели YOLO
            net = cv2.dnn.readNet("yolo/yolov3.weights", "yolo/yolov3.cfg")
            with open("yolo/coco.names", "r") as f:
                classes = [line.strip() for line in f.readlines()]
            uploaded_image.seek(0)
            image_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
            image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
            output_layers = net.getUnconnectedOutLayersNames()

            height, width, channels = image.shape

            # Предобработка изображения для подачи на вход нейросети
            blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            # Подача blob на вход нейросети
            net.setInput(blob)
            outs = net.forward(output_layers)

            # Инициализация списков для обнаруженных объектов
            class_ids = []
            confidences = []
            boxes = []

            # Процесс обнаружения объектов
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:  # Установка порога уверенности
                        # Координаты рамки объекта
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        # Координаты верхнего левого угла рамки
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # Отбор наиболее значимых объектов
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # Рисование рамок и текста на изображении
            font = cv2.FONT_HERSHEY_PLAIN
            colors = np.random.uniform(0, 255, size=(len(classes), 3))
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]
                    color = colors[class_ids[i]]
                    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(image, f"{label}: {confidence:.2f}", (x, y + 30), font, 3, color, 3)

            _, processed_image_bytes = cv2.imencode('.jpg', image)
            processed_image_content = ContentFile(processed_image_bytes.tobytes(), name="processed_image.jpg")
            image_obj = UploadedImage(image=processed_image_content)
            image_obj.save()
            return Response({'message': 'Изображение успешно загружено'},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

