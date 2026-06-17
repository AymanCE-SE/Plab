from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import User, PatientProfile, LabResult, BlogPost, LabAnnouncement

admin.site.site_header = _("PLAB Laboratory Management")
admin.site.site_title = _("PLAB Admin Portal")
admin.site.index_title = _("Welcome to the PLAB administration dashboard")


class LabResultInline(admin.TabularInline):
    """All lab tests for this user (patient); FK on LabResult is `patient`."""

    model = LabResult
    fk_name = "patient"
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name_plural = _("Lab tests")
    fields = (
        "test_name",
        "category",
        "status",
        "recorded_date",
        "is_published",
        "created_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number", "full_name", "total_tests", "is_staff", "is_active", "date_joined")
    ordering = ("phone_number",)
    search_fields = ("phone_number", "full_name")
    list_filter = ("date_joined", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal information"), {"fields": ("full_name",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "full_name", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_lab_tests=Count("lab_results"))

    @admin.display(ordering="total_lab_tests", description=_("Total tests"))
    def total_tests(self, obj):
        return obj.total_lab_tests

    inlines = (LabResultInline,)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "gender")
    search_fields = ("user__phone_number", "user__full_name")
    readonly_fields = ("lab_tests_for_patient",)
    fieldsets = (
        (None, {"fields": ("user", "age", "gender")}),
        (_("Lab tests"), {"fields": ("lab_tests_for_patient",)}),
    )

    @admin.display(description=_("All tests for this patient"))
    def lab_tests_for_patient(self, obj):
        if obj is None:
            return format_html(
                '<p class="help" style="margin:0;">{}</p>',
                _("Save the profile first to see lab tests linked to this account."),
            )
        qs = (
            obj.user.lab_results.all()
            .order_by("-created_at", "-recorded_date", "-id")
        )
        if not qs.exists():
            return format_html(
                '<p class="help" style="margin:0;">{}</p>',
                _("No lab tests recorded for this patient yet."),
            )
        head = format_html(
            "<table class=\"listing\">"
            "<thead><tr>"
            "<th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th>"
            "</tr></thead><tbody>",
            _("Test name"),
            _("Category"),
            _("Status"),
            _("Recorded date"),
            _("Publish status"),
            _("Created at"),
        )
        rows = []
        url_name = "admin:lab_core_labresult_change"
        for r in qs:
            url = reverse(url_name, args=[r.pk])
            pub = _("Published") if r.is_published else _("Not published")
            rows.append(
                format_html(
                    "<tr>"
                    "<th scope=\"row\"><a href=\"{}\">{}</a></th>"
                    "<td>{}</td>"
                    "<td>{}</td>"
                    "<td>{}</td>"
                    "<td>{}</td>"
                    "<td>{}</td>"
                    "</tr>",
                    url,
                    escape(r.test_name),
                    r.get_category_display(),
                    r.get_status_display(),
                    r.recorded_date.isoformat() if r.recorded_date else "—",
                    pub,
                    r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "—",
                )
            )
        return mark_safe("".join([str(head)] + [str(row) for row in rows] + ["</tbody></table>"]))


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "test_name",
        "status",
        "created_at",
        "is_published",
    )
    list_editable = ("status", "is_published")
    search_fields = ("patient__phone_number", "patient__full_name", "test_name")
    list_filter = ("status", "is_published")
    autocomplete_fields = ("patient",)
    readonly_fields = ("created_at",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_pinned", "posted_by", "hearts_count", "created_at")
    search_fields = ("title", "description", "content", "posted_by__full_name", "posted_by__phone_number")
    list_filter = ("is_pinned", "created_at")
    list_editable = ("is_pinned",)
    autocomplete_fields = ("posted_by",)
    prepopulated_fields = {'slug': ('title',)}
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_hearts=Count("hearts"))

    @admin.display(ordering="total_hearts", description=_("Hearts"))
    def hearts_count(self, obj):
        return obj.total_hearts


@admin.register(LabAnnouncement)
class LabAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "priority", "expires_at", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "body")
    list_editable = ("is_active", "priority")
