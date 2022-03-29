from rest_framework import serializers

from .constants import Status
from .models import CacheItem


class BaseSerializer(serializers.Serializer):
    status = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    def get_status(self, obj):
        return 'ok'

    def get_message(self, obj):
        return ''


class CacheSerializer(serializers.Serializer, metaclass=serializers.SerializerMetaclass):
    value = serializers.CharField()

    def update(self, instance, validated_data):
        instance.value = validated_data['value']
        instance.save(update_fields=['value'])
        return instance


class CacheListItemSerializer(CacheSerializer):
    key = serializers.CharField(allow_blank=False)

    def create(self, validated_data):
        return CacheItem.objects.create(
            key=validated_data.get('key'),
            value=validated_data.get('value')
        )


class CacheMutableSerializer(BaseSerializer, CacheSerializer):

    def get_status(self, obj):
        if 'created' in self.context:
            return 'ok' if not self.context['created'] else 'error'
        raise ValueError(f'"created" value in context must be defined for {self.__class__.__name__}')

    def get_message(self, obj):
        if 'created' in self.context:
            return Status.MAP[not self.context['created']]
        raise ValueError(f'"created" value in context must be defined for {self.__class__.__name__}')
