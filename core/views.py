from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import User
from projects.models import ThesisRequest
from messaging.models import Message


def home_view(request):
    return render(request, "core/home.html")


@login_required
def admin_analytics(request):
    if request.user.role != "admin":
        return render(request, "core/unauthorized.html")

    context = {
        "users": User.objects.count(),
        "clients": User.objects.filter(role="client").count(),
        "writers": User.objects.filter(role="writer").count(),
        "requests": ThesisRequest.objects.count(),
        "messages": Message.objects.count(),
    }
    return render(request, "core/admin_analytics.html", context)
