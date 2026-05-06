from django.urls import path
from .views import request_list, request_detail, new_request

urlpatterns = [
    path("", request_list, name="request_list"),
    path("new/", new_request, name="new_request"),
    path("<int:request_id>/", request_detail, name="request_detail"),
]
