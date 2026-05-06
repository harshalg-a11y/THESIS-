from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard_view(request):
    role = request.user.role
    if role == "client":
        return render(request, "accounts/dashboard_client.html")
    if role == "writer":
        return render(request, "accounts/dashboard_writer.html")
    return render(request, "accounts/dashboard_admin.html")
