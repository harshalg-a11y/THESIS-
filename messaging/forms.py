from django import forms
from .models import Thread, Message
from accounts.models import User


class ThreadForm(forms.ModelForm):
    writer = forms.ModelChoiceField(queryset=User.objects.filter(role="writer"))

    class Meta:
        model = Thread
        fields = ["writer", "subject"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
