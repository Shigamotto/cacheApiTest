from datetime import timedelta, datetime
from unittest import mock

import pytz
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase, override_settings
from freezegun import freeze_time
from rest_framework.test import APITestCase

from .models import CacheItem


class TestCreateApi(APITestCase):
    databases = {'default', 'mongodb'}

    def test_create(self):
        response = self.client.post(
            reverse('cache:create'), {
                'value': '123',
                'key': '456'
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                'value': '123',
                'key': '456'
            }
        )


class TestListApi(APITestCase):
    databases = {'default', 'mongodb'}
    url = reverse('cache:list')

    @classmethod
    def setUpTestData(cls):
        ttl = timezone.now() + timedelta(seconds=settings.CACHE_ITEM_TTL)
        CacheItem.objects.bulk_create([
            CacheItem(key='1', value='1', ttl=timezone.now() - timedelta(seconds=1)),
            CacheItem(key='2', value='2', ttl=ttl),
            CacheItem(key='3', value='3', ttl=ttl),
        ])

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), [{
                'value': '2',
                'key': '2'
            }, {
                'value': '3',
                'key': '3'
            }, ]
        )

    def test_delete(self):
        self.assertEqual(CacheItem.objects.count(), 3)
        response = self.client.delete(reverse('cache:list'))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CacheItem.objects.count(), 0)


@freeze_time('2022-03-29 16:17:00')
class TestDetailApi(APITestCase):
    databases = {'default', 'mongodb'}

    @classmethod
    def setUpTestData(cls):
        ttl = timezone.now() + timedelta(seconds=settings.CACHE_ITEM_TTL / 2)
        CacheItem.objects.bulk_create([
            CacheItem(key='1', value='1', ttl=timezone.now() - timedelta(seconds=1)),
            CacheItem(key='2', value='2', ttl=ttl),
        ])

    def test_get(self):
        response = self.client.get(reverse('cache:detail', args=['2']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'message': 'Cache Hit',
                'status': 'ok',
                'value': '2'
            }
        )
        self.assertEqual(
            CacheItem.objects.get(key='2').ttl,
            datetime(2022, 3, 29, 17, 17, tzinfo=pytz.UTC)
        )

    def test_get_not_exists(self):
        with mock.patch(
            'cache.views.create_random_string',
            return_value='123456'
        ):
            response = self.client.get(reverse('cache:detail', args=['3']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'message': 'Cache Miss',
                'status': 'error',
                'value': '123456'
            }
        )
        self.assertEqual(
            CacheItem.objects.get(key='3').ttl,
            datetime(2022, 3, 29, 17, 17, tzinfo=pytz.UTC)
        )

    def test_get_not_in_ttl(self):
        with mock.patch(
            'cache.views.create_random_string',
            return_value='234567'
        ):
            response = self.client.get(reverse('cache:detail', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'message': 'Cache Miss',
                'status': 'error',
                'value': '234567'
            }
        )
        self.assertEqual(
            CacheItem.objects.get(key='1').ttl,
            datetime(2022, 3, 29, 17, 17, tzinfo=pytz.UTC)
        )

    def test_put(self):
        response = self.client.put(
            reverse('cache:detail', args=['2']), {
                'value': '22'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'value': '22'
            }
        )
        self.assertEqual(
            CacheItem.objects.get(key='2').ttl,
            datetime(2022, 3, 29, 17, 17, tzinfo=pytz.UTC)
        )

    def test_put_not_exists(self):
        response = self.client.put(
            reverse('cache:detail', args=['3']), {
                'value': '333'
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_patch(self):
        response = self.client.patch(
            reverse('cache:detail', args=['2']), {
                'value': '2222'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {
                'value': '2222'
            }
        )
        self.assertEqual(
            CacheItem.objects.get(key='2').ttl,
            datetime(2022, 3, 29, 17, 17, tzinfo=pytz.UTC)
        )

    def test_patch_not_exists(self):
        response = self.client.put(
            reverse('cache:detail', args=['3']), {
                'value': '33333'
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        response = self.client.delete(reverse('cache:detail', args=['2']))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(CacheItem.objects.filter(key='2').exists())

    def test_delete_does_not_exists(self):
        response = self.client.delete(reverse('cache:detail', args=['3']))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(CacheItem.objects.count(), 2)


class TestModel(TestCase):
    databases = {'default', 'mongodb'}

    @override_settings(CACHE_ITEM_LIMIT=2)
    def test_save_by_limit(self):
        ttl = timezone.now() + timedelta(seconds=settings.CACHE_ITEM_TTL)
        CacheItem.objects.bulk_create([
            CacheItem(key='1', value='val-1', ttl=timezone.now() - timedelta(seconds=1)),
            CacheItem(key='2', value='val-2', ttl=ttl),
        ])
        item = CacheItem.objects.get(key='1')

        created_new_item = CacheItem.objects.create(key='3', value='val-3')
        self.assertEqual(created_new_item.pk, item.pk)

        item.refresh_from_db()
        self.assertEqual(item, created_new_item)
        self.assertEqual(item.key, '3')
        self.assertEqual(item.value, 'val-3')

    @override_settings(CACHE_ITEM_LIMIT=3)
    def test_save_lower_than_limit(self):
        ttl = timezone.now() + timedelta(seconds=settings.CACHE_ITEM_TTL)
        CacheItem.objects.bulk_create([
            CacheItem(key='1', value='val-1', ttl=timezone.now() - timedelta(seconds=1)),
            CacheItem(key='2', value='val-2', ttl=ttl),
        ])
        item = CacheItem.objects.get(key='1')

        created_new_item = CacheItem.objects.create(key='3', value='val-3')
        self.assertNotEqual(created_new_item.pk, item.pk)

        item.refresh_from_db()
        self.assertNotEqual(item, created_new_item)
        self.assertEqual(item.key, '1')
        self.assertEqual(item.value, 'val-1')

    @freeze_time('2022-03-29 16:17:00')
    def test_ttl(self):
        item = CacheItem.objects.create(key='1', value='val-1')
        self.assertEqual(item.ttl, datetime(2022, 3, 29, 17, 17, tzinfo=pytz.UTC))
