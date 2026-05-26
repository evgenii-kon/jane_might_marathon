"""
Тесты утилит: JWT, datetime_utils.
Эти тесты не требуют базы данных — чисто юнит-тесты.
"""

import pytest
from datetime import timedelta, datetime, timezone

from app.utils.jwt import create_access_token, decode_token, verify_token
from app.utils.datetime_utils import utcnow_naive


# ---------------------------------------------------------------------------
# TestJWT
# ---------------------------------------------------------------------------

class TestJWT:

    def test_create_access_token_returns_string(self):
        token = create_access_token({"sub": "user_id:1"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_access_token_with_expires_delta(self):
        token = create_access_token(
            {"sub": "user_id:2"},
            expires_delta=timedelta(minutes=30),
        )
        assert isinstance(token, str)

    def test_decode_token_valid(self):
        data = {"sub": "user_id:3", "extra": "value"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user_id:3"
        assert payload["extra"] == "value"

    def test_decode_token_invalid_returns_none(self):
        result = decode_token("this.is.not.a.valid.jwt")
        assert result is None

    def test_decode_token_empty_string(self):
        result = decode_token("")
        assert result is None

    def test_decode_token_tampered(self):
        token = create_access_token({"sub": "user_id:4"})
        tampered = token[:-5] + "XXXXX"
        result = decode_token(tampered)
        assert result is None

    def test_decode_token_contains_exp(self):
        token = create_access_token({"sub": "user_id:5"})
        payload = decode_token(token)
        assert "exp" in payload

    def test_verify_token_valid(self):
        token = create_access_token({"sub": "user_id:6"})
        payload = verify_token(token)
        assert payload["sub"] == "user_id:6"

    def test_verify_token_invalid_raises_http_exception(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_create_token_short_expiry(self):
        """Создаём токен с очень коротким временем жизни."""
        token = create_access_token(
            {"sub": "user_id:7"},
            expires_delta=timedelta(seconds=1),
        )
        # Сразу же декодируем — должен быть валидным
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user_id:7"

    def test_multiple_tokens_are_different(self):
        """Два токена для разных payload должны отличаться."""
        t1 = create_access_token({"sub": "user1"})
        t2 = create_access_token({"sub": "user2"})
        assert t1 != t2

    def test_token_payload_preserved(self):
        """Все поля payload сохраняются в токене."""
        data = {"sub": "user_id:8", "role": "admin", "name": "Test"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload["sub"] == "user_id:8"
        assert payload["role"] == "admin"
        assert payload["name"] == "Test"


# ---------------------------------------------------------------------------
# TestDatetimeUtils
# ---------------------------------------------------------------------------

class TestDatetimeUtils:

    def test_utcnow_naive_returns_datetime(self):
        result = utcnow_naive()
        assert isinstance(result, datetime)

    def test_utcnow_naive_has_no_timezone(self):
        """Результат должен быть offset-naive (без tzinfo)."""
        result = utcnow_naive()
        assert result.tzinfo is None

    def test_utcnow_naive_is_recent(self):
        """Время должно быть близко к текущему UTC."""
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        result = utcnow_naive()
        after = datetime.now(timezone.utc).replace(tzinfo=None)
        assert before <= result <= after

    def test_utcnow_naive_two_calls_are_sequential(self):
        """Второй вызов возвращает время >= первого."""
        t1 = utcnow_naive()
        t2 = utcnow_naive()
        assert t2 >= t1


# ---------------------------------------------------------------------------
# TestMasteryIntervals — тест константы в репозитории
# ---------------------------------------------------------------------------

class TestMasteryIntervals:
    """
    Проверяем, что константа MASTERY_INTERVALS в UserWordProgressRepository
    корректна (6 уровней, интервалы возрастают).
    """

    def test_intervals_exist_for_all_levels(self):
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        intervals = UserWordProgressRepository.MASTERY_INTERVALS
        for level in range(6):  # 0..5
            assert level in intervals

    def test_intervals_are_positive(self):
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        intervals = UserWordProgressRepository.MASTERY_INTERVALS
        for level, days in intervals.items():
            assert days > 0, f"Interval for level {level} must be positive"

    def test_intervals_increase_with_level(self):
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        intervals = UserWordProgressRepository.MASTERY_INTERVALS
        previous = 0
        for level in sorted(intervals.keys()):
            assert intervals[level] >= previous
            previous = intervals[level]
