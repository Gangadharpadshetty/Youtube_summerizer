from threading import Lock

_user_video_map = {}
_lock = Lock()


def set_active_video(telegram_id: str, video_id: str):
    with _lock:
        _user_video_map[telegram_id] = video_id


def get_active_video(telegram_id: str):
    with _lock:
        return _user_video_map.get(telegram_id)