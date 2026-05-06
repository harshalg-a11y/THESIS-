from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Payment


@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by("-created_at")
    return render(request, "payments/payment_list.html", {"payments": payments})
