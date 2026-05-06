from django import forms
from .models import ThesisRequest, Milestone, Attachment
from accounts.models import User


class ThesisRequestForm(forms.ModelForm):
    writer = forms.ModelChoiceField(queryset=User.objects.filter(role="writer"))

    class Meta:
        model = ThesisRequest
        fields = ["writer", "title", "description", "budget", "deadline"]


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["title", "due_date", "is_completed"]


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["file"]


class StatusForm(forms.ModelForm):
    class Meta:
        model = ThesisRequest
        fields = ["status"]
