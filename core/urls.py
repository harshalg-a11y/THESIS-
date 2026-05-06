from django.urls import path
from .views import home_view, admin_analytics

urlpatterns = [
    path("", home_view, name="home"),
    path("analytics/", admin_analytics, name="admin_analytics"),
]
