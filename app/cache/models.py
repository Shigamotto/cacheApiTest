from django.conf import settings
from djongo import models

from .utils import create_ttl


class CacheItem(models.Model):
    key = models.CharField(max_length=255, db_index=True, unique=True)
    value = models.TextField()
    ttl = models.DateTimeField()

    def save(self, **kwargs):
        """
        IMPORTANT!!! ttl updates any time, when you use method save.
        """
        count = self.__class__.objects.count()
        if count >= settings.CACHE_ITEM_LIMIT and not self.pk:
            kwargs.update({'force_insert': False})
            self.pk = self.__class__.objects.order_by('ttl').first().pk
        self.ttl = create_ttl()
        if 'update_fields' in kwargs:
            kwargs['update_fields'].append('ttl')
        super().save(**kwargs)
