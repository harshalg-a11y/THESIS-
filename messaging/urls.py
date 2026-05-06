from django.urls import path
from .views import thread_list, thread_detail, new_thread, messages_json

urlpatterns = [
    path("", thread_list, name="thread_list"),
    path("new/", new_thread, name="new_thread"),
    path("<int:thread_id>/", thread_detail, name="thread_detail"),
    path("<int:thread_id>/json/", messages_json, name="messages_json"),
]
