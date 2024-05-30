from django.core.cache import cache


def store_token(user_id, token):
    try:
        timeout = 60 * 59  # seconds
        key = f"session:{user_id}"
        cache.set(key=key, value=token, timeout=timeout)
        return True
    except Exception:
        raise Exception
        return False


def get_token(user_id):
    key = f"session:{user_id}"
    return cache.get(key=key)
