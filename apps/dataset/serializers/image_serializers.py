# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： image_serializers.py
    @date：2024/4/22 16:36
    @desc:
"""
import uuid

from django.db.models import QuerySet
from django.http import HttpResponse
from rest_framework import serializers

from common.exception.app_exception import NotFound404
from common.field.common import UploadedImageField
from common.util.field_message import ErrMessage
from dataset.models import Image


class ImageSerializer(serializers.Serializer):
    image = UploadedImageField(required=True, error_messages=ErrMessage.image("图片"))

    def upload(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        image_id = uuid.uuid1()
        image = Image(id=image_id, image=self.data.get('image').read(), image_name=self.data.get('image').name)
        image.save()
        return f'/api/image/{image_id}'

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True)

        def get(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            image_id = self.data.get('id')
            image = QuerySet(Image).filter(id=image_id).first()
            if image is None:
                raise NotFound404(404, "不存在的图片")
            if image.image_name.endswith('.svg'):
                return HttpResponse(image.image, status=200, headers={'Content-Type': 'image/svg+xml'})
            return HttpResponse(image.image, status=200, headers={'Content-Type': 'image/png'})
