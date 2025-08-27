from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegistrationForm, UserProfileForm


class RegisterView(CreateView):
    """
    User registration view.
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('tracker:dashboard')

    def form_valid(self, form):
        """Log in the user after successful registration."""
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome {user.get_short_name()}! Your account has been created successfully.')
        return response

    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard."""
        if request.user.is_authenticated:
            return redirect('tracker:dashboard')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    """
    User profile view.
    """
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        """Return the current user's profile."""
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    User profile edit view.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        """Return the current user's profile."""
        return self.request.user

    def form_valid(self, form):
        """Show success message after profile update."""
        messages.success(self.request, 'Your profile has been updated successfully.')
        return super().form_valid(form)
