from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Thread, Message
from .forms import ThreadForm, MessageForm


@login_required
def thread_list(request):
    if request.user.role == "client":
        threads = Thread.objects.filter(client=request.user)
    else:
        threads = Thread.objects.filter(writer=request.user)
    return render(request, "messaging/thread_list.html", {"threads": threads})


@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    messages = thread.messages.all()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.sender = request.user
            msg.save()
            return redirect("thread_detail", thread_id=thread.id)
    else:
        form = MessageForm()
    return render(request, "messaging/thread_detail.html", {"thread": thread, "messages": messages, "form": form})


@login_required
def new_thread(request):
    if request.method == "POST":
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.client = request.user
            thread.save()
            return redirect("thread_list")
    else:
        form = ThreadForm()
    return render(request, "messaging/new_thread.html", {"form": form})
