from django.urls import path
from .views import notification_list, mark_read

urlpatterns = [
    path("", notification_list, name="notification_list"),
    path("<int:notification_id>/read/", mark_read, name="notification_read"),
]
