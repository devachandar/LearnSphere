import redis
from django.conf import settings

_client = None
COURSE_TTL_SECONDS = 300


def _get_client():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.REDIS_URL)
    return _client


def get_cached_course(course_id):
    try:
        cached = _get_client().get(f"course:{course_id}")
        import json

        return json.loads(cached) if cached else None
    except redis.RedisError:
        return None


def set_cached_course(course_id, data):
    try:
        import json

        _get_client().set(f"course:{course_id}", json.dumps(data, default=str), ex=COURSE_TTL_SECONDS)
    except redis.RedisError:
        pass


def invalidate_course_cache(course_id):
    try:
        _get_client().delete(f"course:{course_id}")
    except redis.RedisError:
        pass
