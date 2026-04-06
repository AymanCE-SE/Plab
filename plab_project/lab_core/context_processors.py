from django.db.models import Q
from django.utils import timezone

from .models import LabAnnouncement


def lab_announcements(request):
    """Expose active lab announcements to all templates (user-friendly notices)."""
    now = timezone.now()
    announcements = (
        LabAnnouncement.objects.filter(is_active=True)
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        .order_by("-priority", "-created_at")[:5]
    )
    return {"lab_announcements": announcements}
