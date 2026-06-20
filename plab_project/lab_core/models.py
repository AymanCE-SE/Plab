from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import date
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

class UserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            phone_number=phone_number,
            full_name=full_name,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(_("Full name"), max_length=255)
    phone_number = models.CharField(_("Phone number"), max_length=20, unique=True)
    date_joined = models.DateTimeField(_("Date joined"), default=timezone.now)

    is_active = models.BooleanField(_("Active"), default=True)
    is_staff = models.BooleanField(_("Staff status"), default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"


class PatientProfile(models.Model):
    GENDER_CHOICES = (
        ("male", _("Male")),
        ("female", _("Female")),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        verbose_name=_("User"),
    )
    age = models.PositiveIntegerField(_("Age"))
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER_CHOICES)

    class Meta:
        verbose_name = _("Patient profile")
        verbose_name_plural = _("Patient profiles")

    def __str__(self):
        return f"PatientProfile - {self.user.full_name}"


def lab_result_upload_path(instance, filename):
    """Store files in results/YYYY/MM/DD/filename."""
    return f"results/{timezone.now():%Y/%m/%d}/{filename}"


class LabResult(models.Model):
    STATUS_CHOICES = (
        ("PENDING", _("Under Processing")),
        ("REVIEW", _("Under Review")),
        ("COMPLETED", _("Ready for Download")),
    )

    CATEGORY_CHOICES = (
        ("blood", _("Blood")),
        ("urine", _("Urine")),
        ("stool", _("Stool")),
        ("others", _("Others")),
    )

    # The patient account this lab result belongs to.
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lab_results",
        verbose_name=_("Patient"),
    )
    test_name = models.CharField(_("Test name"), max_length=255)
    category = models.CharField(_("Category"), max_length=20, choices=CATEGORY_CHOICES)
    recorded_date = models.DateField(_("Recorded date"), default=date.today)
    # Upload PDF files to a date-based folder path.
    pdf_result = models.FileField(_("PDF result"), upload_to=lab_result_upload_path)
    # Controls whether the result is visible to the patient.
    is_published = models.BooleanField(_("Publish status"), default=False)
    # Patient-visible progress status (used when is_published=False).
    status = models.CharField(
        _("Status"),
        max_length=15,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    # Optional schedule to help patients know when to check back.
    expected_delivery = models.DateTimeField(_("Expected delivery"), blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created at"), default=timezone.now, editable=False)

    class Meta:
        verbose_name = _("Test result")
        verbose_name_plural = _("Test results")
        ordering = ["-created_at", "-recorded_date", "-id"]

    def __str__(self):
        return f"{self.test_name} - {self.patient.phone_number}"


def blog_image_upload_path(instance, filename):
    """Store blog images in health_blog/YYYY/MM/DD/filename."""
    return f"health_blog/{timezone.now():%Y/%m/%d}/{filename}"


class BlogPost(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(unique=True, allow_unicode=True)
    description = models.TextField(_("Description"), blank=True)
    content = models.TextField(_("Content"))
    # Pinned posts appear first on the health blog for visibility.
    is_pinned = models.BooleanField(_("Pinned"), default=False)
    image = models.ImageField(_("Image"), upload_to=blog_image_upload_path, blank=True, null=True)
    posted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
        limit_choices_to={"is_staff": True},
        verbose_name=_("Posted by"),
    )
    hearts = models.ManyToManyField(User, related_name="hearted_posts", blank=True, verbose_name=_("Hearts"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    def get_absolute_url(self):
        return reverse("lab_core:post_detail", kwargs={"slug": self.slug})
    
    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def hearts_count(self):
        return self.hearts.count()


class LabAnnouncement(models.Model):
    """Short-lived lab notices shown to patients (hours, closures, new services)."""

    title = models.CharField(_("Title"), max_length=200, blank=True)
    body = models.TextField(_("Body"))
    link_label = models.CharField(_("Link label"), max_length=100, blank=True)
    link_url = models.URLField(_("Link URL"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    # Higher numbers show first when multiple announcements are active.
    priority = models.PositiveSmallIntegerField(_("Priority"), default=0)
    expires_at = models.DateTimeField(_("Expires at"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Lab announcement")
        verbose_name_plural = _("Lab announcements")
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return self.title or (self.body[:50] + "…" if len(self.body) > 50 else self.body)