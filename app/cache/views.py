import random

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .models import CacheItem
from .serializers import (
    CacheMutableSerializer,
    CacheSerializer,
    CacheListItemSerializer
)
from .utils import create_random_string, create_ttl


class CacheCreateAPIView(generics.CreateAPIView):
    queryset = CacheItem.objects.all()
    serializer_class = CacheListItemSerializer


class CacheAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CacheItem.objects.all()
    serializer_class = CacheSerializer
    lookup_field = 'key'

    @swagger_auto_schema(
        operation_summary='[Extra logic if key does not exists.]',
        operation_description='If the key is not found in the cache:\n'
                              '- Log an output “Cache Miss”.\n'
                              '- Create a random string.\n'
                              '- Update the cache with this random string.\n'
                              '- Return the random string.\n\n'
                              'If the key is found in the cache:\n'
                              '- Log an output “Cache Hit”.\n'
                              '- Get the data for this key.\n'
                              '- Return the data.\n'
    )
    def get(self, request, *args, **kwargs):
        key = kwargs.get('key')
        obj, created = CacheItem.objects.get_or_create(
            key=key,
            defaults={
                'key': key,
                'value': create_random_string(random.randint(8, 12)),
            }
        )
        if not created and obj.ttl < timezone.now():
            created = True
            obj.value = create_random_string(random.randint(8, 12))
            obj.save(update_fields=['value'])
        return Response(
            CacheMutableSerializer(obj, context={'created': created}).data
        )


class CacheListAPIView(generics.ListAPIView):
    queryset = CacheItem.objects.all()
    serializer_class = CacheListItemSerializer

    def get_queryset(self):
        return self.queryset.filter(
            ttl__gte=timezone.now()
        )

    def delete(self, request, *args, **kwargs):
        self.queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
