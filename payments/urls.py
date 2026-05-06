from django.urls import path
from .views import payment_list

urlpatterns = [
    path("", payment_list, name="payment_list"),
]
