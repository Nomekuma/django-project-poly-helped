from django import forms
from .models import Registration, Topic, Post


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            "first_name",
            "last_name",
            "email",
            "cohort",
            "campus",
            "date_of_birth",
            "motivation",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "motivation": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email") or ""
        return email.strip().lower()


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "category", "author_name"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["author_name", "content"]
        widgets = {"content": forms.Textarea(attrs={"rows": 4})}
