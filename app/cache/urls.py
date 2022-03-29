from django.urls import path

from . import views

app_name = 'cache'

urlpatterns = [
    path('', views.CacheCreateAPIView.as_view(), name='create'),
    path('list/', views.CacheListAPIView.as_view(), name='list'),
    path('key/<key>/', views.CacheAPIView.as_view(), name='detail'),
]
