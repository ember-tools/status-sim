"""Retention of exercises: seven days after the last access, in memory and in Redis."""

import asyncio
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import manager as manager_module
from main import app
from manager import REDIS_KEY_PREFIX, RETENTION_SECONDS, ConnectionManager, manager
from models import LeitstelleData

DAY = 24 * 3600


class Clock:
    """A clock the tests move forward by hand."""

    def __init__(self):
        self.now = 1_000_000.0

    def time(self) -> float:
        return self.now


class FakeRedis:
    """The part of the async Redis client the manager uses, with expiry on the test clock."""

    def __init__(self, clock: Clock):
        self.clock = clock
        self.values: dict[str, str] = {}
        self.expires: dict[str, float] = {}

    def _alive(self, key: str) -> bool:
        if key in self.expires and self.expires[key] <= self.clock.now:
            self.values.pop(key, None)
            self.expires.pop(key, None)
        return key in self.values

    async def get(self, key):
        return self.values[key] if self._alive(key) else None

    async def set(self, key, value, ex=None):
        self.values[key] = value
        self.expires.pop(key, None)
        if ex is not None:
            self.expires[key] = self.clock.now + ex

    async def expire(self, key, seconds):
        if not self._alive(key):
            return False
        self.expires[key] = self.clock.now + seconds
        return True

    async def ttl(self, key):
        if not self._alive(key):
            return -2
        if key not in self.expires:
            return -1
        return int(self.expires[key] - self.clock.now)

    async def delete(self, key):
        self.values.pop(key, None)
        self.expires.pop(key, None)

    async def scan(self, cursor=0, match=None, count=None):
        prefix = (match or "").rstrip("*")
        return 0, [key for key in list(self.values) if key.startswith(prefix) and self._alive(key)]

    async def ping(self):
        return True

    async def aclose(self):
        return None


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr(manager_module.time, "time", clock.time)
    return clock


@pytest.fixture
def redis(clock: Clock) -> FakeRedis:
    return FakeRedis(clock)


@pytest.fixture
def server(redis: FakeRedis):
    """The whole server, persisting to the fake Redis."""
    manager._redis = redis
    yield TestClient(app)
    manager._redis = None


def _exercise(code: str = "ADMIN") -> LeitstelleData:
    return LeitstelleData(name="Test", vehicle_code=f"{code}V", staffelfuehrer_code=f"{code}S")


def _add(target: ConnectionManager, code: str = "ADMIN") -> None:
    ls = _exercise(code)
    target.leitstellen[code] = ls
    target.code_to_admin[ls.vehicle_code] = code
    target.code_to_admin[ls.staffelfuehrer_code] = code


def test_writing_an_exercise_gives_its_key_the_full_retention(clock, redis):
    target = ConnectionManager()
    target._redis = redis
    _add(target)
    asyncio.run(target.persist("ADMIN"))
    assert asyncio.run(redis.ttl(f"{REDIS_KEY_PREFIX}ADMIN")) == RETENTION_SECONDS


def test_an_exercise_is_deleted_seven_days_after_the_last_access(clock, redis):
    target = ConnectionManager()
    target._redis = redis
    _add(target)
    asyncio.run(target.persist("ADMIN"))
    clock.now += RETENTION_SECONDS - 1
    asyncio.run(target.expire_stale())
    assert "ADMIN" in target.leitstellen
    clock.now += 1
    asyncio.run(target.expire_stale())
    assert target.leitstellen == {}
    assert target.code_to_admin == {}
    assert target.last_access == {}
    assert target.resolve_admin_code("ADMINV") is None
    assert redis.values == {}


def test_any_access_renews_the_retention(clock, redis):
    target = ConnectionManager()
    target._redis = redis
    _add(target)
    asyncio.run(target.persist("ADMIN"))
    clock.now += 6 * DAY
    asyncio.run(target.touch("ADMIN"))
    assert asyncio.run(redis.ttl(f"{REDIS_KEY_PREFIX}ADMIN")) == RETENTION_SECONDS
    clock.now += 6 * DAY
    asyncio.run(target.expire_stale())
    assert "ADMIN" in target.leitstellen


