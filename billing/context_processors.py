from .services import get_wallet


def wallet(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}
    return {"wallet": get_wallet(user)}
