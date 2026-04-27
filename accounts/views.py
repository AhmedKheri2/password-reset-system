from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password

from .forms import PasswordResetRequestForm


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                # Generate token and uid
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # Build reset link
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={
                        'uidb64': uid,
                        'token': token
                    })
                )

                # Send email (console backend for testing)
                subject = "Password Reset Request"
                message = f"Click the link below to reset your password:\n\n{reset_url}"

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

            return redirect('password_reset_done')

    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/reset_password.html', {'form': form})


def password_reset_done(request):
    return render(request, 'accounts/password_sent.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validate token
    if user is not None and default_token_generator.check_token(user, token):

        if request.method == "POST":
            password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            # Validation checks
            if not password or not confirm_password:
                return render(request, 'accounts/password_reset_confirm.html', {
                    'error': 'All fields are required.'
                })

            if password != confirm_password:
                return render(request, 'accounts/password_reset_confirm.html', {
                    'error': 'Passwords do not match.'
                })

            if len(password) < 6:
                return render(request, 'accounts/password_reset_confirm.html', {
                    'error': 'Password must be at least 6 characters long.'
                })

            # Set new password securely
            user.password = make_password(password)
            user.save()

            return redirect('password_reset_done')

        return render(request, 'accounts/password_reset_confirm.html')

    else:
        return render(request, 'accounts/password_reset_confirm.html', {
            'error': 'Invalid or expired reset link.'
        })