def test_without_redis_the_exercise_still_expires_from_memory(clock):
    target = ConnectionManager()
    _add(target)
    asyncio.run(target.touch("ADMIN"))
    clock.now += RETENTION_SECONDS
    asyncio.run(target.expire_stale())
    assert target.leitstellen == {}


def test_restoring_keeps_the_remaining_lifetime(clock, redis):
    asyncio.run(redis.set(f"{REDIS_KEY_PREFIX}OLD", _exercise("OLD").model_dump_json(), ex=DAY))
    asyncio.run(redis.set(f"{REDIS_KEY_PREFIX}LEGACY", _exercise("LEGACY").model_dump_json()))
    target = ConnectionManager()
    target._redis = redis
    asyncio.run(target._load_all())
    assert set(target.leitstellen) == {"OLD", "LEGACY"}
    assert asyncio.run(redis.ttl(f"{REDIS_KEY_PREFIX}LEGACY")) == RETENTION_SECONDS
    clock.now += DAY
    asyncio.run(target.expire_stale())
    assert set(target.leitstellen) == {"LEGACY"}
    assert target.resolve_admin_code("OLDV") is None


def test_reading_through_the_api_renews_the_retention(clock, redis, server):
    codes = server.post("/api/leitstelle", json={"name": "Read"}).json()
    key = f"{REDIS_KEY_PREFIX}{codes['admin_code']}"
    reads = (
        f"/api/poll/{codes['vehicle_code']}?name=LHF",
        f"/api/leitstelle_info/{codes['admin_code']}",
        f"/api/staffelfuehrer_info/{codes['staffelfuehrer_code']}",
        f"/api/leitstelle/{codes['admin_code']}/scenarios",
        f"/api/join/{codes['vehicle_code']}?name=x",
        f"/leitstelle/{codes['admin_code']}",
    )
    for path in reads:
        clock.now += DAY
        server.get(path, follow_redirects=False)
        assert asyncio.run(redis.ttl(key)) == RETENTION_SECONDS, path
        assert manager.last_access[codes["admin_code"]] == clock.now, path


def test_an_expired_exercise_is_gone_for_every_code(clock, redis, server):
    codes = server.post("/api/leitstelle", json={"name": "Gone"}).json()
    clock.now += RETENTION_SECONDS
    asyncio.run(manager.expire_stale())
    assert server.get(f"/api/poll/{codes['vehicle_code']}").json()["status"] == "error"
    assert server.get(f"/api/join/{codes['staffelfuehrer_code']}").json()["status"] == "error"
    assert server.get(f"/leitstelle/{codes['admin_code']}", follow_redirects=False).status_code == 307


def test_dropping_stale_connections_is_no_access(clock, redis):
    target = ConnectionManager()
    target._redis = redis
    _add(target)
    asyncio.run(target.persist("ADMIN"))
    target.leitstellen["ADMIN"].connections.append(
        manager_module.Connection(name="Car1", last_update=clock.now, last_status_update=clock.now, last_activity=clock.now)
    )
    clock.now += 2 * DAY
    asyncio.run(target.cleanup_inactive())
    assert target.leitstellen["ADMIN"].connections == []
    assert target.last_access["ADMIN"] == clock.now - 2 * DAY
    assert asyncio.run(redis.ttl(f"{REDIS_KEY_PREFIX}ADMIN")) == RETENTION_SECONDS - 2 * DAY
    clock.now += RETENTION_SECONDS - 2 * DAY
    asyncio.run(target.expire_stale())
    assert target.leitstellen == {}


def test_an_access_writes_back_an_exercise_whose_key_is_gone(clock, redis):
    target = ConnectionManager()
    target._redis = redis
    _add(target)
    asyncio.run(target.touch("ADMIN"))
    assert asyncio.run(redis.ttl(f"{REDIS_KEY_PREFIX}ADMIN")) == RETENTION_SECONDS
    assert LeitstelleData.model_validate_json(redis.values[f"{REDIS_KEY_PREFIX}ADMIN"]).name == "Test"
