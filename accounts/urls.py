from django.urls import path
from . import views

urlpatterns = [
    path('reset-password/', views.password_reset_request, name='password_reset'),
    path('reset-password/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]