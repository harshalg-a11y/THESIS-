from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ThesisRequest
from .forms import ThesisRequestForm, MilestoneForm, AttachmentForm, StatusForm


@login_required
def request_list(request):
    if request.user.role == "client":
        requests = ThesisRequest.objects.filter(client=request.user)
    elif request.user.role == "writer":
        requests = ThesisRequest.objects.filter(writer=request.user)
    else:
        requests = ThesisRequest.objects.all()
    return render(request, "projects/request_list.html", {"requests": requests})


@login_required
def request_detail(request, request_id):
    thesis_request = get_object_or_404(ThesisRequest, id=request_id)
    milestone_form = MilestoneForm()
    attachment_form = AttachmentForm()
    status_form = StatusForm(instance=thesis_request)

    if request.method == "POST":
        if "add_milestone" in request.POST:
            milestone_form = MilestoneForm(request.POST)
            if milestone_form.is_valid():
                milestone = milestone_form.save(commit=False)
                milestone.request = thesis_request
                milestone.save()
                return redirect("request_detail", request_id=thesis_request.id)
        if "add_attachment" in request.POST:
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.request = thesis_request
                attachment.save()
                return redirect("request_detail", request_id=thesis_request.id)
        if "update_status" in request.POST:
            status_form = StatusForm(request.POST, instance=thesis_request)
            if status_form.is_valid():
                status_form.save()
                return redirect("request_detail", request_id=thesis_request.id)

    return render(
        request,
        "projects/request_detail.html",
        {
            "request_item": thesis_request,
            "milestone_form": milestone_form,
            "attachment_form": attachment_form,
            "status_form": status_form,
        },
    )


@login_required
def new_request(request):
    if request.method == "POST":
        form = ThesisRequestForm(request.POST)
        if form.is_valid():
            thesis_request = form.save(commit=False)
            thesis_request.client = request.user
            thesis_request.save()
            return redirect("request_list")
    else:
        form = ThesisRequestForm()
    return render(request, "projects/new_request.html", {"form": form})
