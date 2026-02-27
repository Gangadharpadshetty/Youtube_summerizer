import pytest
from threading import Thread
from collections import Counter

# ── module under test (inline) ─────────────────────────────────────────────────
from threading import Lock

_user_video_map = {}
_lock = Lock()


def set_active_video(telegram_id: str, video_id: str):
    with _lock:
        _user_video_map[telegram_id] = video_id


def get_active_video(telegram_id: str):
    with _lock:
        return _user_video_map.get(telegram_id)


# ── fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_map():
    """Reset shared state before every test to avoid cross-test pollution."""
    _user_video_map.clear()
    yield
    _user_video_map.clear()


# ── basic set & get ────────────────────────────────────────────────────────────

class TestSetAndGet:

    def test_set_then_get_returns_video_id(self):
        set_active_video("user_1", "vid_abc")
        assert get_active_video("user_1") == "vid_abc"

    def test_get_unknown_user_returns_none(self):
        assert get_active_video("ghost_user") is None

    def test_set_overwrites_existing_video(self):
        set_active_video("user_1", "vid_old")
        set_active_video("user_1", "vid_new")
        assert get_active_video("user_1") == "vid_new"

    def test_multiple_users_are_independent(self):
        set_active_video("user_1", "vid_A")
        set_active_video("user_2", "vid_B")
        assert get_active_video("user_1") == "vid_A"
        assert get_active_video("user_2") == "vid_B"

    def test_set_empty_string_video_id(self):
        set_active_video("user_1", "")
        assert get_active_video("user_1") == ""

    def test_set_empty_string_telegram_id(self):
        set_active_video("", "vid_abc")
        assert get_active_video("") == "vid_abc"

    def test_get_does_not_mutate_map(self):
        set_active_video("user_1", "vid_abc")
        get_active_video("user_1")
        get_active_video("user_1")
        assert get_active_video("user_1") == "vid_abc"


# ── state isolation ────────────────────────────────────────────────────────────

class TestStateIsolation:

    def test_map_starts_empty(self):
        # autouse fixture clears the map — should always be empty here
        assert get_active_video("any_user") is None

    def test_one_user_does_not_affect_another(self):
        set_active_video("user_A", "vid_1")
        assert get_active_video("user_B") is None

    def test_multiple_sets_same_user_keeps_last(self):
        for i in range(10):
            set_active_video("user_1", f"vid_{i}")
        assert get_active_video("user_1") == "vid_9"


# ── concurrency ────────────────────────────────────────────────────────────────

class TestConcurrency:

    def test_concurrent_writes_do_not_raise(self):
        """Multiple threads writing simultaneously should not raise or corrupt state."""
        errors = []

        def writer(tid, vid):
            try:
                set_active_video(tid, vid)
            except Exception as e:
                errors.append(e)

        threads = [Thread(target=writer, args=(f"user_{i}", f"vid_{i}")) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Exceptions raised during concurrent writes: {errors}"

    def test_concurrent_reads_do_not_raise(self):
        """Multiple threads reading simultaneously should not raise."""
        set_active_video("shared_user", "shared_vid")
        errors = []

        def reader():
            try:
                get_active_video("shared_user")
            except Exception as e:
                errors.append(e)

        threads = [Thread(target=reader) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Exceptions raised during concurrent reads: {errors}"

    def test_concurrent_writes_each_user_gets_own_video(self):
        """Each user's final value should match what was written for them."""
        def writer(i):
            set_active_video(f"user_{i}", f"vid_{i}")

        threads = [Thread(target=writer, args=(i,)) for i in range(30)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        for i in range(30):
            assert get_active_video(f"user_{i}") == f"vid_{i}"== f"vid_{i}"