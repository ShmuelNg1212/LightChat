from django import forms

from .models import Conversation


class RenameForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ["title"]
        labels = {"title": "Chat name"}

    def clean_title(self):
        title = " ".join(self.cleaned_data["title"].split())
        if not title:
            raise forms.ValidationError("Enter a name.")
        return title
