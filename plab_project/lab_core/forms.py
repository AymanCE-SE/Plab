from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User, PatientProfile


class AccountProfileForm(forms.Form):
    """Edit display name and patient demographics (linked PatientProfile)."""

    full_name = forms.CharField(
        label=_("Full Name"),
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Your full name")},
        ),
    )
    age = forms.IntegerField(
        label=_("Age"),
        min_value=0,
        max_value=150,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": _("Age")}),
    )
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=PatientProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields["full_name"].initial = user.full_name
            profile = PatientProfile.objects.filter(user=user).first()
            if profile:
                self.fields["age"].initial = profile.age
                self.fields["gender"].initial = profile.gender

    def save(self):
        self.user.full_name = self.cleaned_data["full_name"]
        self.user.save(update_fields=["full_name"])
        profile, created = PatientProfile.objects.get_or_create(
            user=self.user,
            defaults={
                "age": self.cleaned_data["age"],
                "gender": self.cleaned_data["gender"],
            },
        )
        if not created:
            profile.age = self.cleaned_data["age"]
            profile.gender = self.cleaned_data["gender"]
            profile.save(update_fields=["age", "gender"])


class PatientSignUpForm(UserCreationForm):
    age = forms.IntegerField(
        label=_("Age"),
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": _("Enter your age")}),
    )
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=PatientProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = User
        fields = ("full_name", "phone_number", "age", "gender", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Enter your full name")}
        )
        self.fields["phone_number"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Enter your phone number")}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Create a password")}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("Confirm your password")}
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            PatientProfile.objects.create(
                user=user,
                age=self.cleaned_data["age"],
                gender=self.cleaned_data["gender"],
            )
        return user
