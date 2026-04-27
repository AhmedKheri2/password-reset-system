from django import forms
from django.contrib.auth.models import User


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if user exists
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email.")

        return email