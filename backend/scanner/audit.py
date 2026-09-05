from .models import AuditLog


def record_audit(request, inspection, action, description, metadata=None, previous_value="", new_value=""):
    return AuditLog.objects.create(
        inspection=inspection,
        user=request.user,
        action=action,
        description=description,
        metadata=metadata or {},
        previous_value=previous_value,
        new_value=new_value,
        ip_address=request.META.get("REMOTE_ADDR"),
    )
