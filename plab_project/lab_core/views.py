from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordChangeView as DjangoPasswordChangeView
from django.views.generic import TemplateView, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import translation

from .models import LabResult, PatientProfile, BlogPost
from .forms import PatientSignUpForm, AccountProfileForm


class PatientLoginForm(AuthenticationForm):
    """Login form that uses phone_number as the username field."""
    username = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your phone number"),
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your password"),
            }
        ),
    )


class PatientLoginView(LoginView):
    """Patient login view based on Django's built-in LoginView."""
    template_name = "lab_core/login.html"
    authentication_form = PatientLoginForm
    redirect_authenticated_user = True


class SignUpView(CreateView):
    """Patient registration view using phone_number-based user model."""
    template_name = "lab_core/signup.html"
    form_class = PatientSignUpForm
    success_url = reverse_lazy("lab_core:login")


class HomeView(TemplateView):
    """Public home page that displays health advice posts."""
    template_name = "lab_core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = (
            BlogPost.objects.select_related("posted_by")
            .annotate(hearts_total=Count("hearts"))
            .order_by("-is_pinned", "-created_at")
        )
        return context


class AboutView(TemplateView):
    """About page for PLAB (public)."""
    template_name = "lab_core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = translation.get_language() or ""
        if lang.startswith("ar"):
            context["lab_description"] = (
                getattr(settings, "PLAB_ABOUT_DESCRIPTION_AR", "") or getattr(settings, "PLAB_ABOUT_DESCRIPTION", "") or ""
            )
            context["lab_address"] = (
                getattr(settings, "PLAB_ABOUT_ADDRESS_AR", "") or getattr(settings, "PLAB_ABOUT_ADDRESS", "") or ""
            )
        else:
            context["lab_description"] = getattr(settings, "PLAB_ABOUT_DESCRIPTION", "") or ""
            context["lab_address"] = getattr(settings, "PLAB_ABOUT_ADDRESS", "") or ""
        context["lab_phone"] = getattr(settings, "PLAB_ABOUT_PHONE", "") or ""
        if lang.startswith("ar"):
            context["lab_hours"] = (
                getattr(settings, "PLAB_ABOUT_HOURS_AR", "") or getattr(settings, "PLAB_ABOUT_HOURS", "") or ""
            )
        else:
            context["lab_hours"] = getattr(settings, "PLAB_ABOUT_HOURS", "") or ""
        context["map_embed_url"] = getattr(settings, "PLAB_MAP_EMBED_URL", "") or ""
        return context


class BlogPostDetailView(TemplateView):
    template_name = "lab_core/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(
            BlogPost.objects.select_related("posted_by").annotate(hearts_total=Count("hearts")),
            pk=self.kwargs["pk"],
        )
        context["post"] = post
        context["has_hearted"] = (
            self.request.user.is_authenticated and post.hearts.filter(pk=self.request.user.pk).exists()
        )
        return context


class ProfileView(LoginRequiredMixin, FormView):
    """Let patients update name, age, and gender."""

    template_name = "lab_core/profile.html"
    form_class = AccountProfileForm
    success_url = reverse_lazy("lab_core:profile")
    login_url = "lab_core:login"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, DjangoPasswordChangeView):
    """Allow users to securely update their password after initial login."""
    template_name = "lab_core/password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("lab_core:profile")
    login_url = "lab_core:login"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your password has been updated.")
        return response


class ToggleHeartView(LoginRequiredMixin, View):
    """Add/remove a heart reaction for the current logged-in user."""
    login_url = "lab_core:login"

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        if post.hearts.filter(pk=request.user.pk).exists():
            post.hearts.remove(request.user)
        else:
            post.hearts.add(request.user)
        return redirect(request.POST.get("next") or "lab_core:home")


class DashboardView(LoginRequiredMixin, TemplateView):
    """Show all lab tests for the logged-in patient."""
    template_name = "lab_core/dashboard.html"
    login_url = "lab_core:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = LabResult.objects.filter(
            patient=self.request.user,
        ).order_by("-recorded_date")

        # Avoid broken links by exposing only files that exist on disk.
        for result in results:
            file_name = getattr(result.pdf_result, "name", None)
            result.has_file = bool(file_name) and result.pdf_result.storage.exists(file_name)
            result.can_download = (
                result.is_published
                and result.status == "COMPLETED"
                and result.has_file
            )

        context["results"] = results
        context["patient_profile"] = PatientProfile.objects.filter(user=self.request.user).first()
        return context
