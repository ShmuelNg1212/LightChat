from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    """Django's sign-up form with LightChat's own help text; the validators are unchanged."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Letters, numbers and @ . + - _ only, up to 150 characters."
        self.fields["password1"].help_text = (
            "At least 8 characters. Avoid common passwords, all-number passwords, "
            "and anything close to your username."
        )
        self.fields["password2"].help_text = "Type the same password again."
